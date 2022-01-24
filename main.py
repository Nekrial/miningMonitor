import tkinter as tk
from tkinter import ttk
from tkinter import *
import json
from tkinter import messagebox
import itertools
import requests
from requests import *
import connectionAndAPI
from connectionAndAPI import *
import os
from configValidation import *
import configValidation


gpuList=[]
class createApp(tk.Tk):


    def __init__(self):
        global gpuList
        tk.Tk.__init__(self)
        self._frame = None
        def resetAll(incQuit):
            dir = 'Configs'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))


        kappa = connectionAndAPI.testGpuConnection()
        if kappa == "testGPUConnection Error":
            tk.Label(self,
                     text="I cannot connect to any NVIDIA GPUs. Please start the miner before you start this monitoring program\n "
                          "Please note- Only NVIDIA Gpus are supported at this time\n"
                          "Resetting your profiles for each card may solve the issue").pack(
                fill="x", pady=10)
            tk.Button(self, text="Reset Profiles and restart program", command=lambda:resetAll(1)).pack()
        else:
            # Quick os call to make the configs directory if it does not already exist
            if not os.path.exists('Configs'):
                os.mkdir('Configs')
                # Main loop for reading configs
            for x in kappa:
                try:
                    with open(f"Configs/config{x['device_id']}.txt", 'r') as f:
                        json_object = json.load(f)
                        # This is in the event that the config does not contain
                        configValidation.configVericaiton(json_object)
                        gpuList.append(connectionAndAPI.gpu.from_json(json_object))

                except IOError:
                    self.switch_frame(StartPage)

        if len(gpuList) == len(testGpuConnection()):
            self.switch_frame(monitoringFrame)







    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


class StartPage(tk.Frame):
    def __init__(self, master):

        tk.Frame.__init__(self, master)
        nextDevice = connectionAndAPI.currentDeviceWithoutConfig()
        if nextDevice != None:
            master.title("Start Up Page")
            tk.Label(self,
                     text=f'This is the setup for GPU number {nextDevice[0] + 1} which is a {nextDevice[1]}').grid()
            tk.Label(self, text="What miner are you using?").grid()
            tk.Button(self, text="QuickMiner",
                      command=lambda: [setattr(app, "minerType", "QuickMiner"),
                                       master.switch_frame(VariableSelection)]).grid()
            tk.Button(self, text="Excavator",
                      command=lambda: [setattr(app, "minerType", "Excavator"),
                                       master.switch_frame(VariableSelection)]).grid()
        else:
            master.switch_frame(monitoringFrame)


