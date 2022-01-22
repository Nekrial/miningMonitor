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

class gpu:
    def __init__(self, deviceID, minerType, email, coreTemp, memTemp, powerMax, hotSpot, maxHash, minHash):
        self.deviceID = deviceID
        self.minerType = minerType
        self.email = email
        self.coreTemp =coreTemp
        self.memTemp =memTemp
        self.powerMax = powerMax
        self.hotSpot = hotSpot
        self.maxHash = maxHash
        self.minHash = minHash

    def checkCoreTemp(self):
        return
    def checkMemoryTemp(self):
        gpu = get_phys_gpu(self.deviceID)
        if gpu.vram_temp == None:
            return "No vram sensor to monitor"
            if gpu.vram_temp >= self.memTemp:
                print("Helllllooo")

            return gpu.vram_temp
    def notifyEmail(self,whatBroke):

        port = 465  # For SSL
        password = input(config.emailPassword)

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("miningmonitoremail@gmail.com", password)
            # TODO: Send email here

    @classmethod
    def from_json(cls,json_string):
        defaults = {
            "deviceID" : 99,
            "minerType" : "Excavator",
            "email" : "noone@noone.com",
            "coreTemp" : 80,
            "memTemp" : 110,
            "powerMax": 400,
            "hotSpot": 110,
            "maxHash": 150,
            "minHash": 1

        }
        jsonBeingWeird = eval(str(json_string))
        for k, v in jsonBeingWeird.items():
            if v is None:
                jsonBeingWeird[k] = defaults[k]
        return cls(**jsonBeingWeird)

    def __str__(self):
        return f"Device ID = {self.deviceID}, Miner Type = {self.minerType}, Email = {self.email}, Core Temp Max = {self.coreTemp}\n" \
               f"Max Memory Temp = {self.memTemp}, Power Max in Watts = {self.powerMax}, Max Hot Spot Temp = {self.hotSpot}, \n" \
               f"Max hashrate = {self.maxHash}, Minimum hashrate = {self.minHash}"

    def __repr__(self):
        return f"{self.deviceID}, {self.minerType}, {self.email}, {self.coreTemp}, {self.memTemp}, {self.powerMax}, {self.hotSpot}, {self.maxHash}, {self.minHash}"






def testConnection(incomingMinerType):
    if incomingMinerType == "Excavator":
        return is_HTTP_server_running('localhost', '4000')
    if incomingMinerType == "QuickMiner":
        return is_HTTP_server_running('localhost', '18000')

def testGpuConnection():
    deviceDict = {}
    variable = 0
    try:
        gpuInformation = requests.get('http://localhost:4000/api?command={"id":1,"method":"device.list","params":[]}', timeout=.1)
        for x in gpuInformation.json()['devices']:
            deviceDict[variable] = x
            variable += 1
        return gpuInformation.json()['devices']
    except ConnectionError:
        return "testGPUConnection Error"





def countGpus():
    count = 0
    gpuInformation = requests.get('http://localhost:4000/api?command={"id":1,"method":"device.list","params":[]}')
    for x in gpuInformation.json()['devices']:
        count += 1
    return count


def currentDeviceWithoutConfig():
    try:
        kappa = testGpuConnection()
        for x in kappa:
            with open(f"Configs/config{x['device_id']}.txt", 'r') as f:
                f.close()

    except IOError:
        return x['device_id'],x['name']

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
    print(configList)
    return(configList)

def montoring(incJson):
    deviceDict={}
    variable = 0
    gpuInformation=requests.get('http://localhost:4000/api?command={"id":1,"method":"device.list","params":[]}')
    for x in gpuInformation.json()['devices']:
        deviceDict[variable]=x
        variable +=1






def is_HTTP_server_running(host, port, just_GAE_devserver=False):
    conn = http.client.HTTPConnection(host, port)
    try:
        conn.request('HEAD', '/')
        return not just_GAE_devserver or \
               conn.getresponse().getheader('server')
    except (http.client.socket.error, http.client.HTTPException):
        return False
    finally:
        conn.close()

