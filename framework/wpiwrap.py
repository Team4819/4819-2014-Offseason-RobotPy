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

class Refrence:

    name = ""
    portrefs = dioRefs
    wpi_object_name = "DigitalInput"

    def __init__(self, name, modulename, port):
        self.name = name
        self.modulename = modulename
        self.port = port
        if name in refrences:
            if refrences[name].__class__.__name__ == self.wpi_object_name and refrences[name].port == self.port:
                self.wpiobject = refrences[name].wpiobject
            else:
                raise Exception("Create Refrence error: refrence already registered under the name " + name)
        elif port in self.portrefs:
            if self.portrefs[port].__class__.__name__ == self.wpi_object_name:
                self.wpiobject = self.portrefs[port]
            else:
                raise Exception("Create Refrence error: port " + str(port) + " already used with another type of refrence.")
        else:
            self.init_wpilib_refrence(name, port)
        self.portrefs[port] = self.wpiobject
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

    wpi_object_name = "DigitalInput"
    portrefs = dioRefs

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.DigitalInput(port)
        self.wpiobject.label = name

    def get(self):
        return self.wpiobject.Get()

    def publish_to_table(self):
        wpilib.SmartDashboard.PutBoolean(self.name, self.get())


class AnalogInput(Refrence):

    wpi_object_name = "AnalogChannel"
    portrefs = analogRefs

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.AnalogChannel(port)
        self.wpiobject.label = name

    def get(self):
        return self.wpiobject.GetVoltage()

    def publish_to_table(self):
        wpilib.SmartDashboard.PutNumber(self.name, self.get())


class DigitalOutput(Refrence):

    wpi_object_name = "DigitalOutput"
    portrefs = dioRefs

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
    wpi_object_name = "Counter"
    portrefs = dioRefs

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Counter()
        self.wpiobject.SetUpSource(port)
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
    portrefs = pwmRefs
    wpi_object_name = "Talon"

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
    portrefs = solenoidRefs
    wpi_object_name = "Solenoid"

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
    portrefs = analogRefs
    wpi_object_name = "Gyro"
    error = False
    last_read_time = 0
    last_read_val = 0
    reseting = False

    def __init__(self, name, modulename, port, max_rate):
        Refrence.__init__(self, name, modulename, port)
        self.max_rate = max_rate

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Gyro(port)
        self.wpiobject.label = name

    def get(self):
        angle = self.wpiobject.GetAngle()
        current_time = time.time()

        if self.reseting:
            self.reseting = abs(angle) > 1
            angle = 0

        if self.last_read_time is not 0 and not self.error and not self.reseting:
            rate = (angle - self.last_read_val)/(current_time - self.last_read_time)
            if abs(rate) > self.max_rate:
                self.error = True
                raise DeviceInErrorStateError("value: {}, last_value: {}, time: {}, last_time: {}".format(angle, self.last_read_val, current_time, self.last_read_time))
        self.last_read_time = current_time
        self.last_read_val = angle
        if self.error:
            raise DeviceInErrorStateError()
        return angle

    def reset(self):
        return self.wpiobject.Reset()
        self.reseting = True

    def publish_to_table(self):
        if not self.error:
            wpilib.SmartDashboard.PutNumber(self.name, self.get())
        else:
            wpilib.SmartDashboard.PutNumber(self.name, 0)


class Compressor(Refrence):

    def __init__(self, name, modulename, switchport, relayport):
        self.name = name
        self.modulename = modulename
        self.relayport = relayport
        self.switchport = switchport
        self.wpiobject = None

        if name in refrences:
            raise Exception("Create Refrence error: refrence already registered under the name " + name)

        if switchport in dioRefs:
            if dioRefs[switchport].__class__.__name__ == "Compressor":
                self.wpiobject = dioRefs[switchport]
            else:
                Exception("Create Refrence error: port " + str(switchport) + " already used with another type of refrence.")

        if relayport in relayRefs:
            if relayRefs[relayport].__class__.__name__ == "Compressor":
                self.wpiobject = relayRefs[relayport]
            else:
                Exception("Create Refrence error: port " + str(relayport) + " already used with another type of refrence.")

        if self.wpiobject is None:
            self.init_wpilib_refrence(name, switchport, relayport)

        relayRefs[relayport] = self.wpiobject
        dioRefs[switchport] = self.wpiobject
        refrences[name] = self

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

    last_value = 0
    last_time = 0
    error = False
    reseting = False

    def __init__(self, name, modulename, A_port, B_port, tics_per_foot, max_rate):
        self.name = name
        self.modulename = modulename
        self.A_port = A_port
        self.B_port = B_port
        self.tics_per_foot = float(tics_per_foot)
        self.max_rate = max_rate
        self.wpiobject = None

        if name in refrences:
            if refrences[name].__class__.__name__ == self.wpi_object_name and refrences[name].A_port == self.A_port and refrences[name].B_port == self.B_port:
                self.wpiobject = refrences[name].wpiobject
            else:
                raise Exception("Create Refrence error: refrence already registered under the name " + name)

        if A_port in dioRefs:
            if dioRefs[A_port].__class__.__name__ == "Encoder":
                self.wpiobject = dioRefs[A_port]
            else:
                Exception("Create Refrence error: port " + str(A_port) + " already used with another type of refrence.")

        if B_port in dioRefs:
            if dioRefs[B_port].__class__.__name__ == "Encoder":
                self.wpiobject = dioRefs[B_port]
            else:
                Exception("Create Refrence error: port " + str(A_port) + " already used with another type of refrence.")

        if self.wpiobject is None:
            self.init_wpilib_refrence(name, A_port, B_port)

        dioRefs[A_port] = self.wpiobject
        dioRefs[B_port] = self.wpiobject
        refrences[name] = self

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
        current_time = time.time()
        if self.reseting:
            self.reseting = abs(feet) > .5
            feet = 0

        if self.last_time is not 0 and not self.error and not self.reseting:
            rate = (feet - self.last_value)/(current_time - self.last_time)
            if abs(rate) > self.max_rate:
                self.error = True
                raise DeviceInErrorStateError("value: {}, last_value: {}, time: {}, last_time: {}".format(feet, self.last_value, current_time, self.last_time))

        self.last_time = current_time
        self.last_value = feet

        if self.error:
            raise DeviceInErrorStateError()

        return feet

    def get_rate(self):
        value = self.wpiobject.GetRate()/self.tics_per_foot
        if value is None:
            value = 0
        if self.error:
            raise DeviceInErrorStateError()
        return value

    def reset(self):
        self.wpiobject.Reset()
        self.reseting = True

    def publish_to_table(self):
        if not self.error:
            wpilib.SmartDashboard.PutNumber(self.name, self.get())
        else:
            wpilib.SmartDashboard.PutNumber(self.name, 0)