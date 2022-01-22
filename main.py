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
        connectionAndAPI.gatherConfigs()
        if kappa == "testGPUConnection Error":
            tk.Label(self,
                     text="I cannot connect to any NVIDIA GPUs. Please start the miner before you start this monitoring program\n "
                          "Please note- Only NVIDIA Gpus are supported at this time\n"
                          "Resetting your profiles for each card may solve the issue").pack(
                fill="x", pady=10)
            tk.Button(self, text="Reset Profiles and restart program", command=lambda:resetAll(1)).pack()
        else:
            for x in kappa:

                try:
                    with open(f"Configs/config{x['device_id']}.txt", 'r') as f:
                        json_object = json.load(f)
                        gpuList.append(connectionAndAPI.gpu.from_json(json_object))
                        f.close()
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
        def getEmailInputBoxValue():
            userInput = emailInputBox.get()
            if userInput == '':
                messagebox.showerror(title="Invalid Email Input",
                                     message="Please input a email so that we can notify you when an error occurs.")
            else:
                return userInput

        # this is a function to get the user input from the text input box
        def getCoreTempInputBoxValue():
            userInput = coreTempInput.get()
            if coreTempInput.cget('state') == "normal":
                try:
                    userInput = int(userInput)
                    return userInput
                except:
                    messagebox.showerror(title="Invalid Core Temp Input",
                                         message="Please input a numerical Max Core Temperature")
            else:
                return

        # this is a function to get the user input from the text input box
        def getGDDRInputBoxValue():

            userInput = gddrInput.get()
            if gddrInput.cget('state') == "normal":
                try:
                    userInput = int(userInput)
                    return userInput
                except:
                    messagebox.showerror(title="Invalid Memory Temp Input",
                                         message="Please input a numerical Max GDDR6X Temperature")
            else:
                return

        # this is a function to get the user input from the text input box
        def getPowerInputBoxValue():
            userInput = gpuPowerInput.get()
            if gpuPowerInput.cget('state') == "normal":
                try:
                    userInput = int(userInput)
                    return userInput
                except:
                    messagebox.showerror(title="Invalid Max Power Input",
                                         message="Please input a numerical Max Power in Watts")
            else:
                return

        # this is a function to get the user input from the text input box
        def getHotSpotInputBoxValue():
            userInput = hotSpotTempInput.get()
            if hotSpotTempInput.cget('state') == "normal":
                try:
                    userInput = int(userInput)
                    return userInput
                except:
                    messagebox.showerror(title="Invalid Hot Spot Temp Input",
                                         message="Please input a numerical Max Hot Spot Temperature")
            else:
                return

        def getMaxHashrateInputBoxValue():
            userInput = maxHashrateInput.get()

            if maxHashrateInput.cget('state') == "normal":
                try:
                    userInput = int(userInput)
                    return userInput
                except:
                    messagebox.showerror(title="Invalid Max Hashrate",
                                         message="Please input a numerical max hashrate")
            else:
                return

        def getMinHashrateInputBoxValue():
            userInput = minHashrateInput.get()

            if minHashrateInput.cget('state') == "normal":
                try:
                    userInput = int(userInput)
                    return userInput
                except:
                    messagebox.showerror(title="Invalid Min Hashrate",
                                         message="Please input a numerical minimum hashrate")
            else:
                return

        def getAllAndCheck():

            nextDevice = connectionAndAPI.currentDeviceWithoutConfig()

            dict = {"deviceID": nextDevice[0],

                    "minerType": app.minerType,

                    "email": getEmailInputBoxValue(),

                    "coreTemp": getCoreTempInputBoxValue(),

                    "memTemp": getGDDRInputBoxValue(),

                    "powerMax": getPowerInputBoxValue(),

                    "hotSpot": getHotSpotInputBoxValue(),

                    "maxHash": getMaxHashrateInputBoxValue(),

                    "minHash": getMinHashrateInputBoxValue(),



                    }
            json_object = json.dumps(dict)
            # The break cases where the data should not be sent to further processing
            if dict["email"] == None or dict["minerType"] == None:
                return
            else:
                if nextDevice != None:
                    with open(f"Configs/config{nextDevice[0]}.txt", "w+") as outfile:
                        outfile.write(json_object)
                        gpuList.append(connectionAndAPI.gpu.from_json(json_object))
                        outfile.close()
                        if len(gpuList) != connectionAndAPI.countGpus():
                            app.switch_frame(StartPage)
                        else:
                            app.switch_frame(monitoringFrame)
                else:
                    print("fuck")

        def on_click(event):
            event.widget.delete(0, tk.END)

        def show_entry(var, widget):

            if var.get() == 0:
                # Clean up line and function
                widget.delete(0, tk.END)
                widget.configure(state="disabled")
            else:
                widget.configure(state="normal")

        # This is the section of code which creates the a label
        Label(self, text='What email would you like to be notified at?',
              font=('arial', 10, 'normal')).place(x=15, y=12)

        # This is the section of code which creates a text input box
        emailInputBox = Entry(self, width=40)
        emailInputBox.place(x=15, y=30)

        # Making the monitor label
        Label(self, text='What would you like me to monitor?', font=('arial', 10, 'normal')).place(x=12, y=60)
        # core temp input and checkbox block
        coreTempInput = Entry(self, width=20, )
        coreTempInput.place(x=103, y=100)
        coreTempInput.bind("<Button-1>", on_click)
        coreTempInput.configure(state="disabled")

        CoreTempCheck = Checkbutton(self, onvalue=1, offvalue=0, text='Core Temp', variable=coreTempCheckVariable,
                                    font=('arial', 8, 'normal'),
                                    command=lambda: [show_entry(coreTempCheckVariable, coreTempInput),
                                                     coreTempInput.insert(tk.END, "Enter Max Core Temp")
                                                     ])
        CoreTempCheck.place(x=9, y=97)
        # end core temp block

        # Gddr6x input block
        gddrInput = Entry(self, width=20)
        gddrInput.place(x=121, y=134)
        gddrInput.bind("<Button-1>", on_click)
        gddrInput.configure(state="disabled")

        # This is the section of code which creates a checkbox
        gddrTempCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='GDDR6X Temp',
                                       variable=gddrTempCheckboxVariable,
                                       command=lambda: [show_entry(gddrTempCheckboxVariable, gddrInput),
                                                        gddrInput.insert(tk.END, "Enter Max Memory Temp")])
        gddrTempCheckbox.place(x=9, y=131)
        # end gddr block

        # Power input block
        gpuPowerInput = Entry(self, width=21)
        gpuPowerInput.place(x=134, y=170)
        gpuPowerInput.bind("<Button-1>", on_click)
        gpuPowerInput.configure(state="disabled")

        gpuPowerCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Gpu Power Draw', variable=gpuPowerCheckboxVar,
                                       command=lambda: [show_entry(gpuPowerCheckboxVar, gpuPowerInput),
                                                        gpuPowerInput.insert(tk.END, "Enter Max Power(Watts)")])
        gpuPowerCheckbox.place(x=9, y=167)
        # End gpu power input block

        # hotspot block
        hotSpotTempInput = Entry(self, width=20)
        hotSpotTempInput.place(x=126, y=201)
        hotSpotTempInput.bind("<Button-1>", on_click)
        hotSpotTempInput.configure(state="disabled")

        hotSpotTempCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Hot Spot Temp',
                                          variable=hotSpotTempCheckboxVar,
                                          command=lambda: [show_entry(hotSpotTempCheckboxVar, hotSpotTempInput),
                                                           hotSpotTempInput.insert(tk.END, "Enter Max Hot Spot")])
        hotSpotTempCheckbox.place(x=9, y=198)

        # Max Hashrate block
        maxHashrateInput = Entry(self, width=20)
        maxHashrateInput.place(x=126, y=230)
        maxHashrateInput.bind("<Button-1>", on_click)
        maxHashrateInput.configure(state="disabled")

        maxHashrateCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Max Hashrate',
                                          variable=maxHashrateCheckboxVar,
                                          command=lambda: [show_entry(maxHashrateCheckboxVar, maxHashrateInput),
                                                           maxHashrateInput.insert(tk.END, "Enter Max Hashrate")])
        maxHashrateCheckbox.place(x=9, y=227)

        # Min Hashrate block
        minHashrateInput = Entry(self, width=25)
        minHashrateInput.place(x=140, y=260)
        minHashrateInput.bind("<Button-1>", on_click)
        minHashrateInput.configure(state="disabled")

        minHashrateCheckbox = Checkbutton(self, onvalue=1, offvalue=0, text='Minimum Hashrate',
                                          variable=minHashrateCheckboxVar,
                                          command=lambda: [show_entry(minHashrateCheckboxVar, minHashrateInput),
                                                           minHashrateInput.insert(tk.END, "Enter Min Hashrate")])
        minHashrateCheckbox.place(x=9, y=257)

        # This is the section of code which creates a button
        Button(self, text='Begin Monitoring', bg='#F0F8FF', font=('arial', 8, 'normal'), command=lambda: getAllAndCheck(
        )).place(x=101, y=300)


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
        for gpu in gpuList:
            gpu.checkMaxHash()
        tk.Label(self,
                 text="Oh hello! Connection has been successfully made to your gpu. I am currently monitoring based on your proposed settings").pack(
            fill="x", pady=10)
        tk.Button(self, text="Reset Profiles", command=lambda:resetAll).pack()
        self.after(5000,lambda: master.switch_frame(monitoringFrame))




if __name__ == "__main__":
    app = createApp()

    app.mainloop()
