from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import sys
import imutils
from PIL import Image
import os
import pygame

from neopixel import *
import _rpi_ws281x as ws

# import tweepy

pygame.init()
screen = pygame.display.set_mode((1280,800), pygame.FULLSCREEN)

# aauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# aauth.set_access_token(access_token, access_token_secret)

# api = tweepy.API(auth)

# LED strip configuration:
LED_COUNT      = 31      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = True   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

STATE_IDLE = 0
STATE_HEARTGROW = 1
STATE_TAKEPHOTO = 2
STATE_SPARKLE = 3
STATE_HEARTSHRINK = 4

def colourFill(strip, colour):
    for i in range(strip.numPixels()):
	strip.setPixelColor(i, colour)
    strip.show()

def sparkleHeart(strip, heartColour, sparkleColour, counter):
    for i in range(strip.numPixels()):
        if(i % 8 == counter):
            strip.setPixelColor(i, sparkleColour)
        else:
            strip.setPixelColor(i, heartColour)
    strip.show()

def fillInHeart(strip, colour, counter):
    for i in range(strip.numPixels()):
        if(i <= counter):
            strip.setPixelColor(i, colour)
        elif(i >= (strip.numPixels() - counter)):
            strip.setPixelColor(i, colour)
        else:
            strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

currentState = STATE_IDLE

heartCounter = 0
sparkleCounter = 0

# Adapt to your needs

# Get user supplied values
cascPath = "lbpcascade_frontalface.xml"
#cascPath = "haarcascade_frontalface_default.xml"

# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320, 240))

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

# allow the camera to warmup
time.sleep(0.1)
lastTime = time.time()*1000.0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imagePrint = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
    flags = cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    print time.time()*1000.0-lastTime," Found {0} faces!".format(len(faces))
    lastTime = time.time()*1000.0
    # Draw a rectangle around the faces
    #for (x, y, w, h) in faces:
    #    cv2.circle(image, (x+w/2, y+h/2), int((w+h)/3), (255, 255, 255), 1)
    # show the frame
    # cv2.imshow("Frame", image)
    # key = cv2.waitKey(1) & 0xFF
 
    numFaces = len(faces)

    if(currentState == STATE_IDLE):
        # LEDs are clear
        colourFill(strip, Color(0,0,0))
        print("State IDLE")

        if(numFaces >= 2):
            currentState = STATE_HEARTGROW

    elif(currentState == STATE_HEARTGROW):
        # run the animation
        fillInHeart(strip, Color(255,0,127), heartCounter)
        heartCounter = heartCounter + 4
        print("State HEARTGROW")

        if(heartCounter >= 16):
            currentState = STATE_TAKEPHOTO
        elif(numFaces < 2):
            currentState = STATE_HEARTSHRINK

    elif(currentState == STATE_HEARTSHRINK):
        # run the animation
        fillInHeart(strip, Color(255,0,127), heartCounter)
        heartCounter = heartCounter - 4

        print("State HEARTSHRINK")

        if(heartCounter <= 0):
            currentState = STATE_IDLE
        elif(numFaces >= 2):
            currentState = STATE_HEARTGROW

    elif(currentState == STATE_TAKEPHOTO):
        # take a photo
        print("State TAKEPHOTO")

        printImage = Image.fromarray(imagePrint)
        
        i = 0

        while os.path.exists("photos/love_photo_%s.jpg" % i):
            i += 1

        printImage.save("photos/love_photo_%s.jpg" % i)

        statusMessage = "Two faces detected!"

        # api.update_with_media("photos/love_photo_%s.jpg" % i, statusMessage)

        picture = pygame.image.load("photos/love_photo_%s.jpg" % i)
        picture = pygame.transform.scale(picture, (1280,800))
        rect = picture.get_rect()
        rect = rect.move((0,0))
        screen.blit(picture, (0,0))
        pygame.display.update()

        currentState = STATE_SPARKLE

    elif(currentState == STATE_SPARKLE):
        # sparkly things!
        print("State SPARKLE")
        sparkleHeart(strip, Color(255, 0, 127), Color(127,0,255), sparkleCounter)
        sparkleCounter = sparkleCounter + 1
        if(sparkleCounter > 7):
            sparkleCounter = 0

        if(numFaces < 2):
            currentState = STATE_HEARTSHRINK

    else:
        currentState = STATE_IDLE



	# clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    
	# if the `q` key was pressed, break from the loop
    #if key == ord("q"):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()
        
  
        

