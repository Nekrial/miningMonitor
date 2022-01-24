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


class gpu:
    def __init__(self, deviceID, minerType, email, coreTemp, memTemp, powerMax, hotSpot, maxHash, minHash):
        self.deviceID = deviceID
        self.minerType = minerType
        self.email = email
        self.coreTemp = coreTemp
        self.memTemp = memTemp
        self.powerMax = powerMax
        self.hotSpot = hotSpot
        self.maxHash = maxHash
        self.minHash = minHash
        self.knownPort = queryKnownPorts()

    def checkCoreTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        currentTemp = gpu.core_temp

        if currentTemp >= self.coreTemp:
            emailCheck = self.notifyEmail(f"The current core temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                                          f"The max temp you set me to monitor was {self.coreTemp}\n"
                                          f"The device model is {gpu.name}")

            return emailCheck

    def checkMaxPower(self):
        gpu = get_phys_gpu(self.deviceID)
        currentPower = gpu.power

        if currentPower >= self.coreTemp:

            emailCheck = self.notifyEmail(
                f"The current power draw of gpu {self.deviceID} is currently {currentPower}c\n"
                f"The max power draw you set me to monitor was {self.powerMax}\n"
                f"The device model is {gpu.name}")

            return emailCheck

    def hotSpotTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        currentTemp = gpu.hotspot_temp

        if currentTemp >= self.hotSpotTemp():

            emailCheck = self.notifyEmail(
                f"The current hotspot temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                f"The max how spot temp set me to monitor was {self.hotSpot}\n"
                f"The device model is {gpu.name}")
            return emailCheck

    def checkMemTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        currentTemp = gpu.vram_temp

        if currentTemp != None and currentTemp >= self.memTemp:
            emailCheck = self.notifyEmail(
                f"The current memory temp of gpu {self.deviceID} is currently {currentTemp}c\n"
                f"The max memory temp you set me to monitor was {self.memTemp}\n"
                f"The device model is {gpu.name}")

            return emailCheck

    def checkMaxHash(self):
        workerInformation = requests.get(
            'http://localhost:4000/api?command={"id":1,"method":"worker.list","params":[]}', timeout=.1)
        workerInformation = workerInformation.json()

        currentSpeed = workerInformation["workers"][self.deviceID]['algorithms'][0]['speed']

        if int(str(currentSpeed)[:2]) > self.maxHash:
            emailCheck = self.notifyEmail(f"The hashrate of gpu {self.deviceID} is currently {currentSpeed}c\n"
                                          f"The max hashrate you set me to monitor was {self.maxHash}")
            return emailCheck

    def checkMinHash(self):
        workerInformation = requests.get(
            'http://localhost:4000/api?command={"id":1,"method":"worker.list","params":[]}', timeout=.1)
        workerInformation = workerInformation.json()

        currentSpeed = workerInformation["workers"][self.deviceID]['algorithms'][0]['speed']
        if int(str(currentSpeed)[:2]) <= self.minHash:
            emailCheck = self.notifyEmail(f"The hashrate of gpu {self.deviceID} is currently {currentSpeed}c\n"
                                          f"The min hashrate you set me to monitor was {self.minHash}")

            return emailCheck

    def notifyEmail(self, whatBroke):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "miningmonitoremail@gmail.com"  # Enter your address
        receiver_email = self.email  # Enter receiver address
        password = config.emailPassword
        message = whatBroke
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
        except smtplib.SMTPRecipientsRefused:
            raise Exception("Please reset the profiles and add a valid email")

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


def queryKnownPorts():
    # Pinging the Excavator default port
    if is_HTTP_server_running('localhost', '4000'):
        return 'http://localhost:4000/api?command={"id":1,"method":"device.list","params":[]}'

    # Pinging the quickminer port
    if is_HTTP_server_running('localhost', '18000'):
        return 'http://localhost:18000/api?command={"id":1,"method":"device.list","params":[]}'


def testGpuConnection():
    deviceDict = {}
    variable = 0

    try:
        gpuInformation = requests.get(queryKnownPorts(),
                                      timeout=.1)
        for x in gpuInformation.json()['devices']:
            deviceDict[variable] = x
            variable += 1
        return gpuInformation.json()['devices']
    except ConnectionError:
        return


def countGpus():
    return len(get_gpus())


def currentDeviceWithoutConfig():
    try:
        kappa = testGpuConnection()
        for x in kappa:
            with open(f"Configs/config{x['device_id']}.txt", 'r') as f:
                f.close()
    except IOError:
        return x['device_id'], x['name']


def gatherConfigs():
    kappa = testGpuConnection()
    configList = []
    for x in kappa:
        try:
            with open(f"Configs/config{x['device_id']}.txt", 'r') as f:
                configList.append(f"Configs/config{x['device_id']}.txt")
                f.close()
        except IOError:
            continue
    return (configList)


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
