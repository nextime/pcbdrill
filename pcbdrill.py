import Tkinter as tk
import tkFileDialog as fd
import tkMessageBox as mbox
import numpy as np
import re 
import cv2
import excellon
import serial
from PIL import ImageTk,Image
import sys, os
import pickle
global coordinates, camdev, printerdev, ser
FPATH = None
FILEOPENED=False
app = tk.Tk()
app.title('PCB Drill Utility - 1.0')
app.rowconfigure(0, weight=1)
app.columnconfigure(0, weight=1)
CANVAS=tk.Canvas(app, bg='white')
CANVAS.grid(row=0,column=0,rowspan=2,sticky='nsew')
GCODE = tk.Text(app)
GCODE.grid(row=0,column=1,sticky='nsew')
NEWGCODE=tk.Text(app)



def left_click(event):
   if FILEOPENED:
      foro=myBoard.find_by_id(CANVAS.find_closest(event.x, event.y)[0])
      if len(myBoard.referencePoints)>=3:
         mbox.showwarning(message='3 holes are enough for computation !')
         get_real_coord(foro.get_coord())
      else:
         if foro.get_coord() in myBoard.referencePoints:
            mbox.showwarning(message='You just selected this hole !')
         else:
            CANVAS.itemconfigure(foro.id,fill='green')
            get_real_coord(foro.get_coord())
            myBoard.referencePoints[foro.get_coord()]=[]
         
def get_real_coord(coord):

   def close_popup(coord, canvas):
      global capture
      try:
         capture.release()
      except:
         pass
      return ret(coord,coordinates.get())

   def send_gcode(gcode):
      global ser
      print 'SEND GCODE->', gcode
      ser.write(gcode.upper()+"\r\n")
      ser.flush()

   global coordinates,POPUP,printerdev,ser
   POPUP=tk.Toplevel()
   POPUP.title('Insert the real coordinates')
   label=tk.Label(POPUP,text='Please insert the real coordinates for this point : ')
   coordinates=tk.Entry(POPUP)
   canvas = tk.Canvas(POPUP,width=800,height=600)
   ok=tk.Button(POPUP,text='Ok',command=lambda: close_popup(coord, canvas))
   cameraButton=tk.Button(POPUP,text='Open Camera',command=lambda: openCamera(POPUP,canvas))
   cameraButton.grid()
   coordinates.insert(0, 'X'+str(coord[0])+' Y'+str(coord[1]))
   label.grid()
   canvas.grid()
   canvas.grid_forget()
   coordinates.grid()
   if printerdev:
      print 'OPEN SERIAL', printerdev
      ser = serial.Serial(
           port=printerdev,
           baudrate=115200,
           #parity=serial.PARITY_ODD,
           #stopbits=serial.STOPBITS_TWO,
           #bytesize=serial.SEVENBITS
      )
      ser.write("G01 F500+\r\n")
      gcode=tk.Entry(POPUP)
      gcode.insert(0, 'gcode here')
      gcode.grid()
      up=tk.Button(POPUP,text='SEND GCODE',command=lambda: send_gcode(gcode.get()))
      up.grid()
      update_serial(up)
   ok.grid()
   

def openCamera(window,canvas):
   global capture, camdev, printerdev, ser
   
   if camdev:
      print 'OPEN CAMDEV'
      capture = cv2.VideoCapture()
      capture.open(camdev)
      if not capture.isOpened() :
         mbox.showwarning(message='Webcam not found !')
         return
   else:
      capture = cv2.VideoCapture(1)
      print 'OPEN CAPTURE CAMERA 1'
      if not capture.isOpened() :
         print 'OPEN CAPTURE CAMERA 0'
         capture = cv2.VideoCapture(0)
         if not capture.isOpened():
            mbox.showwarning(message='Webcam not found !')
            return
   canvas.grid()
   update_frame(window,capture,canvas)
      

def viewCamera():
   def closePopup(cap, pop):
      cap.release()
      pop.destroy()

   if camdev:
      print 'OPEN CAMDEV'
      capture = cv2.VideoCapture()
      capture.open(camdev)
      if not capture.isOpened() :
         mbox.showwarning(message='Webcam not found !')
         return
   else:
      capture = cv2.VideoCapture(1)
      if not capture.isOpened():
         capture = cv2.VideoCapture(0)
         if not capture.isOpened():
            mbox.showwarning(message='Webcam not found !')
            return
   camPopup=tk.Toplevel()
   camPopup.title('Camera View')
   camPopup.protocol('WM_DELETE_WINDOW', lambda: closePopup(capture, camPopup))
   canvas = tk.Canvas(camPopup, width=800,height=600)
   canvas.grid()
   update_frame(camPopup, capture, canvas)


