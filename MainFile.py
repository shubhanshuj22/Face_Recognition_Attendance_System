import csv
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import yagmail
import datetime
import os
import time
import re 
import tkinter as tk
from tkinter import * 
from tkinter import messagebox




# counting the numbers


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

# Take image function to add image data 
def takeImages(Id,name):
    

#     Id = input("Enter Your Roll-Id: ")
#     name = input("Enter Your Name: ")

    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0

        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                #incrementing sample number
                sampleNum = sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage" + os.sep +name + "."+Id + '.' +
                            str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
                #display the frame
                cv2.imshow('frame', img)
            #wait for 100 miliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum > 100:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for ID : " + Id + " Name : " + name
        row = [Id, name]
        with open("StudentDetails"+os.sep+"StudentDetails.csv", 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        messagebox.showinfo("Success", "Student added successfully")
    else:
        messagebox.showinfo("Failed", "Student is not added")


        
            
# Check Camera is working or not         
def camer():
#     cap = cv2.VideoCapture(0)
    cam = cv2.VideoCapture(0)
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    sampleNum = 0

    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #display the frame
            cv2.imshow('frame', img)
            
        #wait for 100 miliseconds
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cam.release()
    cv2.destroyAllWindows()
        
#     while(True):
#         #capture frame-by-frame
#         ret, frame  = cap.read()
#         #operations on the frame come here
#         gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
#         #display the resulting frame
#         cv2.imshow('frame', gray)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     # when everything is done
#     cap.release()
#     cv2.destroyAllWindows()
    
    
# -------------- image labesl ------------------------
def getImagesAndLabels(path):
    from PIL import Image

    # get the path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # print(imagePaths)

    # create empth face list
    faces = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
#         print(imagePath)
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids


# ----------- train images function ---------------
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel"+os.sep+"Trainner.yml")
    messagebox.showinfo("Success", "Images Trained successfully")
    
# recognize Face and take attendence and save into date.csv
def recognize_attendence():
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
    recognizer.read("TrainingImageLabel"+os.sep+"Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv("StudentDetails"+os.sep+"StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)

    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for(x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

            if(conf < 50):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                aa = df.loc[df['Id'] == Id]['Name'].values
                tt = str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]

            else:
                Id = 'Unknown'
                tt = str(Id)
            if(conf > 75):
                noOfFile = len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown"+os.sep+"Image"+str(noOfFile) +
                            ".jpg", im[y:y+h, x:x+w])
            cv2.putText(im, str(tt), (x, y+h), font, 1, (255, 255, 255), 2)
        attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
        cv2.imshow('im', im)
        if (cv2.waitKey(1) == ord('q')):
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    fileName = "Attendance"+os.sep+"Attendance_"+date+".csv"
    attendance.to_csv(fileName, index=False)
    cam.release()
    cv2.destroyAllWindows()

    messagebox.showinfo("Success", "Attendance taken successfully")

# Decrypt password
def decr(ans):
    l=''
    for i in ans:
        x=chr((((ord(i)-97)-2756)%25)+97)
        l+=x;
    return l;

# Function for automatic mail
def mailMe():
    global email
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    receiver = email  # receiver email address
    body = "Attendence File"  # email body
    filename = "Attendance"+os.sep+"Attendance_"+date+".csv"  # attach the file

    # mail information
    yag = yagmail.SMTP("Email@gmail.com", decr("sjdkjdskjs"))

    # sent the mail
    yag.send(
        to=receiver,
        subject="Attendance Report Of "+date,  # email subject
        contents=body,  # email body
        attachments=filename,  # file attached
    )
    messagebox.showinfo("Success", "Attendance Mailed Successfully")

    

# ----------------------------------------------------GUI Code----------------------------------------- 

# LoginPage

def emailValid():
    global email
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    email=username.get()
    if(re.search(regex,email) ): 
        login.destroy()
    else:
        messagebox.showinfo("Error", "Wrong Email Address")
        
def loginpage():
    
    Label(login,text="Enter Your email : ",font=16).grid(row=1,column=1,sticky=E,padx=50)
    em=Entry(login,textvariable=username,width=40,font=16)
    em.grid(row=1,column=2,padx=50,pady=30,sticky=W)
    
    Button(login,text="Login",font=16,command=emailValid).grid(row=2,column=2,pady=30)

    login.mainloop()

def validName(e1,e2,inn):
    global name,roll;
    roll= e1.get();
    name=e2.get()
    if(name.isalpha()==False):
        messagebox.showinfo("Error", "Enter Alphabetical Name")
    elif(is_number(roll)==False):
        messagebox.showinfo("Error", "Enter Numeric Roll ID")
    else:
        inn.destroy()
        takeImages(roll,name)
        
    

    
    
def inName():
    from functools import partial
    inn= tk.Tk(className="Add Image Data");
    
    
    Label(inn,text="Enter Your Roll Number : ",font=16).grid(row=1,column=1,sticky=E,padx=50)
    e1=Entry(inn,width=25,font=16)
    e1.grid(row=1,column=2,padx=50,pady=30,sticky=W)
    
    Label(inn,text="Enter Your Name : ",font=16).grid(row=2,column=1,sticky=E,padx=50)
    e2=Entry(inn,width=25,font=16)
    e2.grid(row=2,column=2,padx=50,pady=30,sticky=W)
    
    Button(inn,text="Submit",font=16,command=partial(validName, e1,e2,inn)).grid(row=3,column=2,pady=30)
    
    inn.mainloop()
    

def main():

    Label(root,text="Welcome to Face Recogination Attendance System",font=26).grid(row=1,column=1,sticky=E,padx=100,pady=40)
    
    Button(root,text="Check Camera",font=15,command=camer).grid(row=2,column=1,pady=20)
    Button(root,text="Add Student",font=15,command=inName).grid(row=3,column=1,pady=20)
    Button(root,text="Train Data",font=15,command=TrainImages).grid(row=4,column=1,pady=20)
    Button(root,text="Take Attendance",font=15,command=recognize_attendence).grid(row=5,column=1,pady=20)
    Button(root,text="Mail Attendance",font=15,command=mailMe).grid(row=6,column=1,pady=20)
    
    root.mainloop()

    
    
login = tk.Tk(className="Login")
email=''
name='';
roll='';
username = StringVar()
loginpage(); 
root = tk.Tk(className="Main Page")  
main()    


