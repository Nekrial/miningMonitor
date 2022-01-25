import pynvraw
import requests
from requests import *
import http.client
import tkinter as tk
from tkinter import ttk
from tkinter import *
import json
from pynvraw import *
import smtplib, ssl
import config
from tkinter import messagebox
import signal
import psutil
import os
import subprocess


class gpu:
    def __init__(self, deviceID, minerType, coreTemp, memTemp, powerMax, hotSpot, maxHash, minHash, sendEmail=0,
                 restartMiner=0, shutdownSequence=0, email=None):
        self.deviceID = deviceID
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
        self.knownPort = queryKnownPorts()

    def limitExceeded(self, emailPreset):
        # This list will grow as we add more supported miners
        supportedMinerProcessDict = {
            "Excavator": "excavator.exe",
            "QuickMiner": "excavator.exe"
        }
        # Checking to see which of the protocols they are set to execute
        # This try block is to soley test the user inputted email and make exception parsing easier higher up in main

        if self.sendEmail == 1:
            self.notifyEmail(emailPreset)


        if self.restartMiner == 1:
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

    def checkMaxPower(self):
        gpu = get_phys_gpu(self.deviceID)
        currentPower = gpu.power

        if currentPower >= self.powerMax:
            emailPreset = (
                f"The current power draw of gpu {self.deviceID} is currently {currentPower}c\n"
                f"The max power draw you set me to monitor was {self.powerMax}\n"
                f"The device model is {gpu.name}")

            return self.limitExceeded(emailPreset)

    def hotSpotTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        currentTemp = gpu.hotspot_temp

        if currentTemp >= self.hotSpotTemp():
            emailPreset = (
                f"The current hotspot temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                f"The max how spot temp set me to monitor was {self.hotSpot}\n"
                f"The device model is {gpu.name}")

            return self.limitExceeded(emailPreset)

    def checkMemTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        currentTemp = gpu.vram_temp

        if currentTemp is not None and currentTemp >= self.memTemp:
            emailPreset = (
                f"The current memory temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                f"The max memory temp you set me to monitor was {self.memTemp}\n"
                f"The device model is {gpu.name}")

            return self.limitExceeded(emailPreset)

    def checkMaxHash(self):
        currentSpeed = getCurrentHashrate(self.minerType, self.deviceID)

        if int(str(currentSpeed)[:2]) > self.maxHash:
            emailPreset = (f"The hashrate of gpu {self.deviceID} is currently {currentSpeed}c\n"
                           f"The max hashrate you set me to monitor was {self.maxHash}")
            return self.limitExceeded(emailPreset)

    def checkMinHash(self):
        try:
            currentSpeed = getCurrentHashrate(self.minerType, self.deviceID)

            if int(str(currentSpeed)[:2]) <= self.minHash:
                emailPreset = (f"The hashrate of gpu {self.deviceID} is currently {currentSpeed}c\n"
                               f"The min hashrate you set me to monitor was {self.minHash}")
                return self.limitExceeded(emailPreset)
        except:
            print("hjey")

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
        return f"Device ID = {self.deviceID}, Miner Type = {self.minerType}, Email = {self.email}, Core Temp Max = {self.coreTemp}\n" \
               f"Max Memory Temp = {self.memTemp}, Power Max in Watts = {self.powerMax}, Max Hot Spot Temp = {self.hotSpot}, \n" \
               f"Max hashrate = {self.maxHash}, Minimum hashrate = {self.minHash}"

    def __repr__(self):
        return f"{self.deviceID}, {self.minerType}, {self.email}, {self.coreTemp}, {self.memTemp}, {self.powerMax}, {self.hotSpot}, {self.maxHash}, {self.minHash}"


def getCurrentHashrate(currentMiner, deviceID):
    if currentMiner == "Excavator":
        workerInformation = requests.get(
            'http://localhost:4000/api?command={"id":1,"method":"worker.list","params":[]}', timeout=.1)
        workerInformation = workerInformation.json()

        currentSpeed = workerInformation["workers"][deviceID]['algorithms'][0]['speed']

        return currentSpeed

    elif currentMiner == "QuickMiner":
        workerInformation = requests.get(
            'http://localhost:18000/api?command={"id":1,"method":"worker.list","params":[]}', timeout=.1)
        workerInformation = workerInformation.json()

        currentSpeed = workerInformation["workers"][deviceID]['algorithms'][0]['speed']

        return currentSpeed


def queryKnownPorts():
    # Pinging the Excavator default port
    if is_HTTP_server_running('localhost', '4000'):
        return 'http://localhost:4000/api?command={"id":1,"method":"device.list","params":[]}'

    # Pinging the quickminer port
    if is_HTTP_server_running('localhost', '18000'):
        return 'http://localhost:18000/api?command={"id":1,"method":"device.list","params":[]}'

# TODO break this shit and make it not use miner info
def testGpuConnection():
    deviceDict = {}
    # Gathering NVIDIA Gpus via pyvnraw
    gpuList = pynvraw.get_gpus()
    # If gpuList is empty then there are no supported nvidia gpus in the system
    if gpuList != "":
        for index, graphicsCard in enumerate(gpuList):
            deviceDict[index] = graphicsCard.name
        return deviceDict
    else:
        return "No gpu detected"


def countGpus():
    return len(get_gpus())

# Should be updated to use the new test connection
def currentDeviceWithoutConfig():
    try:
        kappa = testGpuConnection()
        for index, value in enumerate(kappa):
            # Testing which is the first card without a config
            with open(f"Configs/config{index}.txt", 'r') as f:
                f.close()
    except IOError:
        return index, value

# Should be updated to work with new test connection
def gatherConfigs():
    kappa = testGpuConnection()
    configList = {}
    for x in kappa:
        print(x)
        try:
            with open(f"Configs/config{x}.txt", 'r') as f:
                configList[x] = f"Configs/config{x}.txt"
        except IOError:
            continue
    return configList


def is_HTTP_server_running(host, port, just_GAE_devserver=False):
    conn = http.client.HTTPConnection(host, port, timeout=.01)
    try:
        conn.request('HEAD', '/')
        return not just_GAE_devserver or \
               conn.getresponse().getheader('server')
    except (http.client.socket.error, http.client.HTTPException):
        return False
    finally:
        conn.close()
