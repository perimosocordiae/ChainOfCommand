from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.task.Task import Task
from pandac.PandaModules import *
from time import time,sleep
from random import choice

# adapted from http://www.panda3d.org/phpbb2/viewtopic.php?t=4881

class NetworkBase(object): # abstract base class for the client and server classes
    def __init__(self,port):
        self.port = port
        self.cManager = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager,0)

    def __processData(self, netDatagram):
        return PyDatagramIterator(netDatagram).getString()
    
    def send(self, data, conn):
        pdg = PyDatagram()
        pdg.addString(data)
        self.cWriter.send(pdg, conn)
        
    def getData(self):
        data = []
        while self.cReader.dataAvailable():
            datagram = NetDatagram()  # catch the incoming data in this instance
            # Check the return value; if we were threaded, someone else could have
            # snagged this data before we did
            if self.cReader.getData(datagram):
                data.append((self.__processData(datagram), datagram.getConnection()))
        return data

class Server(NetworkBase):
    def __init__(self, port, backlog=1000):
        super(Server,self).__init__(port)
        self.backlog = backlog
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.activeConnections = []
        self.player_dict = dict()
        self.ready_players = 0
        self.rand_seed = int(time())
        self.__connect(self.port, self.backlog)
        self.__startPolling()

    def __connect(self, port, backlog=1000):
        # Bind to our socket
        tcpSocket = self.cManager.openTCPServerRendezvous(port, backlog)
        self.cListener.addConnection(tcpSocket)

    def __startPolling(self):
        taskMgr.add(self.__tskListenerPolling, "serverListenTask", -40)
        taskMgr.add(self.__tskDisconnectPolling, "serverDisconnectTask", -39)
        
    def __tskListenerPolling(self, task):
        # look for new clients
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
        
            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.activeConnections.append(newConnection) # Remember connection
                self.cReader.addConnection(newConnection)     # Begin reading connection
                self.send("seed %d"%self.rand_seed,newConnection) # send the new client the random seed
                
        # republish messages
        for d in self.getData():
            ds = d[0].split()
            if ds[0] == 'player':
                append = ''
                while (d[0]+append) in self.player_dict :
                    if self.player_dict[d[0]+append].getAddress().getIpString() == '0.0.0.0' :
                        removeThis = self.player_dict[d[0]+append]
                        self.cReader.removeConnection(removeThis)
                        for c in range(len(self.activeConnections)):
                            if self.activeConnections[c] == removeThis:
                                del self.activeConnections[c]
                                break
                        break
                    append += choice(list('!@#$%^&*'))
                if append != '' :
                    dataCopy = list(ds)
                    del dataCopy[0] # get rid of 'player'
                    self.send('append_name %s'%append, d[1])
                if len(self.player_dict) > 0 :
                    firstPlayer = self.getFirstPlayer()
                self.player_dict[d[0]+append] = d[1]
                for p in self.player_dict: self.broadcast(p)
                if len(self.player_dict) > 1 :
                    self.broadcast('echo lobbyinfo')
                    self.send('echo gametype', self.player_dict[firstPlayer])
            elif ds[0] == 'unreg':
                pd = 'player %s'%ds[1]
                assert pd in self.player_dict
                del self.player_dict[pd]
                self.broadcast(d[0])
            elif d[0] == 'ready': 
                self.ready_players += 1
                if self.ready_players == len(self.player_dict):
                    self.send('DroneSpawner', self.player_dict[self.getFirstPlayer()])
                    # reset this game's data, so we're ready for the next one
                    self.player_dict.clear()
                    self.ready_players = 0
                    self.rand_seed = int(time())
                    self.broadcast('go')
            else:
                self.broadcast(d[0])
        return Task.cont
    
    def __tskDisconnectPolling(self, task):
        while self.cManager.resetConnectionAvailable():
            connPointer = PointerToConnection()
            self.cManager.getResetConnection(connPointer)
            connection = connPointer.p()
            # Remove the connection we just found to be "reset" or "disconnected"
            self.cReader.removeConnection(connection)
            # Loop through the activeConnections till we find the connection we just deleted
            # and remove it from our activeConnections list
            for c in range(len(self.activeConnections)):
                if self.activeConnections[c] == connection:
                    del self.activeConnections[c]
                    break       
        return Task.cont
    
    def broadcast(self, data):
        # Broadcast data out to all activeConnections
        for con in self.activeConnections:
            self.send(data, con)
    
    def getFirstPlayer(self):
        if len(self.player_dict) < 1 : return
        else: return self.player_dict.keys()[0]
        
    def shutdown(self):
        for conn in self.activeConnections:
            self.cManager.closeConnection(conn)
        taskMgr.remove("serverListenTask")
        taskMgr.remove("serverDisconnectTask")

class Client(NetworkBase):
    def __init__(self, host, port, timeout=3000):
        super(Client,self).__init__(port)
        self.host = host
        self.timeout = timeout
        self.server_conn = None # By default, we are not connected
        self.__connect(self.host, self.port, self.timeout)
        self.__startPolling()
        
    def __connect(self, host, port, timeout=3000):
        # Connect to our host's socket
        self.server_conn = self.cManager.openTCPClientConnection(host, port, timeout)
        if self.server_conn:
            self.cReader.addConnection(self.server_conn)  # receive messages from server
        else:
            raise EnvironmentError()
    
    def __startPolling(self):
        taskMgr.add(self.__tskDisconnectPolling, "clientDisconnectTask", -39)
    
    def __tskDisconnectPolling(self, task):
        while self.cManager.resetConnectionAvailable():
            connPointer = PointerToConnection()
            self.cManager.getResetConnection(connPointer)
            connection = connPointer.p()
            # Remove the connection we just found to be "reset" or "disconnected"
            self.cReader.removeConnection(connection)
            self.connected = False     
        return Task.cont
    
    def send(self, data, conn=None):
        super(Client,self).send(data, self.server_conn)
    
    def close_connection(self):
        self.cManager.closeConnection(self.server_conn)
