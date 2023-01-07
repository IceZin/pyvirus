import time

from modules.Ping import Ping
from events import Events
from threading import Thread

class Module(Thread):
  def __init__(self, conn):
    Thread.__init__(self)

    self.conn = conn
    self.events = Events()

    self.ping = Ping(10, 500, self.conn)
    self.ping.onEnd = self.onEnd
    self.ping.start()

    self.endThread = False

  def onEnd(self):
    self.events.trigger("end", None)
    self.endThread = True

  def handleData(self):
    while not self.endThread:
      try:
        data = self.conn.recv(32768)
        if data:
          if data[0] == 0x0:
            self.ping.queue.put(0x0)
          else:
            self.events.trigger("data", data.decode().split(';'))
      except Exception as err:
        print(err)
        self.ping.stopPing = True

      time.sleep(0.01)

  def run(self):
    self.handleData()

  def send(self, message):
    self.conn.sendall(bytes(message, encoding="utf-8"))