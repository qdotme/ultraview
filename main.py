from direct.showbase.ShowBase import ShowBase

__author__ = 'Tomasz'

from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter

from panda3d.core import PointerToConnection
from panda3d.core import NetAddress

from direct.task import Task

import socket
import sys
import struct
import math


from math import pi, sin, cos

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(cManager, 0)
        self.cReader = QueuedConnectionReader(cManager, 0)
        self.cWriter = ConnectionWriter(cManager,0)

        self.activeConnections=[] # We'll want to keep track of these later

        # port_address=9999 #No-other TCP/IP services are using this port
        # backlog=1000 #If we ignore 1,000 connection attempts, something is wrong!
        # tcpSocket = cManager.openTCPServerRendezvous(port_address,backlog)
        #
        # self.cListener.addConnection(tcpSocket)



        # Load the environment model.
        self.environ = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.environ.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        self.fetus = self.loader.loadModel("HumanFetus")
        self.fetus.reparentTo(self.render)

        # self.disableMouse()

        # self.taskMgr.add(self.tskListenerPolling,"Poll the connection listener",-39)
        # self.taskMgr.add(self.tskReaderPolling,"Poll the connection reader",-40)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', 9999))
        self.sock.listen(1)
        self.sock.setblocking(0)

        self.coords = [0, 0, 0]
        self.idx = 0

        self.taskMgr.add(self.acceptConns, "Poll the connection listener", -39)
        self.taskMgr.add(self.processConn, "Poll the connection itself", -40)
        # Add the spinCameraTask procedure to the task manager.
        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        # self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

    def acceptConns(self, taskdata):
        try:
            self.conn, info = self.sock.accept()
        except socket.error:
            return Task.cont

        print self.conn, info
        self.conn.setblocking(0)

        return Task.cont


    def processConn(self, taskdata):
        while True:

            try:
                data = self.conn.recv(4)
                if len(data) < 4:
                    return Task.cont

                # print ':'.join(x.encode('hex') for x in data)
                # print data, struct.unpack('>f', data)
                data = struct.unpack('>f', data)[0]

                if math.isnan(data):
                    if self.idx > 0:
                        print self.coords
                        self.camera.setPos(*self.coords)
                        # self.camera.setPos(3+self.coords[0], 3, 3)

                    self.idx = 0

                else:
                    self.coords[self.idx] = data
                    self.idx += 1


            except socket.error:
                return Task.cont
            except AttributeError:
                return Task.cont

        return Task.cont

app = MyApp()
app.run()
