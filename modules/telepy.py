__author__ = 'christian'

from framework import ModBase, ModMaster
import socket

class module(ModBase.module):

    name = "remote"

    def moduleLoad(self):
        sock = socket.socket()
        host = socket.gethostname()
        port = 4819
        sock.bind((host, port))

        while not self.stopFlag:
            sock.listen(5)