def setCameraOffset():
   if camdev:
      print 'OPEN CAMDEV'
      capture = cv2.VideoCapture()
      capture.open(camdev)
      if not capture.isOpened() :
         mbox.showwarning(message='Webcam not found !')
         return
   else:
      capture = cv2.VideoCapture(1)
      if not capture.isOpened():
         capture = cv2.VideoCapture(0)
         if not capture.isOpened():
            mbox.showwarning(message='Webcam not found !')
            return
   offsetPopup=tk.Toplevel()
   offsetPopup.title('Set Camera Offset')
   label=tk.Label(offsetPopup,text='Please insert the camera offset')
   coordinates=tk.Entry(offsetPopup)
   ok=tk.Button(offsetPopup,text='Ok',command=lambda: myBoard.setOffset(capture,offsetPopup,(coordinates.get().upper().replace('X','').replace('Y','').split())))
   coordinates.insert(0, "X0.00 Y0.00")
   canvas = tk.Canvas(offsetPopup, width=800,height=600)
   label.grid()
   canvas.grid()
   coordinates.grid()
   ok.grid()
   update_frame(offsetPopup, capture, canvas)


def update_serial(btn):
   global ser
   if ser:
      out=''
      while ser.inWaiting() > 0:
         out += ser.read(1)
      if out:
         print 'SERIAL IN->', out
      btn.after(500, update_serial, btn)

def update_frame(window, capture, canvas):
   frame=capture.read()[1]
   if frame is not None:
      frame=cv2.resize(frame,(800,600))
      frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      # HUD
      height,width,p=frame.shape
      cv2.line(frame,(width/2,0),(width/2,height),(255,255,255),thickness=1)
      cv2.line(frame,(0,height/2),(width,height/2),(255,255,255),thickness=1)
      cv2.circle(frame,(width/2,height/2),50,(255,255,255),thickness=1)
      a=Image.fromarray(frame)
      image= ImageTk.PhotoImage(image=a)
      canvas.create_image(width/2, height/2, image=image)
      canvas.update()
      canvas.after(0, func=lambda: update_frame(window, capture, canvas))
   else:
      print 'RELEASE CAMERA CAUSE NO FRAME'
      capture.release()
   
   
      
def ret(coord,realcoord):
   x,y=coord
   x_real,y_real=realcoord.upper().replace('X','').replace('Y','').split()
   POPUP.withdraw()
   myBoard.referencePoints[coord]=(float(x_real)-myBoard.cameraOffset[0],float(y_real)-myBoard.cameraOffset[1])
   print 'REFERENCE POINTS->',  myBoard.referencePoints
   print 'REFERENCE CAMERA OFFSET[0]->', myBoard.cameraOffset[0]
   
   
def compute_matrix():
   global NEW_GCODE
   original_coord=[]
   real_coord=[]
   for key,value in myBoard.referencePoints.items():
      original_coord.append(key)
      real_coord.append(value)
   xa,ya=original_coord[0]
   xb,yb=original_coord[1]
   xc,yc=original_coord[2]
   xaa,yaa=real_coord[0]
   xbb,ybb=real_coord[1]
   xcc,ycc=real_coord[2]
   M=np.matrix([[xa,xb,xc],[ya,yb,yc],[1,1,1]])
   S=np.matrix([[xaa,xbb,xcc],[yaa,ybb,ycc]])
   myBoard.transformationMatrix=S*(M.I)
   print 'Transformation Matrix->', myBoard.transformationMatrix
   update_hole_coord()
   
def update_hole_coord():
   for hole in myBoard.holes:
      old_coord=np.array([[hole.x],[hole.y],[1]])
      a,b=np.dot(myBoard.transformationMatrix,old_coord).tolist()
      hole.new_x=a[0]
      hole.new_y=b[0]
      myBoard.update_range((a[0],b[0]))
   
def right_click(event):
   if FILEOPENED:
      myBoard.referencePoints.clear()
      for hole in myBoard.holes:
         CANVAS.itemconfigure(hole.id,fill='red')
def do_quit():
    app.quit()
def do_calculate():
   global FILEOPENED
   if FILEOPENED:
      if len(myBoard.referencePoints)==3:
         compute_matrix()
         new_gcode()
      else:
         mbox.askokcancel(message='Please select three holes for matrix computation')
   else:
      mbox.showwarning(message='Please open a file first')
