def configVericaiton(incConfig):
    dictKeys = {"deviceID": 0, "minerType": "QuickMiner", "coreTemp": None, "memTemp": None, "powerMax": None, "hotSpot": None,
                "maxHash": None, "minHash": None, "sendEmail": 0, "restartMiner": 0, "shutdownSequence": 0, "email": ""}

    missingKeys = []

    for key in dictKeys:
        if key not in incConfig.keys():
            missingKeys.append(key)

