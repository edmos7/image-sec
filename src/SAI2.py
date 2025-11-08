print("Attivo il Virtual Environment...")
import os
print("Importing Libraries...")
#Import Libraries
from ultralytics import YOLO
import cv2
import shutil
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
print("Controllo cartella images...")
opt = "/opt"
#Prendi immagini dalla cartella con tutte quelle scattate
curfold = (os.getcwd()+"/SAI2").replace('\\','/')#SAI2
if "toproc" in os.listdir(curfold):
    shutil.rmtree(curfold+"/toproc")
srcfolder = opt+"/images2"#path alla cartella opt/images2
imgs = os.listdir(srcfolder)#lista immagini
serv = ""
port = int()
user = ""
pw = ""
sender = user
receiver = user
#Se cartella immagini non vuota, avvia processing, sennò manda email di alert
if len(imgs) != 0:
    print("Cartella images non è vuota...")
    source = []
    for i in imgs:
        source.append(os.path.join(srcfolder,i).replace('\\','/'))

    #Ritaglia immagini
    print("Ritaglio Immagini...")
    os.makedirs(curfold+"/toproc")#smista tutte le immagini (post-crop) in un'altra cartella
    proc = curfold+"/toproc"
    def resize(dirs):
        c = 0
        for item in dirs:
            im = cv2.imread(item)
            h , w = im.shape[:2]
            croppedimg = im[ 40:h , 0:w ] #h first
            cv2.imwrite(proc+"/"+str(imgs[c]), croppedimg)
            c += 1
    resize(source)
    #Carica il modello
    print("Carico Modello...")
    model = YOLO("yolov8s.pt")
    #Prendi risultati
    print("Analizzo le immagini...")
    results = model.predict(source=proc,classes=[0,2],verbose=False)  

    print("Creo cartelle del giorno...")
    day = str(date.today())
    day = day.split("-")
    day0 = day[2]+"-"+day[1]+"-"+day[0]
    Ok = opt+"/archivio/ok/"+day0.replace("-","_")+"_2.0_"
    Ko = opt+"/archivio/ko/"+day0.replace("-","_")+"_2.0_"
    if day0.replace("-","_")+"_2.0_" not in os.listdir(opt+"/archivio/ok"):
        os.makedirs(Ok)
    else:
        shutil.rmtree(Ok)
        os.makedirs(Ok)
    if day0.replace("-","_")+"_2.0_" not in os.listdir(opt+"/archivio/ko"):
        os.makedirs(Ko)
    else:
        shutil.rmtree(Ko)
        os.makedirs(Ko)

    print("Smisto foto in Ok e Ko...")
    #Se macchina/persona trovata smista in OK sennò KO
    ps = os.listdir(proc)
    for i in range(len(ps)):
        obj = results[i].boxes.cls 
        if 0. in obj or 2. in obj :#0. is person class, 2. is car class
            shutil.copy(curfold+"/toproc/"+ps[i],Ok)
        else:
            shutil.copy(curfold+"/toproc/"+ps[i],Ko)

    #Send Emails(Ok,Ko,NoImgs function)

    def send():
        print("Invio mail...")
        if len(os.listdir(Ok)) != 0:#If Ok folder is not empty
            body = f"""
            Buongiorno,
            Sono state identificate macchine/persone
            In allegato le foto.
            """
            re = "Passaggio Effettuato - ImageSecurityAI_2.0 Report"
            
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = re

            
            msg.attach(MIMEText(body, 'plain'))

            pic = os.listdir(Ok)[0]#send first Ok image only
                
            filename = os.path.join(Ok,pic).replace("\\","/")

            attachment= open(filename, 'rb')

            attachment_package = MIMEBase('application', 'octet-stream')
            attachment_package.set_payload((attachment).read())
            encoders.encode_base64(attachment_package)
            attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
            msg.attach(attachment_package)

            text = msg.as_string()

            # Connect with the server
            print("Connecting to server...")
            ias_server = smtplib.SMTP(serv, port)
            ias_server.starttls()
            ias_server.login(user, pw)
            print("Succesfully connected to server")
            print()


            # Send emails to receiver
            print(f"Sending email to: {receiver}...")
            ias_server.sendmail(sender, receiver, text)
            print(f"Email sent to: {receiver}")
            print()

            # Close the port
            ias_server.quit()
        
    
        elif len(os.listdir(Ok))== 0:#If Ok folder is empty
            body = f"""
            Buongiorno,
            Non sono state identificate macchine/persone
            Per controllare di persona in caso di underperformance del modello, visita: address
            """
            cont = ssl.create_default_context()
            re = "Passaggio non Effettuato - ImageSecurityAI_2.0 Report"
            #MIME object to define parts of the email
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = re

            # Attach the body of the message
            msg.attach(MIMEText(body, 'plain'))

            text = msg.as_string()
            try:
                # Connect to the server
                print("Connecting to server...")
                ias_server = smtplib.SMTP(serv, port)
                ias_server.starttls(context=cont)
                ias_server.login(user, pw)
                print("Connected to server :-)")
                
                # Send the actual email
                print()
                print(f"Sending email to - {receiver}")
                ias_server.sendmail(sender, receiver, text)
                print(f"Email successfully sent to - {receiver}")

            # If there's an error, print it out
            except Exception as e:
                print(e)

            # Close the port
            finally:
                ias_server.quit()
    
    send()
        #Delete Ok/Ko folders(?)
    shutil.rmtree(proc)
    
else:#If imgs is empty
        print("Invio mail di alert...")
        body = f"""
        ALERT
        Buongiorno,
        Non è stata scattata nessuna foto,
        possibile malfunzionamento hardware.
        """
        cont = ssl.create_default_context()
        re = "ALERT - ImageSecurityAI_2.0"
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = re 
        msg.attach(MIMEText(body, 'plain'))

        msg = msg.as_string()

        try:
            # Connect to the server
            print("Connecting to server...")
            ias_server = smtplib.SMTP(serv, port)
            ias_server.starttls(context=cont)
            ias_server.login(user, pw)
            print("Connected to server :-)")
            
            # Send the actual email
            print()
            print(f"Sending email to - {receiver}")
            ias_server.sendmail(sender, receiver, msg)
            print(f"Email successfully sent to - {receiver}")

        # If there's an error, print it out
        except Exception as e:
            print(e)

        # Close the port
        finally:
            ias_server.quit()


       
print("Esco dal Virtual Environment...")


