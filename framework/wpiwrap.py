__author__ = 'christian'
import time
import logging
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

refrences = dict()
dioRefs = dict()
analogRefs = dict()
pwmRefs = dict()
solenoidRefs = dict()
relayRefs = dict()


def clear_refrences(mod):
    reflist = list()
    for ref in refrences:
        if refrences[ref].modulename is mod:
            reflist.append(ref)

    for ref in reflist:
        refrences[ref].neuteralize()
        del(refrences[ref])


def publish_values():
    for ref in refrences:
        refrences[ref].publish_to_table()

class DeviceInErrorStateError(Exception):
    pass

class DeviceWatchdog():
    max_rate = 0
    last_value = 0
    last_time = 0
    last_time_changed = 0
    reset_at = 0
    reset_grace = 1

    def __init__(self, max_rate):
        self.max_rate = max_rate
        self.reset()

    def sniff(self, value):
        current_time = time.time()
        status = True
        message = ""
        if value != self.last_value:
            time_delta = current_time - self.last_time_changed
            rate = (value - self.last_value)/time_delta
            status = rate <= self.max_rate
            if not status:
                message = "rate exceeded max rate! the rate was {}, and the other values were: max_rate: {}, value: {}, last_value: {}, time_delta: {}".format(rate, self.max_rate, value, self.last_value, time_delta)
            self.last_time_changed = current_time
            self.last_value = value
        if abs(current_time - self.reset_at) < self.reset_grace:
            status = True
        return message, status

    def reset(self):
        self.reset_at = time.time()

class Refrence:

    name = ""
    portrefs = [dioRefs]
    wpi_object_name = wpilib.DigitalInput.__name__
    status = True
    statmsg = ""

    def __init__(self, name, modulename, port):
        self.name = name
        self.modulename = modulename
        self.get_wpiobject(name, port)

    def get_wpiobject(self, name, *ports):
        self.ports = ports
        self.wpiobject = None

        if name in refrences:
            if refrences[name].__class__.__name__ == self.__class__.__name__ and refrences[name].ports == self.ports:
                self.wpiobject = refrences[name].wpiobject
            else:
                raise Exception("Create Refrence error: refrence already registered under the name " + name)

        for port, refs in zip(ports, self.portrefs):
            if port in refs:
                if refs[port].__class__.__name__ == self.wpi_object_name:
                    self.wpiobject = refs[port]
                else:
                    raise Exception("Create Refrence error: port " + str(port) + " already in use with another type of refrence, " + refs[port].__class__.__name__)

        if self.wpiobject is None:
            self.init_wpilib_refrence(name, *ports)

        for port, refs in zip(ports, self.portrefs):
            refs[port] = self.wpiobject

        refrences[name] = self

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = None

    def get(self):
        return 0

    def set(self, value):
        pass

    def neuteralize(self):
        self.set(0)

    def dumpValues(self):
        return str(self.get())

    def publish_to_table(self):
        wpilib.SmartDashboard.PutString(self.name, self.dumpValues())

    def __getattr__(self, item):
        return getattr(self.wpiobject, item)


class DigitalInput(Refrence):

    wpi_object_name = wpilib.DigitalInput.__name__
    portrefs = [dioRefs]

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.DigitalInput(port)
        self.wpiobject.label = name

    def get(self):
        return self.wpiobject.Get()

    def publish_to_table(self):
        wpilib.SmartDashboard.PutBoolean(self.name, self.get())


class AnalogInput(Refrence):

    wpi_object_name = wpilib.AnalogChannel.__name__
    portrefs = [analogRefs]

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.AnalogChannel(port)
        self.wpiobject.label = name

    def get(self):
        return self.wpiobject.GetVoltage()

    def publish_to_table(self):
        wpilib.SmartDashboard.PutNumber(self.name, self.get())


class DigitalOutput(Refrence):

    wpi_object_name = wpilib.DigitalOutput.__name__
    portrefs = [dioRefs]

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.DigitalOutput(port)
        self.wpiobject.label = name

    def set(self, value):
        return self.wpiobject.Set(value)

    def neuteralize(self):
        self.set(False)

    def publish_to_table(self):
        wpilib.SmartDashboard.PutBoolean(self.name, self.wpiobject.Get())


