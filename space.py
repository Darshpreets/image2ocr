#request for api
import requests
#json for api data handling
import json
#to check internet connection
import socket
#GUI using Tkinter
from Tkinter import *
#openCV
import cv2
#for datetime
from datetime import datetime
#tesseract
import sys
#offline text extraction
import pytesseract

imageName = ""

def save_image(e):
  global imageName
  imageName = datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ".jpg"
  camera = cv2.VideoCapture(0) #0 for default 
  retval, cameraCapture = camera.read()
  cv2.imwrite(imageName, cameraCapture)
  del(camera)

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
  global imageName
  toplevel = Toplevel()
  text = Text(toplevel)
  scroll = Scrollbar(toplevel, command=text.yview)
  text.configure(yscrollcommand=scroll.set)
  text.insert(END, str)
  text.pack(side=LEFT)
  scroll.pack(side=RIGHT, fill=Y)


def do_ocr(e):
  global imageName
  if is_connected():
    data = json.loads(ocr_space_file(filename=imageName))
    if not data['ParsedResults'][0]['ErrorMessage']:
      print("\nOutput: "data['ParsedResults'][0]['ParsedText'])
      show_result(str="\n\tOutput:\n" + data['ParsedResults'][0]['ParsedText'])
    else:
      print("\nError: " + data['ParsedResults'][0]['ErrorDetails'])
      show_result(str="\n\tError:\n" + data['ParsedResults'][0]['ErrorDetails'])
  else:
    show_result(pytesseract.image_to_string(Image.open(imageName)))



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
