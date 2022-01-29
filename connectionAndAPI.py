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


def getCurrentHashrate(currentMiner, deviceID):
    if currentMiner == "Excavator" and is_HTTP_server_running('localhost', '4000'):
        workerInformation = requests.get(
            'http://localhost:4000/api?command={"id":1,"method":"worker.list","params":[]}', timeout=.1)
        workerInformation = workerInformation.json()

        currentSpeed = workerInformation["workers"][deviceID]['algorithms'][0]['speed']

        return currentSpeed

    elif currentMiner == "QuickMiner" and is_HTTP_server_running('localhost', '18000'):
        workerInformation = requests.get(
            'http://localhost:18000/api?command={"id":1,"method":"worker.list","params":[]}', timeout=.1)
        workerInformation = workerInformation.json()
        currentSpeed = workerInformation["workers"][deviceID]['algorithms'][0]['speed']

        return currentSpeed

    return "Miner not detected"


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
        return index, kappa[index]


# Should be updated to work with new test connection
def gatherConfigs():
    kappa = testGpuConnection()
    configList = {}
    for x in kappa:
        if path.exists(f"Configs/config{x}.txt"):
            configList[x] = f"Configs/config{x}.txt"

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
