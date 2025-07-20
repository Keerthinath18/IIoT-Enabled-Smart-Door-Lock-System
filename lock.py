import RPi.GPIO as GPIO
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import urllib.request
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from picamera import PiCamera
from time import sleep
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
# Initialize the display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)
# Set GPIO mode
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# GPIO setup
GPIO.setup(38, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)
GPIO.setup(15, GPIO.IN)
GPIO.setup(16, GPIO.IN)
password1 = "1234"
# Relay 2: pin 38
GPIO.output(38, 1)
print("Lock Closed")
count = 0
max_count = 5
counter = 0
a="3"
print("Option 1 Thingspeak")
print("Option 2 manual entry")
print("Option 3 MQTT")
a=input("enter your option")
# Display text with increased font size
def draw_text_with_font_size(draw, xy, text, font_path, font_size, fill="white"):
    font = ImageFont.truetype(font_path, font_size)
    draw.text(xy, text, font=font, fill=fill)
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    client.subscribe("ETS/IOTKIT/RELAY") # Subscribe Message
    print("SUBSCRIBED...")
    print("Enter Command")
# Function to get input with timeout
def get_input_with_timeout(prompt, timeout):
    print(prompt + " (You have", timeout, "seconds):")
    user_input = [None]

    def input_thread():
        user_input[0] = input()

    input_thread = threading.Thread(target=input_thread)
    input_thread.start()
    input_thread.join(timeout)

    if input_thread.is_alive():
        print("\nTime's up! Input skipped.")
        return None
    else:
        return user_input[0]

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    x=msg.payload.decode('utf-8')
    
    if x == '1234': 
        GPIO.output(38, 0)
        print("Lock Open")
        #time.sleep(5)
        #GPIO.output(38, 1)
        #print("Relay1 On")
        raise SystemExit

    
        

