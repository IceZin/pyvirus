import binascii
import os

class Events:
  def __init__(self):
    self.events = {}

  def trigger(self, *args):
    if args[0] in self.events:
      for callback in self.events[args[0]].values():
        callback(*args[1:])

  def destroy(self, event, callback_id):
    if event in self.events:
      if callback_id in self.events[event]:
        del self.events[event][callback_id]
  
  def on(self, event, callback):
    if event not in self.events:
      self.events[event] = {}

    callback_id = binascii.b2a_hex(os.urandom(10)).decode('utf-8')
    while callback_id in self.events[event]:
      callback_id = binascii.b2a_hex(os.urandom(10)).decode('utf-8')

    self.events[event][callback_id] = callback

    return callback_id

  def clear(self):
    self.events = {}

  def remove(self, event):
    if event in self.events:
      del self.events[event]