"""
This is a wrapper for wpilib that primarily focuses on allowing multiple modules to have access to the same device refrences.
Whenever a device refrence is created, the wpilib refrence is initialized once, then saved to one of the refs dictionaries, when
that device is created again, the already-initialized wpilib refrence will be pulled from the dictionary.
"""
__author__ = 'christian'
import time
import logging
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

#TODO comment all of this stuff

#These are the refrence dictionaries, they cache wpilib refrences so that they can be re-used elsewhere.

#This holds refrences to all objects inheriting from wpiwrap.Refrence, this is the first place
# checked when looking for device refrence dupilcates.
refrences = list()

#The following dictionaries hold refrences to the actual wpilib objects under their appropriate port number, for example: dioRefs[1] refrences
# whatever wpilib object (if any) that is using dio port 1
dioRefs = dict()
analogRefs = dict()
pwmRefs = dict()
solenoidRefs = dict()
relayRefs = dict()
usbRefs = dict()


def clear_refrences(subsystem):
    """This searches through the refrences for anything created by subsystem, neuteralizes their outputs, and removes them"""

    #Neuteralize them
    for ref in refrences[:]:
        ref.neuteralize()
        refrences.remove(ref)


def publish_values():
    """This loops through all refrences and runs their publish_to_table command"""
    for ref in refrences[:]:
        ref.publish_to_table()

class DeviceInErrorStateError(Exception):
    """This is raised when the device is in an error state"""
    pass

class DeviceWatchdog():
    """This can be used to keep tabs on a value and alert when it is misbehaving, ususally by increasing or decreasing too quickly"""

    #The rate of change that the value cannot exceed
    max_rate = 0

    #The last-sniffed value
    last_value = 0

    #When the value was last sniffed
    last_time = 0

    #The last time the value changed between sniffs
    last_time_changed = 0

    #The last time the value was reset
    reset_at = 0

    #How long after a reset to we ignore alerts
    reset_grace = 1

    def __init__(self, max_rate):
        #Save max_rate and reset
        self.max_rate = max_rate
        self.reset()

    def sniff(self, value):
        """
        This accepts a value and checks it for violations. It returns two values: message and status.
        message is the summary of an exception, if any.
        status is a boolean value which turns false if we have a violation
        """

        #Initialize some variables
        current_time = time.time()
        status = True
        message = ""

        #If the value has changed since we last sniffed it, it is worth checking over
        if value != self.last_value:
            #How much time has passed since the last change?
            time_delta = current_time - self.last_time_changed
            #What then is the rate of change of the value?
            rate = (value - self.last_value)/time_delta
            #Set status to false if the rate exceeds the maximum
            status = rate <= self.max_rate

            if not status:
                #Set the message and debug info
                message = "rate exceeded max rate! the rate was {}, and the other values were: max_rate: {}, value: {}, last_value: {}, time_delta: {}".format(rate, self.max_rate, value, self.last_value, time_delta)

            #Save some variables
            self.last_time_changed = current_time
            self.last_value = value

        #If we are within the reset grace period, then set the status to true
        if abs(current_time - self.reset_at) < self.reset_grace:
            status = True

        #Return it! Return it!
        return message, status

    def reset(self):
        """This allows for the value to change significantly without alerting the dog"""
        #Save the current time
        self.reset_at = time.time()


class Refrence:
    """This is used to allow multiple subsystems to have control of the same wpilib device refrence."""

    #The name of the device
    name = ""

    #The port refrence dictionaries to use when caching the wpilib object
    portrefs = [dioRefs]

    #The name of the wpi object
    wpi_object_name = wpilib.DigitalInput.__name__

    #The error status and error message, if there is any
    status = True
    statmsg = ""

    #The subsystem that created this
    subsystem = ""

    def __init__(self, name, subsystem, port):
        self.name = name
        self.subsystem = subsystem
        self.get_wpiobject(name, port)

    def get_wpiobject(self, name, *ports):
        """This function populates our wpiobject with either a cached one, or a brand new one. It also saves the refrence in the port refrences given"""

        #Save some values
        self.ports = ports
        self.wpiobject = None

        #Check that the ports are not used elsewhere. If so, then error if it is the wrong object.
        #Loop through each pair of portref and port
        for port, refs in zip(ports, self.portrefs):
            #If the port is populated
            if port in refs:
                #Does it's name match the object we are looking for?
                if refs[port].__class__.__name__ == self.wpi_object_name:
                    self.wpiobject = refs[port]
                #Else we cannot create another device here, as the port is already used.
                else:
                    raise Exception("Create Refrence error: port " + str(port) + " already in use with another type of refrence, " + refs[port].__class__.__name__)

        #If we still haven't found anything, create one from scratch
        if self.wpiobject is None:
            self.init_wpilib_refrence(name, *ports)

        #Save it to all of the relevant port refs
        for port, refs in zip(ports, self.portrefs):
            refs[port] = self.wpiobject

        #Save self to the refrence list
        refrences.append(self)

    def init_wpilib_refrence(self, name, port):
        """This is meant to be overloaded with something to initialize the correct wpi object"""
        self.wpiobject = None

    def get(self):
        """This is meant to be overloaded with the wpi object's default getter"""
        return 0

    def set(self, value):
        """This is meant to be overloaded with the wpi object's default setter"""
        pass

    def neuteralize(self):
        """This is meant to be overloaded with whatever puts the wpi object into a safe state."""
        self.set(0)

    def dumpValues(self):
        """Dumps the values as a string"""
        return str(self.get())

    def publish_to_table(self):
        """Dumps the values to the smart dashboard"""
        wpilib.SmartDashboard.PutString(self.name, self.dumpValues())

    def __getattr__(self, item):
        """If we haven't heard of a function, forward the request to the wpi object"""
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

    def set_semi_period(self):
        #TODO Remove this try/except once pyfrc is updated with my commit
        try:
            self.wpiobject.SetSemiPeriodMode(True)
        except AttributeError:
            logging.info("My patch must not have fully propogated yet, there is no attribute for Counter.SetSemiPeriodMode")

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

    def __init__(self, name, subsystem, port, max_rate):
        self.name = name
        self.subsystem = subsystem
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

    def __init__(self, name, subsystem, switchport, relayport):
        self.name = name
        self.subsystem = subsystem
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

    def __init__(self, name, subsystem, A_port, B_port, tics_per_foot, max_rate):
        self.name = name
        self.subsystem = subsystem
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

class Joystick(Refrence):

    portrefs = [usbRefs]
    wpi_object_name = wpilib.Joystick.__name__

    def __init__(self, name, subsystem, port):
        self.name = name
        self.subsystem = subsystem
        self.get_wpiobject(name, port)

    def init_wpilib_refrence(self, name, port):
        self.wpiobject = wpilib.Joystick(port)

    def get_button(self, button):
        return self.wpiobject.GetRawButton(button)

    def get_axis(self, axis):
        return self.wpiobject.GetAxis(axis)

    def publish_to_table(self):
        pass
        #wpilib.SmartDashboard.PutString(self.name, self.dumpValues())