def do_about():
   mbox.showinfo('PCB Drill Utility','This is a pre-alpha release, use it carefully. \nFor contact please mail to: mail@alessiovaleri.it''')
   
def do_open():
   #if not myBoard.offsetIsSet:
   #   mbox.showwarning(message='Please set the camera offset first !')
   #   return
   path = fd.askopenfilename(title='Select a file', 
                              filetypes=[('Nc File', '*.nc'),("text", "*.txt"), 
                                         ('Ngc File', '*.ngc')])
   if len(path) > 0:
      real_open(path)

def real_open(path):
   global FPATH,FILEOPENED
   GCODE.delete('1.0', 'end')
   NEWGCODE.delete('1.0', 'end')
   NEWGCODE.grid_forget()
   with open(path, 'r') as f:
      file=f.readlines()
   FPATH = path
   FILEOPENED=True
   myBoard.reset()
   CANVAS.delete('all')
   file_to_object(file)
      
def importExcellon():
   #if not myBoard.offsetIsSet:
   #   mbox.showwarning(message='Please set the camera offset first !')
   #   return
   path = fd.askopenfilename(title='Select a file',filetypes=[('Excellon File', '*.dri')])
   if len(path) > 0:
      global FILEOPENED
      GCODE.delete('1.0', 'end')
      NEWGCODE.delete('1.0', 'end')
      NEWGCODE.grid_forget()
      FILEOPENED=True
      myBoard.reset()
      CANVAS.delete('all')
      with open(path, 'r') as f:
         file=f.readlines()
      for index,row in enumerate(file):
         if row.startswith('Plotfiles:'):
            filename=file[index+2].replace('\n','').strip()
            try:
               with open(filename):pass
               getExcellonParameters(filename)
            except:
               with open(path[:-4]):pass
               getExcellonParameters(path[:-4])
               
def getExcellonParameters(filename):
   window=tk.Toplevel()
   window.title('Import Excellon')
   clearanceLb=tk.Label(window,text='Z Clearance')
   clearance=tk.Entry(window)
   depthLb=tk.Label(window,text='Z Depth')
   depth=tk.Entry(window)
   feedLb=tk.Label(window,text='Cutting Speed')
   feed=tk.Entry(window)
   v=tk.StringVar()
   mm=tk.Radiobutton(window,text='mm',variable=v,value='mm')
   inch=tk.Radiobutton(window,text='inch',variable=v,value='inch')
   unit=tk.Label(window,text='Output Units')
   importBt=tk.Button(window,text='Import',command=lambda: doImportExcellon(window,filename,(v,int(clearance.get()),int(depth.get()),int(feed.get()))))
   clearanceLb.grid(row=0,column=0)
   clearance.grid(row=0,column=1)
   depthLb.grid(row=1,column=0)
   depth.grid(row=1,column=1)
   feedLb.grid(row=2,column=0)
   feed.grid(row=2,column=1)
   unit.grid(row=3,column=0,rowspan=2)
   mm.grid(row=3,column=1)
   inch.grid(row=4,column=1)
   importBt.grid(row=5,columnspan=2)

def doImportExcellon(window,filename,parameters):
   window.destroy()
   file_to_object(excellon.excellonToGcode(filename,parameters))      
    