class VariableSelection(tk.Frame):

    def __init__(self, master):
        global gpuList
        tk.Frame.__init__(self, master, width=300, height=350)
        self.frame = tk.Frame(self)
        master.title("Variable Selection Page")
        # Checkbox Variables
        coreTempCheckVariable = tk.IntVar(value=0)

        gddrTempCheckboxVariable = tk.IntVar(value=0)

        gpuPowerCheckboxVar = tk.IntVar(value=0)

        hotSpotTempCheckboxVar = tk.IntVar(value=0)

        maxHashrateCheckboxVar = tk.IntVar(value=0)

        minHashrateCheckboxVar = tk.IntVar(value=0)

        # Getters


        # this is a function to get the user input from the text input box
        def getCoreTempInputBoxValue():

            if coreTempInput.cget('state') == "normal":
                userInput = coreTempInput.get()

                if userInput.isdigit():
                    userInput = int(userInput)
                    return userInput

                messagebox.showerror(title="Invalid Core Temp Input",
                                    message="Please input a numerical Max Core Temperature")



        # this is a function to get the user input from the text input box
        def getGDDRInputBoxValue():

            userInput = gddrInput.get()
            if gddrInput.cget('state') == "normal":

                if userInput.isdigit():
                    userInput = int(userInput)
                    return userInput

                messagebox.showerror(title="Invalid Memory Temp Input",
                                     message="Please input a numerical Max GDDR6X Temperature")


        # this is a function to get the user input from the text input box
        def getPowerInputBoxValue():
            userInput = gpuPowerInput.get()
            if gpuPowerInput.cget('state') == "normal":

                if userInput.isdigit():
                    userInput = int(userInput)
                    return userInput

                messagebox.showerror(title="Invalid Max Power Input",
                                     message="Please input a numerical Max Power in Watts")


        # this is a function to get the user input from the text input box
        def getHotSpotInputBoxValue():
            userInput = hotSpotTempInput.get()
            if hotSpotTempInput.cget('state') == "normal":
                if userInput.isdigit():
                    userInput = int(userInput)
                    return userInput

                messagebox.showerror(title="Invalid Hot Spot Temp Input",
                                     message="Please input a numerical Max Hot Spot Temperature")


        def getMaxHashrateInputBoxValue():
            userInput = maxHashrateInput.get()

            if maxHashrateInput.cget('state') == "normal":
                if userInput.isdigit():
                    userInput = int(userInput)
                    return userInput

                messagebox.showerror(title="Invalid Max Hashrate",
                                     message="Please input a numerical max hashrate")


        def getMinHashrateInputBoxValue():
            userInput = minHashrateInput.get()
            if minHashrateInput.cget('state') == "normal":
                if userInput.isdigit():
                    userInput = int(userInput)
                    return userInput

                messagebox.showerror(title="Invalid Min Hashrate",
                                     message="Please input a numerical minimum hashrate")


        def getAllAndCheck():

            nextDevice = connectionAndAPI.currentDeviceWithoutConfig()

            dict = {"deviceID": nextDevice[0],

                    "minerType": app.minerType,

                    "coreTemp": getCoreTempInputBoxValue(),

                    "memTemp": getGDDRInputBoxValue(),

                    "powerMax": getPowerInputBoxValue(),

                    "hotSpot": getHotSpotInputBoxValue(),

                    "maxHash": getMaxHashrateInputBoxValue(),

                    "minHash": getMinHashrateInputBoxValue(),
                    }


            commandsDict = {
                0: lambda: None,
                1: lambda: None,
                2: lambda: coreTempCheckVariable.get(),
                3: lambda: gddrTempCheckboxVariable.get(),
                4: lambda: gpuPowerCheckboxVar.get(),
                5: lambda: hotSpotTempCheckboxVar.get(),
                6: lambda: maxHashrateCheckboxVar.get(),
                7: lambda: minHashrateCheckboxVar.get(),
            }
            json_object = json.dumps(dict)

            # This look checks if any check box is ticked but does not have a value in it. This also allows the error message
            #  to appear properly and not reset the users already inputted data
            for index, value in enumerate(dict.values()):
                if value is None and commandsDict[index]() == 1:
                    return



            # The break cases where the data should not be sent to further processing
            if dict["minerType"] is None:

                return
            else:

                if nextDevice is not None:
                    with open(f"Configs/config{nextDevice[0]}.txt", "w+") as outfile:
                        outfile.write(json_object)
                        gpuList.append(connectionAndAPI.gpu.from_json(json_object))
                        
                        if len(connectionAndAPI.gatherConfigs()) != connectionAndAPI.countGpus():
                            app.switch_frame(StartPage)

                        else:
                            app.switch_frame(restartCheck)
                else:
                    print("fuck")

        # This just clears the text from the input box when clicked
        def on_click(event):
            event.widget.delete(0, tk.END)

        # Making the monitor label
        Label(self, text='What would you like me to monitor?', font=('arial', 13, 'normal')).place(x=12, y=30)
        # core temp input and checkbox block
        coreTempInput = Entry(self, width=20, )
        coreTempInput.bind("<Button-1>", on_click)
        coreTempInput.configure(state="disabled")

        CoreTempCheck = Checkbutton(self, onvalue=1, offvalue=0, text='Core Temp', variable=coreTempCheckVariable,
                                    font=('arial', 8, 'normal'),
                                    command=lambda: [show_entry(coreTempCheckVariable, coreTempInput, 103 ,100),
                                                     coreTempInput.insert(tk.END, "Enter Max Core Temp")
                                                     ])
        CoreTempCheck.place(x=9, y=97)
        # end core temp block

        # Gddr6x input block
        gddrInput = Entry(self, width=20)
        gddrInput.bind("<Button-1>", on_click)
        gddrInput.configure(state="disabled")
        # This is the section of code which creates a checkbox
        gddrTempCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='GDDR6X Temp',
                                       variable=gddrTempCheckboxVariable,
                                       command=lambda: [show_entry(gddrTempCheckboxVariable, gddrInput, 121, 134),
                                                        gddrInput.insert(tk.END, "Enter Max Memory Temp")])
        gddrTempCheckbox.place(x=9, y=131)
        # end gddr block

        # Power input block
        gpuPowerInput = Entry(self, width=21)
        gpuPowerInput.bind("<Button-1>", on_click)
        gpuPowerInput.configure(state="disabled")
        gpuPowerCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Gpu Power Draw', variable=gpuPowerCheckboxVar,
                                       command=lambda: [show_entry(gpuPowerCheckboxVar, gpuPowerInput,134, 170),
                                                        gpuPowerInput.insert(tk.END, "Enter Max Power(Watts)")])
        gpuPowerCheckbox.place(x=9, y=167)
        # End gpu power input block

        # hotspot block
        hotSpotTempInput = Entry(self, width=20)
        hotSpotTempInput.bind("<Button-1>", on_click)
        hotSpotTempInput.configure(state="disabled")

        hotSpotTempCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Hot Spot Temp',
                                          variable=hotSpotTempCheckboxVar,
                                          command=lambda: [show_entry(hotSpotTempCheckboxVar, hotSpotTempInput, 126, 201),
                                                           hotSpotTempInput.insert(tk.END, "Enter Max Hot Spot")])
        hotSpotTempCheckbox.place(x=9, y=198)

        # Max Hashrate block
        maxHashrateInput = Entry(self, width=20)
        maxHashrateInput.bind("<Button-1>", on_click)
        maxHashrateInput.configure(state="disabled")

        maxHashrateCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Max Hashrate',
                                          variable=maxHashrateCheckboxVar,
                                          command=lambda: [show_entry(maxHashrateCheckboxVar, maxHashrateInput,126, 230),
                                                           maxHashrateInput.insert(tk.END, "Enter Max Hashrate")])
        maxHashrateCheckbox.place(x=9, y=227)

        # Min Hashrate block
        minHashrateInput = Entry(self, width=25)
        minHashrateInput.bind("<Button-1>", on_click)
        minHashrateInput.configure(state="disabled")

        minHashrateCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Minimum Hashrate',
                                          variable=minHashrateCheckboxVar,
                                          command=lambda: [show_entry(minHashrateCheckboxVar, minHashrateInput, 140, 260),
                                                           minHashrateInput.insert(tk.END, "Enter Min Hashrate")])
        minHashrateCheckbox.place(x=9, y=257)

        # This is the section of code which creates a button
        Button(self, text='Continue', bg='#F0F8FF', font=('arial', 8, 'normal'), command=lambda: getAllAndCheck(
        )).place(x=101, y=300)

