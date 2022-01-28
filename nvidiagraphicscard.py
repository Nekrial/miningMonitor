import re

import pynvraw
import requests
from requests import *
import http.client
import json
from pynvraw import *
import smtplib, ssl
import config
from tkinter import messagebox
import signal
import psutil
import os
from os import path
from datetime import datetime
from connectionAndAPI import *
import re

class gpu:
    def __init__(self, deviceID, deviceName, minerType, coreTemp, memTemp, powerMax, hotSpot, maxHash, minHash, sendEmail=0,
                 restartMiner=0, shutdownSequence=0, email=None):
        self.deviceID = deviceID
        # Trimming the name down after the x as x is shared by both gtx and rtx. Makes displaying the name easier later
        self.deviceName = re.split("x",deviceName, flags=re.IGNORECASE)[1]
        self.minerType = minerType
        self.email = email
        self.coreTemp = coreTemp
        self.memTemp = memTemp
        self.powerMax = powerMax
        self.hotSpot = hotSpot
        self.maxHash = maxHash
        self.minHash = minHash
        self.sendEmail = sendEmail
        self.restartMiner = restartMiner
        self.shutdownSequence = shutdownSequence
        self.emailTimer = datetime.now()
        self.restartTimer = datetime.now()



    def timeDifference(self, incTime):
        exactTime = datetime.now()

        difference = (exactTime - incTime)

        return difference.total_seconds()


    def limitExceeded(self, emailPreset):
        # This list will grow as we add more supported miners
        supportedMinerProcessDict = {
            "Excavator": "excavator.exe",
            "QuickMiner": "excavator.exe"
        }
        # Checking to see which of the protocols they are set to execute
        try:
            if self.sendEmail == 1:
                timerDif = self.timeDifference(self.emailTimer)
                # This will only send them an email every 30 minutes instead of spamming them every 45 seconds
                if timerDif > 18000:
                    self.notifyEmail(emailPreset)
        except smtplib.SMTPRecipientsRefused:
            # Invalid email but one of the other two more important processes needs to be ran
            if self.restartMiner or self.shutdownSequence == 1:
                pass
            return "Email Error"

        if self.restartMiner == 1:
            timerDif = self.timeDifference(self.restartTimer)
            # This will only restart the miner once per minute else errors can build and cause gpus not to be detected
            if timerDif > 60:
                for proc in psutil.process_iter():
                    # check whether the process name matches. Possible exceptions
                    if proc.name() == supportedMinerProcessDict[self.minerType]:
                        proc.kill()
                        return "Miner kill attempted"
        # Not going to lie, I haven't tested this shutdown feature and I am just hoping it works. I don't want to restart
        if self.shutdownSequence == 1:
            os.system("shutdown /s /t 1")
            return "Shutdown Failed"

    def checkCoreTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        currentTemp = gpu.core_temp

        if currentTemp >= self.coreTemp:
            emailPreset = (f"The current core temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                           f"The max temp you set me to monitor was {self.coreTemp}\n"
                           f"The device model is {gpu.name}")
            return self.limitExceeded(emailPreset)

    def getCurrentCoreTemp(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        return str(int(graphicsCard.core_temp)) + "c"

    def checkMaxPower(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        currentPower = graphicsCard.power

        if currentPower >= self.powerMax:
            emailPreset = (
                f"The current power draw of gpu {self.deviceID} is currently {currentPower}c\n"
                f"The max power draw you set me to monitor was {self.powerMax}\n"
                f"The device model is {graphicsCard.name}")

            return self.limitExceeded(emailPreset)

    def getCurrentPowerDraw(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        # Casting as an int to remove decimals and then casting as a string to add c to the end for Celsius
        return str(int(graphicsCard.power)) + " watts"

    def hotSpotTemp(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        currentTemp = graphicsCard.hotspot_temp

        if currentTemp >= self.hotSpotTemp():
            emailPreset = (
                f"The current hotspot temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                f"The max how spot temp set me to monitor was {self.hotSpot}\n"
                f"The device model is {graphicsCard.name}")

            return self.limitExceeded(emailPreset)

    def getCurrentHotSpotTemp(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        # Casting as an int to remove decimals and then casting as a string to add c to the end for Celsius
        return str(int(graphicsCard.hotspot_temp)) + "c"

    def checkMemTemp(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        currentTemp = graphicsCard.vram_temp

        if currentTemp is not None and currentTemp >= self.memTemp:
            emailPreset = (
                f"The current memory temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                f"The max memory temp you set me to monitor was {self.memTemp}\n"
                f"The device model is {graphicsCard.name}")

            return self.limitExceeded(emailPreset)

    def getCurrentMemoryTemp(self):
        graphicsCard = get_phys_gpu(self.deviceID)
        currentTemp = graphicsCard.vram_temp
        if currentTemp is None:
            return "NA"
        # Casting as an int to remove decimals and then casting as a string to add c to the end for Celsius
        return str(int(currentTemp)) + "c"

    def checkMaxHash(self):
        currentSpeed = getCurrentHashrate(self.minerType, self.deviceID)
        # Error checking
        if currentSpeed =="Miner not detected":
            return "Miner not detected"
        if int(str(currentSpeed)[:2]) > self.maxHash:
            emailPreset = (f"The hashrate of gpu {self.deviceID} is currently {currentSpeed}c\n"
                           f"The max hashrate you set me to monitor was {self.maxHash}")
            return self.limitExceeded(emailPreset)
        # Current speed will either be a number or an error statement if the miner is not detected
        return currentSpeed

    def getCurrentHashrate(self):
        currentSpeed = getCurrentHashrate(self.minerType, self.deviceID)
        # Error checking
        if currentSpeed == "Miner not detected":
            return "Miner not detected"

        return str(int(currentSpeed)) + "mh/s"

    def checkMinHash(self):
        currentSpeed = getCurrentHashrate(self.minerType, self.deviceID)

        if currentSpeed =="Miner not detected":
            return "Miner not detected"

        if int(str(currentSpeed)[:2]) <= self.minHash:
            emailPreset = (f"The hashrate of gpu {self.deviceID} is currently {currentSpeed}c\n"
                           f"The min hashrate you set me to monitor was {self.minHash}")
            return self.limitExceeded(emailPreset)
        # Current speed will either be a number or an error statement if the miner is not detected
        return currentSpeed

    def notifyEmail(self, whatBroke):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "miningmonitoremail@gmail.com"  # Enter your address
        receiver_email = self.email  # Enter receiver address
        password = config.emailPassword
        message = whatBroke

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    # Object init method
    @classmethod
    def from_json(cls, json_string):
        defaults = {
            "deviceID": 99,
            "minerType": "Excavator",
            "email": "noone@noone.com",
            "coreTemp": 80,
            "memTemp": 110,
            "powerMax": 400,
            "hotSpot": 110,
            "maxHash": 150,
            "minHash": 1
        }
        json_string = str(json_string).replace("null", "None")
        jsonBeingWeird = eval(str(json_string))

        for k, v in jsonBeingWeird.items():
            if v == None:
                jsonBeingWeird[k] = defaults[k]
        return cls(**jsonBeingWeird)

    def __str__(self):
        return f"Device ID = {self.deviceID}, The device name is {self.deviceName}, Miner Type = {self.minerType}, Email = {self.email}, Core Temp Max = {self.coreTemp}\n" \
               f"Max Memory Temp = {self.memTemp}, Power Max in Watts = {self.powerMax}, Max Hot Spot Temp = {self.hotSpot}, \n" \
               f"Max hashrate = {self.maxHash}, Minimum hashrate = {self.minHash}"

    def __repr__(self):
        return f"{self.deviceID}, {self.minerType}, {self.email}, {self.coreTemp}, {self.memTemp}, {self.powerMax}, {self.hotSpot}, {self.maxHash}, {self.minHash}"