def new_gcode():
   x=0
   y=0
   NEWGCODE.grid(row=0,column=2,sticky='nsew')
   newfile=GCODE.get('1.0', 'end').split('\n')
   reg = re.compile("((?P<xy>[Xx]\b*([-]?)\b*(\d*).?(\d*)\s+[Yy]\b*([-]?)\b*(\d*).?(\d*))|(?P<yx>[Yy]\b*([-]?)\b*(\d*).?(\d*)\s+[Xx]\b*([-]?)\b*(\d*).?(\d*))|(?P<x>[Xx]\b*([-]?)\b*(\d*).?(\d*))|(?P<y>[Yy]\b*([-]?)\b*(\d*).?(\d*)))")
   for row in newfile:
      newrow=row
      result=reg.search(row)
      if result:
         found=True
         if result.group('xy'):
            x=float(result.group(3)+result.group(4)+'.'+result.group(5))
            y=float(result.group(6)+result.group(7)+'.'+result.group(8))
            old_coord=np.array([[x],[y],[1]])
            a,b=np.dot(myBoard.transformationMatrix,old_coord).tolist()
            newrow=re.sub('([Xx]\b*([-]?)\b*(\d*).?(\d*)\s+[Yy]\b*([-]?)\b*(\d*).?(\d*))','X'+str(a[0])+' Y'+str(b[0]),result.string)
         if result.group('yx'):
            x=float(result.group(13)+result.group(14)+'.'+result.group(15))
            y=float(result.group(10)+result.group(11)+'.'+result.group(12))
            old_coord=np.array([[x],[y],[1]])
            a,b=np.dot(myBoard.transformationMatrix,old_coord).tolist()
            newrow=re.sub('([Yy]\b*([-]?)\b*(\d*).?(\d*)\s+[Xx]\b*([-]?)\b*(\d*).?(\d*))','X'+str(a[0])+' Y'+str(b[0]),result.string)
         if result.group('x'):
            x=float(result.group(17)+result.group(18)+'.'+result.group(19))
            old_coord=np.array([[x],[y],[1]])
            a,b=np.dot(myBoard.transformationMatrix,old_coord).tolist()
            newrow=re.sub('([Xx]\b*([-]?)\b*(\d*).?(\d*))','X'+str(a[0])+' Y'+str(b[0]),result.string)
         if result.group('y'):
            y=float(result.group(21)+result.group(22)+'.'+result.group(23))
            old_coord=np.array([[x],[y],[1]])
            a,b=np.dot(myBoard.transformationMatrix,old_coord).tolist()
            newrow=re.sub('([Yy]\b*([-]?)\b*(\d*).?(\d*))','X'+str(a[0])+' Y'+str(b[0]),result.string)
         
      NEWGCODE.insert('end', newrow+'\n')
def file_to_object(file):
      reg = re.compile("((?P<xy>[Xx]\b*([-]?)\b*(\d*).?(\d*)\s+[Yy]\b*([-]?)\b*(\d*).?(\d*))|(?P<yx>[Yy]\b*([-]?)\b*(\d*).?(\d*)\s+[Xx]\b*([-]?)\b*(\d*).?(\d*))|(?P<x>[Xx]\b*([-]?)\b*(\d*).?(\d*))|(?P<y>[Yy]\b*([-]?)\b*(\d*).?(\d*)))")
      x=0
      y=0
      for row in file:
         GCODE.insert('end', row)         
         found=False
         if (' x' in row and ' y' in row) or (' X' in row and ' Y' in row):
            splitrow = row.split()
            x=False
            y=False
            for sr in splitrow:
               if sr.startswith('x') or sr.startswith('X'):
                  x=sr[1:]
               elif sr.startswith('y') or sr.startswith('Y'):
                  y=sr[1:]
            if x and y:
               found=True

         else:
            result=reg.search(row)
            if result:
               print 'RESULT->', result
               found=True
               if result.group('xy'):
                  x=result.group(3)+result.group(4)+'.'+result.group(5)
                  y=result.group(6)+result.group(7)+'.'+result.group(8)               
               if result.group('yx'):
                  x=result.group(13)+result.group(14)+'.'+result.group(15)
                  y=result.group(10)+result.group(11)+'.'+result.group(12)
               if result.group('x'):
                  x=result.group(17)+result.group(18)+'.'+result.group(19)
               if result.group('y'):
                  y=result.group(21)+result.group(22)+'.'+result.group(23)
      
         if found:
            print 'X->', x, 'Y->', y, 'ROW->', row
            myBoard.add_hole((float(x),float(y)))
   
      for fori in myBoard.holes:
         print 'FORI->', fori.get_coord()
      show_holes()
def show_holes():         
   for hole in myBoard.holes:
         hole.render()   
   CANVAS.after(50,show_holes)
def do_saveas():
    path = fd.asksaveasfilename(title='Dove Salvare')
    if len(path) > 0:
        global FPATH
        with open(path, 'w') as f:
            f.write(NEWGCODE.get('1.0', 'end'))
        app.title(path)
        FPATH = path

def do_help():
   mbox.showinfo(message='''To compute an affine trasnsformation on a plane, three points are needed.\nPlease select them with a left click and input the coordinates you are detecting on your machine. Right click to deselect.\nPress 'Transform' to start computation and the new gcode file is ready to be saved.\nFor further information visit http://www.alessiovaleri.it\nHappy drilling :-)''')
         