if a=="1":
    try:
        while True:
            
            if counter==3:
                camera = PiCamera()
                # Email and SMTP configuration
                sender_email = "kaadarshritul@gmail.com"
                receiver_email = "126015044@sastra.ac.in"
                password = "eoxv zehf ogsm twgb"  # Replace with your application-specific password
                # Create a multipart message
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = "Test Mail with Image"

                # Add body to email
                message.attach(MIMEText("Intruder Entry", "plain"))
                camera.start_preview()
                #camera.annotate_text = "Hello world!"
                sleep(5)
                camera.capture('/home/pi/Desktop/text3.jpg')
                camera.stop_preview()
                camera.close()
                # Open and attach the image file
                with open(r'/home/pi/Desktop/text3.jpg', "rb") as attachment:
                    image_part = MIMEImage(attachment.read(), "jpg")
                    image_part.add_header("Content-Disposition", "attachment", filename="image.jpg")
                    message.attach(image_part)

                # Connect to SMTP server and send email
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.send_message(message)

                print("Mail with image sent successfully!")
                
                    
            if counter==5:
                GPIO.output(37, GPIO.HIGH)
                print("BUZZER ON")
                time.sleep(3)  # 3-second time delay
                GPIO.output(37, GPIO.LOW)
                print("BUZZER OFF")
                time.sleep(1)
                break
            if count == 0:
                print("The room is empty")
                with canvas(device) as draw:
                    # Specify the font size
                    font_size = 16
                    # Specify the path to the font file
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                    draw_text_with_font_size(draw, (0, 0), "The room", font_path, font_size)
                    draw_text_with_font_size(draw, (0, 20), "is empty", font_path, font_size)        
        
        
            if count == max_count:
                print("Room is full")
                with canvas(device) as draw:
                    # Specify the font size
                    font_size = 16
                    # Specify the path to the font file
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                    draw_text_with_font_size(draw, (0, 0), "The room", font_path, font_size)
                    draw_text_with_font_size(draw, (0, 20), "is full", font_path, font_size)        
        
            if GPIO.input(16) == GPIO.HIGH and count != 0:
                count -= 1
                publish.single("ETS/IOTKIT/up/SHAK2", str(count), hostname="test.mosquitto.org")
                print(count)
                
            with canvas(device) as draw:
                font_size = 16
                # Specify the path to the font file
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                # Draw text with specified font siz
                draw_text_with_font_size(draw, (0, 0), "Enter your", font_path, font_size)
                draw_text_with_font_size(draw, (0, 20), "password", font_path, font_size)
                draw_text_with_font_size(draw, (0, 40), "in 5 seconds", font_path, font_size)
            
            request = urllib.request.urlopen('https://api.thingspeak.com/talkbacks/52000/commands/execute?api_key=TVUO5266DK2KXYFE')
            time.sleep(8)
            command = request.read().decode()
            if command == '1234' and GPIO.input(15) == GPIO.HIGH and count<5:
                counter=0
                device.clear()
                with canvas(device) as draw:
                    
                    font_size = 16
                # Specify the path to the font file
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                # Draw text with specified font siz
                    draw_text_with_font_size(draw, (0, 0), "Correct", font_path, font_size)
                    draw_text_with_font_size(draw, (0, 20), "password", font_path, font_size)
                    
                publish.single("ETS/IOTKIT/up/SHAK1", "Lock Open", hostname="test.mosquitto.org")
                count += 1
                publish.single("ETS/IOTKIT/up/SHAK2", str(count), hostname="test.mosquitto.org")
                print(count)
                GPIO.output(38, 0)
                print("Lock Open")
                time.sleep(2)
                GPIO.output(38, 1)
                print("Lock Closed")
                publish.single("ETS/IOTKIT/up/SHAK1", "Lock Closed", hostname="test.mosquitto.org")

                    
            elif command!="1234" and GPIO.input(15)==GPIO.HIGH:
                counter+=1
                if(counter!=4):
                    with canvas(device) as draw:
                        # Specify the font size
                        font_size = 16
                        # Specify the path to the font file

                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                        draw_text_with_font_size(draw, (0, 0), "Wrong", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 20), "password", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 40), "Attempt "+str(counter), font_path, font_size)
                elif counter==5:
                    with canvas(device) as draw:
                        # Specify the font size
                        font_size = 16
                        # Specify the path to the font file

                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                        draw_text_with_font_size(draw, (0, 0), "No more", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 20), "remaining", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 40), "attempts ", font_path, font_size)

                else:
                    with canvas(device) as draw:
                        # Specify the font size
                        font_size = 16
                        # Specify the path to the font file

                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                        draw_text_with_font_size(draw, (0, 0), "Buzzer", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 20), "Alert", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 40), "Last Attempt ", font_path, font_size)
                        

                    
            time.sleep(2)
    except KeyboardInterrupt:
            # Ctrl+C and stop the program
            GPIO.output(38, 0)
    
        

        