# Places or unplaces the input box based on the checkbox value
# Placing it out here so that multiple classes may use it
def show_entry(var, widget, incX, incY):

    if var.get() == 1:

        # Clean up line and function. The if statement is to check if it is a label or a textbox as we do not want to delete text of a label
        if type(widget)== "<class 'tkinter.Entry'>":
            widget.delete(0, tk.END)
        widget.configure(state="normal")
        widget.place(x=incX, y=incY)
    else:
        widget.configure(state="disabled")
        widget.place_forget()


class restartCheck(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, width=300, height=350)
        self.frame = tk.Frame(self)
        master.title("Final Checks")

        def getEmailInputBoxValue():
            userInput = emailInputBox.get()
            if userInput == "" and sendEmailCheckBox.get() == 1:
                messagebox.showerror(title="Invalid Email Input",
                                     message="Please input a email so that we can notify you when an error occurs.")
                return ""
            else:
                return userInput

        # Creating the checkbox variables
        sendEmailCheckBox = tk.IntVar(value=0)

        restartMinerCheckbox = tk.IntVar(value=0)

        shutDownComputer = tk.IntVar(value=0)

        valueArray= [sendEmailCheckBox,restartMinerCheckbox,shutDownComputer]

        commandsDict = {
            0: lambda:[show_entry(valueArray[0], emailInputLable,9,200),show_entry(valueArray[0], emailInputBox, 9, 230)],
            1: None,
            2: None
        }
        whatDoText = [
            "Send me an email",
            "Restart the miner",
            "Shutdown the computer"
        ]

        yVar = 97

        Label(self, text='If something goes wrong with a GPU\n'
                         ' what would you like me to do?', font=('arial', 12, 'normal')).place(x=25, y=30)

        for index, name in enumerate(whatDoText):
            # Generating the checkboxes
            x = Checkbutton(self, onvalue=1, offvalue=0, text=whatDoText[index], variable=valueArray[index],
                                        font=('arial', 8, 'normal'), command =commandsDict[index])
            x.place(x=9, y=yVar)
            yVar += 30
        # This is the section of code which creates the a label
        emailInputLable = Label(self, text='What email would you like to be notified at?',
              font=('arial', 10, 'normal'))
        emailInputBox = Entry(self, width=40)

        # This is the section of code which creates a text input box


        # This is the section of code which creates a button
        Button(self, text='Begin Monitoring', bg='#F0F8FF', font=('arial', 8, 'normal'), command=lambda: getAllAndProcess(valueArray
        )).place(x=101, y=300)
        #def show_entry(var, widget, incX, incY):



        def getAllAndProcess(valueArray):
            # preparing values for json integration

            selectionDict = {
                'sendEmail' : valueArray[0].get(),
                'restartMiner' : valueArray[1].get(),
                'shutdownSequence' : valueArray[2].get()
            }

            # The break case if everything is null and nothing is selected
            if sum(selectionDict.values())==0:
                messagebox.showerror(title="No options selected",
                                     message="Please select at least one of the options")
            #     To break out of the submission if the email box is selected but no email is input
            elif getEmailInputBoxValue() == '' and valueArray[0].get() == 1 :

                return
            else:
                # Appending each config file with the variables of what to do in case of failure
                selectionDict["email"] = getEmailInputBoxValue()
                for x in range(connectionAndAPI.countGpus()):
                    with open(f"Configs/config{x}.txt",'r+') as openFile:
                        data = json.load(openFile)
                        data.update(selectionDict)
                        openFile.seek(0)
                        json.dump(data,openFile)
                        openFile.close()
                master.switch_frame(monitoringFrame)