class Board():
   
   def __init__(self):
      self.X_range=[]
      self.Y_range=[]
      self.holes=[]
      self.cameraOffset=(0,0)
      #self.offsetIsSet=False
      self.referencePoints={}
      self.transformationMatrix=[]
   def add_hole(self,coord):
      self.update_range(coord)
      self.holes.append(Hole(coord))
   def update_range(self,coord):
      x,y=coord
      self.X_range.append(float(x))
      self.Y_range.append(float(y))
      self.X_range=[min(self.X_range),max(self.X_range)]
      self.Y_range=[min(self.Y_range),max(self.Y_range)]
   def scale(self):
      space=50
      try:
         return min((CANVAS.winfo_width()-space)/abs(self.X_range[1]-self.X_range[0]),(CANVAS.winfo_height()-space)/abs(self.Y_range[1]-self.Y_range[0]))      
      except:
         return 0.0
   def x_min(self):
      return int(self.X_range[0])
   def y_min(self):
      return int(self.Y_range[0])
   def find_by_id(self,id):
      for hole in self.holes:
         if hole.id==id:
            return hole
   def setOffset(self,camera,appdow,coord):
      camera.release()
      appdow.destroy()
      self.cameraOffset=(float(coord[0]),float(coord[1]))
      #self.offsetIsSet=True
      print 'CAMERA OFFSET->', self.cameraOffset
   def reset(self):
      self.X_range=[]
      self.Y_range=[]
      self.holes=[]
      self.referencePoints={}
      
class Hole():
   def __init__(self,coordinate):
      x,y=coordinate
      self.radius=2
      self.x=x
      self.new_x=x
      self.y=y
      self.new_y=y
      self.id=CANVAS.create_oval(x-self.radius,y-self.radius,x+self.radius,y+self.radius,fill='red')
      
   def get_coord(self):
      return(self.new_x,self.new_y)
   def get_old_coord(self):
      return(self.x,self.y)
   def render(self):
      space=6
      a=(self.new_x-myBoard.x_min())*myBoard.scale()
      b=(self.new_y-myBoard.y_min())*myBoard.scale()
      CANVAS.coords(self.id,a+self.radius,CANVAS.winfo_height()-b-self.radius-space,a+self.radius+space,CANVAS.winfo_height()-b-self.radius)
   
      
      
      
      
def do_savemtx():
   path = fd.asksaveasfilename(title='Dove Salvare', filetypes=[("PCB Matrix", "*.mtx")], initialfile="untitled.mtx")
   if len(path) > 0:
      f=open(path, "w")
      pickle.dump(myBoard.transformationMatrix, f)
      f.close()


def importMatrix():
   path = fd.askopenfilename(title='Select a file', filetypes=[("PCB Matrix", "*.mtx")])
   if len(path) > 0:
      f=open(path, "r")
      myBoard.transformationMatrix=pickle.load(f)
      f.close()


def applyMatrix():
   update_hole_coord()
   new_gcode()

   
camdev=False
printerdev=False
mb = tk.Menu(app) 
app.config(menu=mb)
fm = tk.Menu(mb)
fm.add_command(label='Open...', command=do_open)
fm.add_command(label='Import Excellon', command=importExcellon)
fm.add_command(label='Import matrix', command=importMatrix)

fm.add_command(label='Save', command=do_saveas)
fm.add_separator()
fm.add_command(label='Save matrix', command=do_savemtx)
fm.add_command(label='Help', command=do_help)
fm.add_separator()
fm.add_command(label='About',command=do_about)
fm.add_separator()
fm.add_command(label='Quit', command=do_quit)
mb.add_cascade(label='File', menu=fm)
CALCULATE=tk.Button(app,text='Compute Transform',command=do_calculate)
CALCULATE.grid(row=1,column=1,columnspan=2,sticky='nsew')
APPLYMTX=tk.Button(app,text='Apply Transform',command=applyMatrix)
APPLYMTX.grid(row=2,column=1,columnspan=2,sticky='nsew')
OPEN_CAMERA=tk.Button(app,text='Set Camera Offset',command=setCameraOffset)
OPEN_CAMERA.grid(row=3,column=1,columnspan=2,sticky='nsew')
VIEW_CAMERA=tk.Button(app,text='View Camera',command=viewCamera)
VIEW_CAMERA.grid(row=4,column=1,columnspan=2,sticky='nsew')
CANVAS.bind('<Button-1>',left_click)
CANVAS.bind('<Button>',right_click)
myBoard=Board()
if len(sys.argv) > 1:
   for ar in sys.argv[1:]:
      print 'check', ar
      if ar.startswith('/dev/video'):
         try:
            if int(ar[-1]) in [0,1,2,3,4,5,6,7,8,9]:
               camdev=int(ar[-1])
         except:
            pass
      elif ar.startswith('/dev/'):
         printerdev=ar
         ser=False
      elif os.path.isfile(ar) and (ar.endswith('.txt') or ar.endswith('nc') or ar.endswith('gcode') or ar.endswith('ngc')):
         real_open(ar)
tk.mainloop()


      