elif a=="2":
    try:
        while True:
            if counter==3:
                camera = PiCamera()
                # Email and SMTP configuration
                sender_email = "kaadarshritul@gmail.com"
                receiver_email = "126015044@sastra.ac.in"
                password = "eoxv zehf ogsm twgb"  # Replace with your application-specific password
                # Create a multipart message
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = "Test Mail with Image"

                # Add body to email
                message.attach(MIMEText("Intruder Entry", "plain"))
                camera.start_preview()
                #camera.annotate_text = "Hello world!"
                sleep(5)
                camera.capture('/home/pi/Desktop/text3.jpg')
                camera.stop_preview()
                camera.close()
                # Open and attach the image file
                with open(r'/home/pi/Desktop/text3.jpg', "rb") as attachment:
                    image_part = MIMEImage(attachment.read(), "jpg")
                    image_part.add_header("Content-Disposition", "attachment", filename="image.jpg")
                    message.attach(image_part)

                # Connect to SMTP server and send email
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.send_message(message)

                print("Mail with image sent successfully!")   
                    
            if counter==5:
                GPIO.output(37, GPIO.HIGH)
                print("BUZZER ON")
                time.sleep(3)  # 3-second time delay
                GPIO.output(37, GPIO.LOW)
                print("BUZZER OFF")
                time.sleep(1)
                break
            if count == 0:
                print("The room is empty")
                with canvas(device) as draw:
                    # Specify the font size
                    font_size = 16
                    # Specify the path to the font file
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                    draw_text_with_font_size(draw, (0, 0), "The room", font_path, font_size)
                    draw_text_with_font_size(draw, (0, 20), "is empty", font_path, font_size)
            if count == max_count:
                print("Room is full")
                with canvas(device) as draw:
                    # Specify the font size
                    font_size = 16
                    # Specify the path to the font file
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                    draw_text_with_font_size(draw, (0, 0), "The room", font_path, font_size)
                    draw_text_with_font_size(draw, (0, 20), "is full", font_path, font_size)        
        
            if GPIO.input(16) == GPIO.HIGH and count != 0:
                count -= 1
                device.clear()
                publish.single("ETS/IOTKIT/up/SHAK2", str(count), hostname="test.mosquitto.org")
                print(count)
            with canvas(device) as draw:
                font_size = 16
                # Specify the path to the font file
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                # Draw text with specified font siz
                draw_text_with_font_size(draw, (0, 0), "Enter your", font_path, font_size)
                draw_text_with_font_size(draw, (0, 20), "password", font_path, font_size)
                draw_text_with_font_size(draw, (0, 40), "in 5 seconds", font_path, font_size)

            password = get_input_with_timeout("Enter your password", 5)  # Set the timeout for password input (in seconds)
            if password == password1 and GPIO.input(15) == GPIO.HIGH and count < max_count:
               device.clear()
               with canvas(device) as draw:
                              
                   font_size = 16
                # Specify the path to the font file
                   font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                # Draw text with specified font siz
                   draw_text_with_font_size(draw, (0, 0), "Correct", font_path, font_size)
                   draw_text_with_font_size(draw, (0, 20), "password", font_path, font_size)
                 
               publish.single("ETS/IOTKIT/up/SHAK1", "Lock Open", hostname="test.mosquitto.org")
               counter=0
               count += 1
               publish.single("ETS/IOTKIT/up/SHAK2", str(count), hostname="test.mosquitto.org")
               print(count)
               GPIO.output(38, 0)
               print("Relay2 OFF")
               time.sleep(2)
               GPIO.output(38, 1)
               print("Relay2 ON")
               publish.single("ETS/IOTKIT/up/SHAK1", "Lock Closed", hostname="test.mosquitto.org")
            else:
                counter+=1
                if(counter!=4):
                    with canvas(device) as draw:
                        # Specify the font size
                        font_size = 16
                        # Specify the path to the font file

                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                        draw_text_with_font_size(draw, (0, 0), "Wrong", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 20), "password", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 40), "Attempt "+str(counter), font_path, font_size)
                elif counter==5:
                    with canvas(device) as draw:
                        # Specify the font size
                        font_size = 16
                        # Specify the path to the font file

                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                        draw_text_with_font_size(draw, (0, 0), "No more", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 20), "remaining", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 40), "attempts ", font_path, font_size)

                else:
                    with canvas(device) as draw:
                        # Specify the font size
                        font_size = 16
                        # Specify the path to the font file

                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path accordingly
                        # Draw text with specified font size
                    
                        draw_text_with_font_size(draw, (0, 0), "Buzzer", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 20), "Alert", font_path, font_size)
                        draw_text_with_font_size(draw, (0, 40), "Last Attempt ", font_path, font_size)
                        

            time.sleep(2)
    except KeyboardInterrupt:
            # Ctrl+C and stop the program
            GPIO.output(38, 0)
else:
    try:
        while True:
            
         
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect("test.mosquitto.org", 1883, 60)          
            client.loop_forever()
            
           
            
        time.sleep(2)


            
    except KeyboardInterrupt:
            # Ctrl+C and stop the program
            GPIO.output(38, 1)
                            
        
        
