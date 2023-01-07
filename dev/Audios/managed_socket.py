import socket
from requests import get
from threading import Thread
import uuid
import os
import time

def milliseconds():
  return round(time.time() * 1000)

class Socket(Thread):
  def __init__(self, host, port, s_type):
    Thread.__init__(self)
    self.host = host
    self.port = port
    self.type = s_type
    self.s = None
    self.thread = None
    self.connected = False
    self.events = {}
    self.lastPing = 0
    self.timeout = 10000
    self.lastConnection = 0
    self.decodeData = True
    self.enablePing = True

  def handleData(self, callback):
    self.lastPing = milliseconds()

    while self.connected:
      try:
        data = self.s.recv(1024)
        if data:
          if data[0] == 0x0 and self.enablePing:
            self.s.sendall((0x0).to_bytes(1, 'big'))
            self.lastPing = milliseconds()
          else:
            if self.decodeData:
              data = data.decode().split(';')
              if data[0] == "quit":
                self.s.close()
                break
              else:
                callback("data", data)
            else:
              callback("data", data)
      except Exception as err:
        print(err)
        self.connected = False

  def run(self):
    while True:
      try:
        if not self.connected and milliseconds() - self.lastConnection > 5000:
          self.lastConnection = milliseconds()
          self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.s.connect((self.host, self.port))
          self.s.sendall(bytes(f'type={self.type};mac={str(hex(uuid.getnode()))};name={os.environ["COMPUTERNAME"]}', encoding='utf8'))
          self.connected = True
          self.thread = Thread(target=self.handleData, args=(self.trigger, )).start()
        else:
          if self.lastPing != 0 and milliseconds() - self.lastPing > self.timeout:
            self.s.close()
            self.connected = False
      except Exception as err:
        print(err)
        continue

      time.sleep(0.01)

  def on(self, address: str, callback):
    self.events[address] = callback

  def trigger(self, address, data):
    if self.events[address] is not None:
      self.events[address](data)