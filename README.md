[![Build Status](https://travis-ci.org/Team4819/4819-2014-Offseason-RobotPy.svg?branch=master)](https://travis-ci.org/Team4819/4819-2014-Offseason-RobotPy)
[![Coverage Status](https://coveralls.io/repos/Team4819/4819-2014-Offseason-RobotPy/badge.png)](https://coveralls.io/r/Team4819/4819-2014-Offseason-RobotPy)
[![Code Health](https://landscape.io/github/Team4819/4819-2014-Offseason-RobotPy/master/landscape.png)](https://landscape.io/github/Team4819/4819-2014-Offseason-RobotPy/master)

This is experimental offseason code for Team 4819.

###Overview:
This year's offseason robot code project is written in Python. We use RobotPy, which is a python wrapper for the C++ wpi library, for running it on the cRIO.

More than code for just one robot, this repository is the building and testing place for our custom python framework.

###Framework:

Our new framework effectively isolates the robot-specific python code into "Modules", which are independent python files that are dynamically loaded at run-time. Modules can be freely manipulated, loaded, unloaded, replaced, and worked on at any time.

###Modules:
For examples of modules, see the modules/examples directory for a couple of well-commented example modules. For now, actual robot-driving modules are categorized by author, so all of the modules under modules/christian are my modules.

There are two main ways to change what modules are run on the robot: One is the config file, and the other is the remote control utility:

##Config file:
For refrence, here is a bare-bones config file:
```
[StartupMods]
drivetrain
intake
autonomous

[drivetrain]
modules.author.basic_drive
modules.author.enhanced_drive

[intake]
modules.author.intake

[autonomous]
modules.author.simple_auto
```
Modules are known to the framework by two names, their filename (modules.christian.basic_drive] and their subsystem name (drivetrain). When communicating between modules, you should always use the subsystem name, as modules can be interchanged at any time. 

The config file does two things: it specifies what subsystems should be loaded at startup, and it lists the actual module filenames that fall under those subsystem names.

When specifying a list of module filenames, you are also letting the framework know what modules can be switched to in case of module failure. The first listed module is always used first, but if something were to go wrong with it, it will get immediately replaced with the next module in-line.

##Module reloading:

Due to the nature of python, the ability to reload modules means that code modifications can be run instantaneously. For the cRIO, ftp can be used to upload modified modules mid-run. The module reload can be run either from the remote utilty, or by pressing button 10 on joystick 1.

##Remote utility:

The remote utility uses pynetworktables to connect to a framework_remote module run on the robot. It provides a nice visualization of what is actually happening in the framework, and provides fine controls to manipulate the framework.

The script is located under scripts/remote.py, and it reqires one argument: the ip address of wherever the robot code is running.