class Counter(Refrence):
    wpi_object_name = wpilib.Counter.__name__
    portrefs = [dioRefs]

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Counter()
        self.wpiobject.SetUpSource(port)
        self.wpiobject.Start()
        self.wpiobject.label = name

    def get(self):
        return self.wpiobject.Get()

    def reset(self):
        return self.wpiobject.Reset()

    def start(self):
        return self.wpiobject.Start()

    def publish_to_table(self):
        wpilib.SmartDashboard.PutNumber(self.name, self.get())



class Talon(Refrence):
    portrefs = [pwmRefs]
    wpi_object_name = wpilib.Talon.__name__

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Talon(port)
        self.wpiobject.label = name

    def get(self):
        return self.wpiobject.Get()

    def set(self, value):
        self.wpiobject.Set(value)

    def publish_to_table(self):
        wpilib.SmartDashboard.PutNumber(self.name, self.get())


class Solenoid(Refrence):
    portrefs = [solenoidRefs]
    wpi_object_name = wpilib.Solenoid.__name__

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Solenoid(port)
        self.wpiobject.label = name

    def set(self, value):
        self.wpiobject.Set(value)

    def neuteralize(self):
        self.set(False)

    def publish_to_table(self):
        wpilib.SmartDashboard.PutBoolean(self.name, self.wpiobject.Get())

class Gyro(Refrence):
    portrefs = [analogRefs]
    wpi_object_name = wpilib.Gyro.__name__
    last_read_time = 0
    last_read_val = 0

    def __init__(self, name, modulename, port, max_rate):
        self.name = name
        self.modulename = modulename
        self.dog = DeviceWatchdog(max_rate)
        self.get_wpiobject(name, port)

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Gyro(port)
        self.wpiobject.label = name

    def get(self):
        angle = self.wpiobject.GetAngle()
        self.statmsg, self.status = self.dog.sniff(angle)

        if not self.status:
            raise DeviceInErrorStateError(self.statmsg)
        else:
            return angle

    def reset(self):
        self.dog.reset()
        return self.wpiobject.Reset()

    def publish_to_table(self):
        if self.status:
            wpilib.SmartDashboard.PutNumber(self.name, self.get())
        else:
            wpilib.SmartDashboard.PutNumber(self.name, 0)


class Compressor(Refrence):

    wpi_object_name = wpilib.Compressor.__name__
    portrefs = [dioRefs, relayRefs]

    def __init__(self, name, modulename, switchport, relayport):
        self.name = name
        self.modulename = modulename
        self.get_wpiobject(name, switchport, relayport)

    def init_wpilib_refrence(self, name, switch, relay):
        self.wpiobject = wpilib.Compressor(switch, relay)
        self.wpiobject.label = name

    def set(self, value):
        if value:
            self.wpiobject.Start()
        else:
            self.wpiobject.Stop()

    def neuteralize(self):
        self.set(False)

    def publish_to_table(self):
        wpilib.SmartDashboard.PutBoolean(self.name, self.wpiobject.GetPressureSwitchValue())


class Encoder(Refrence):

    portrefs = [dioRefs, dioRefs]
    wpi_object_name = wpilib.Encoder.__name__

    def __init__(self, name, modulename, A_port, B_port, tics_per_foot, max_rate):
        self.name = name
        self.modulename = modulename
        self.tics_per_foot = tics_per_foot
        self.dog = DeviceWatchdog(max_rate)
        self.get_wpiobject(name, A_port, B_port)


    def init_wpilib_refrence(self, name, A_port, B_port):
        self.wpiobject = wpilib.Encoder(A_port, B_port)
        self.wpiobject.Start()
        self.wpiobject.Reset()
        self.wpiobject.label = name

    def get(self):
        value = self.wpiobject.Get()
        if value is None:
            value = 0
        feet = float(value/self.tics_per_foot)
        self.statmsg, self.status = self.dog.sniff(feet)

        if not self.status:
            raise DeviceInErrorStateError(self.statmsg)
        else:
            return feet

    def get_rate(self):
        value = self.wpiobject.GetRate()/self.tics_per_foot
        if value is None:
            value = 0
        if not self.status:
            raise DeviceInErrorStateError(self.statmsg)
        else:
            return value

    def reset(self):
        self.wpiobject.Reset()
        self.dog.reset()

    def publish_to_table(self):
        if self.status:
            wpilib.SmartDashboard.PutNumber(self.name, self.get())
        else:
            wpilib.SmartDashboard.PutNumber(self.name, 0)