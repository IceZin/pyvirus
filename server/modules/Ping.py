import time

from queue import Queue
from threading import Thread

def milliseconds():
  return round(time.time() * 1000)


class Ping(Thread):
  def __init__(self, maxLoss, interval, conn):
    Thread.__init__(self)

    self.maxLoss = maxLoss
    self.interval = interval
    self.conn = conn
    self.awaitingPing = False
    self.pingTime = 0
    self.loss = 0
    self.queue = Queue()
    self.onEnd = None
    self.stopPing = False
    self.disable = False

  def run(self):
    while not self.stopPing:
      if not self.disable:
        if not self.awaitingPing:
          try:
            if milliseconds() - self.pingTime >= self.interval:
              self.conn.sendall((0x0).to_bytes(1, 'big'))
              self.awaitingPing = True
              self.pingTime = milliseconds()
          except Exception as err:
            break
        else:
          if (milliseconds() - self.pingTime) < self.interval:
            if not self.queue.empty():
              d = self.queue.get()
              if d == 0x0:
                self.awaitingPing = False
          else:
            self.loss += 1
            self.awaitingPing = False

            if self.loss == self.maxLoss:
              break

      time.sleep(0.01)

    self.conn.close()
    if self.onEnd:
      self.onEnd()