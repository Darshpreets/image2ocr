#request for api
import requests
#json for api data handling
import json
#to check internet connection
import socket
#GUI using Tkinter
from Tkinter import *

import pygame.camera    
pygame.camera.init()
cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
#image saving
import pygame.image

#for datetime
from datetime import datetime
#tesseract
import sys
#offline text extraction
import pytesseract
import os
import sqlite3

timeStamp = ""
DIR = os.getcwd() + "/images/"
if not os.path.exists("images"):
    os.makedirs("images")

def database_insert(str):
  global timeStamp
  conn = sqlite3.connect('records.db')
  conn.execute('''CREATE TABLE IF NOT EXISTS records
       (datetime TEXT PRIMARY KEY NOT NULL,
       path  TEXT NOT NULL,
       ocrtext TEXT );''')
  conn.execute("""INSERT INTO records (datetime, path, ocrtext)
       VALUES ( '""" + timeStamp  + """', ' """ 
       + DIR + timeStamp + ".jpg" + """', ' """ 
       + str + """')""")
  conn.commit()
  conn.close()

def database_query():
  for row in conn.execute('SELECT * FROM records'):
    print row


def save_image(e):
  global timeStamp
  cam.start()
  img = cam.get_image()
  timeStamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
  pygame.image.save(img, DIR + timeStamp + ".jpg")
  cam.stop()
  pygame.camera.quit()

#To check internet connection
REMOTE_SERVER = "www.google.com"
def is_connected():
  try:
    host = socket.gethostbyname(REMOTE_SERVER)
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False


#function to utilize ocr.space api
def ocr_space_file(filename, overlay=False, api_key='890b59f2b188957', language='eng'):
  payload = {'isOverlayRequired': overlay,
             'apikey': api_key,
             'language': language,
             }
  with open(filename, 'rb') as f:
      r = requests.post('https://api.ocr.space/parse/image',
                        files={filename: f},
                        data=payload,
                        )
  return r.content.decode()

def show_result(str):
  global timeStamp
  toplevel = Toplevel()
  text = Text(toplevel)
  scroll = Scrollbar(toplevel, command=text.yview)
  text.configure(yscrollcommand=scroll.set)
  text.insert(END, str)
  text.pack(side=LEFT)
  scroll.pack(side=RIGHT, fill=Y)


def do_ocr(e):
  global timeStamp
  if is_connected():
    data = json.loads(ocr_space_file(filename=DIR + timeStamp + ".jpg"))
    if not data['ParsedResults'][0]['ErrorMessage']:
      value = data['ParsedResults'][0]['ParsedText']
      print("\nOutput: " + value)
      show_result(str="\n\tOutput:\n" + value)
      database_insert(str = value)
    else:
      errorMsg = data['ParsedResults'][0]['ErrorDetails']
      print("\nError: " + errorMsg)
      show_result(str="\n\tError:\n" + errorMsg)
  else:
    show_result(pytesseract.image_to_string(Image.open(DIR + timeStamp + ".jpg")))

root = Tk()
root.title("OCR")
labelText = "Press any key to do OCR"
if not is_connected():
  labelText = labelText + "\n\nPlease Connect to internet for better accuracy"
label = Label(root, text=labelText, height=0, width=100)

label.pack()
b = Button(root, text="Quit", width=20, command=root.destroy)
b.pack(side='bottom',padx=0,pady=0)
frame = Frame(root, width=250, height=500)
frame.bind("<KeyPress>", save_image)
frame.bind("<KeyRelease>", do_ocr)
frame.pack()
frame.focus_set()
root.mainloop()