class monitoringFrame(tk.Frame):

    def __init__(self, master):
        global gpuList
        tk.Frame.__init__(self, master)
        master.title("Monitoring Station")
        def resetAll():
            dir = 'Configs'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
                master.switch_frame(StartPage)
        if connectionAndAPI.testGpuConnection() == "testGPUConnection Error":
            tk.Label(self,
                     text="I cannot connect to the miner. Do you have it running?").pack(
                fill="x", pady=10)
            tk.Button(self, text="Reset Profiles", command=lambda:resetAll()).pack

            # The monitoring loop. Checks each gpus present
        label1 = tk.Label(self,
                 text="Oh hello! Connection has been successfully made to your gpu. I am currently monitoring based on your proposed settings")
        label1.pack(
            fill="x", pady=10)
        button1 = tk.Button(self, text="Reset Profiles", command=lambda: resetAll())
        button1.pack()
        try:
            for gpu in gpuList:
                    gpu.checkMaxHash()
                    gpu.checkMinHash()
                    gpu.checkMaxPower()
                    gpu.checkCoreTemp()
                    gpu.checkMemTemp()
        except:
            button1.pack_forget()
            label1.pack_forget()
            tk.Label(self,
                     text="An invalid email address was detected in your profile\n"
                          "Please reset your profiles with the button below").pack(
                fill="x", pady=10)
            tk.Button(self, text="Reset Profiles", command=lambda: resetAll()).pack()

        self.after(5000,lambda: master.switch_frame(monitoringFrame))







if __name__ == "__main__":
    app = createApp()


    app.mainloop()
