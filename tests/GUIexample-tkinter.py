from Tkinter import *
import tkFileDialog
import tkMessageBox
import ttk
import threading
import signal, os
import Queue
import random
import time

# Variable to control working Loop from GUI
wt1_running = False

# Variable to control measurement thread
mt_exit = False


class RoadscanGui:

    cnffile = ""

    def __init__(self, master, queue, stopRequest):
        self.queue = queue

        master.config()
        master.title("Roadscan")

        # WIDGETS STYLE
        self.style = ttk.Style()
        self.style.configure('TFrame', background='oldlace')
        self.style.configure('TButton', foreground='#181a1e', background='#9aa0a0', relief=GROOVE)
        self.style.configure('TEntry', foreground='#181a1e', background='#89f0f9', font=('Arial', 11))
        self.style.configure('TLabel', foreground='#181a1e', background='oldlace', font=('Arial', 10, 'normal'))
        self.style.configure('TCheckbutton', foreground='#181a1e', background='oldlace', font=('Arial', 10, 'normal'))

        # CREATE MENU BAR
        self.menubar = Menu(master)

        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Exit", command=stopRequest)

        self.utilMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Utils", menu=self.utilMenu)
        self.utilMenu.add_command(label="Read GPS", command=self.gps_test)
        self.utilMenu.add_command(label="USB devices", command=self.usb_test)

        # ADD MENU TO THE WINDOW
        master.config(menu=self.menubar)

        # CREATE FRAME WITH MEASUREMENT CONTROLS#
        self.frame_control = ttk.Frame(master, relief=GROOVE)
        self.frame_control.pack(fill=X)


        # WIDGETS DEFINITION
        self.gpslbl = ttk.Label(self.frame_control, text="GPS Port")
        self.gpsport = ttk.Entry(self.frame_control, width=10)

        self.fsh6lbl = ttk.Label(self.frame_control, text="MDEV Port")
        self.fsh6port = ttk.Entry(self.frame_control, width=10)

        self.cfg = ttk.Button(self.frame_control, text="Select configuration", command=self.config_file)

        self.audioon = BooleanVar()
        self.audio = ttk.Checkbutton(self.frame_control, text="Audio", variable=self.audioon, onvalue=True)

        self.detect = ttk.Button(self.frame_control, text="Detect GPS/MDEV", command=self.detect_ports)


        # PUT WIDGETS IN THE FRAME
        self.gpslbl.grid(column=0, row=0, padx=5, pady=5, sticky=W+E)
        self.fsh6lbl.grid(column=1, row=0, padx=5, pady=5, sticky=W+E)

        self.gpsport.grid(column=0, row=1, padx=5, pady=5, sticky=W+E)
        self.fsh6port.grid(column=1, row=1, padx=5, pady=5, sticky=W+E)

        self.audio.grid(column=1, row=2, padx=5, pady=5, sticky=W+E)

        self.cfg.grid(column=0, row=3, padx=5, pady=5, sticky=W+E)
        self.detect.grid(column=1, row=3, padx=5, pady=5, sticky=W+E)


        #######################################
        # CREATE FRAME WITH MEASUREMENT STATUS#
        self.frame_status = ttk.Frame(master)
        self.frame_status.pack(fill=X)

        self.latlnglbl = ttk.Label(self.frame_status, text="lat/lng:")
        self.latlng = ttk.Entry(self.frame_status, width=25)
        self.magnlbl = ttk.Label(self.frame_status, text="Magn.:")
        self.magn = ttk.Entry(self.frame_status, width=25)

        self.start = ttk.Button(self.frame_status, text="Start", command=self.start_measurement)
        self.progbar = ttk.Progressbar(self.frame_status, orient=HORIZONTAL, mode="indeterminate")

        self.latlnglbl.grid(row=0, column=0, padx=5, pady=5, sticky=W+E)
        self.latlng.grid(row=0, column=1, padx=5, pady=5, sticky=W+E)
        self.magnlbl.grid(row=1, column=0, padx=5, pady=5, sticky=W+E)
        self.magn.grid(row=1, column=1, padx=5, pady=5, sticky=W+E)
        self.start.grid(row=2, column=1, padx=5, pady=5, sticky=W+E)
        self.progbar.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=W+E)

        # WORK IN PROGRESS ...


    def config_file(self):
        fname = tkFileDialog.askopenfilename(filetypes=(("Configuration file", "*.ini"), ("Text files", "*.txt")))
        if fname:
            try:
                tkMessageBox.showinfo("Information", "Configuration file selected: %s" % fname)
                self.cnffile = fname
            except:  # <- naked except is a bad idea
                tkMessageBox.showerror("Open Configuration File", "Failed to read file\n'%s'" % fname)


    def detect_ports(self):
        """
        Find USB ports Where are GPS and FSH Connected
        :return:
        """
        import pyudev
        context = pyudev.Context()

        # At first, clear the Entry boxes
        self.gpsport.delete(0, END)
        self.fsh6port.delete(0, END)

        if context.list_devices(subsystem='tty', ID_BUS='usb') == '':
            self.gpsport.insert(0, "off")
            self.fsh6port.insert(0, "off")
        else:
            for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
                if device['ID_MODEL_FROM_DATABASE'].find('GPS') != -1:
                    self.gpsport.insert(0, device['DEVNAME'])
                elif device['ID_MODEL_FROM_DATABASE'].find('FT232') != -1:
                    self.fsh6port.insert(0, device['DEVNAME'])
                else:
                    self.gpsport.insert(0, "Unknown")
                    self.fsh6port.insert(0, "Unknown")
            if self.gpsport.get() == "":
                self.gpsport.insert(0, "off")
            if self.fsh6port.get() == "":
                tkMessageBox.showerror("Error", "You cannot measure without Instrument!")


    def start_measurement(self):
        global wt1_running
        if (self.cnffile == ""):
            tkMessageBox.showerror("Error", "Configuration file was not selected!")
        elif (self.fsh6port == "" or self.fsh6port == "Unknown"):
            tkMessageBox.showerror("Error", "Meas. device is not connected or unknown!")
        else:
            #tkMessageBox.showinfo("Information", "Lets start ...")
            if (self.start['text'] == "Start"):
                wt1_running = True
                self.progbar.start()
                self.start['text'] = "Stop"
            else:
                wt1_running = False
                self.progbar.stop()
                self.start['text'] = "Start"

            print("Config file: {}".format(self.cnffile))
            print("Measurement device port: {}".format(self.fsh6port.get()))
            print("GPS device port: {}".format(self.gpsport.get()))
            print("Sound enabled: {}".format(self.audioon.get()))


    def gps_test(self):
        from Garmin import Gpsmgr
        port = self.gpsport.get()
        self.progbar.start()
        if port.strip() != "":
            type = 'garmin'
            # latit, longit = latlong(port, type).split(',')
            # print("GPS {} is connected to {} port".format(type, port))
            # print("Position is {} {}".format(latit, longit))
            # print("Time is {}".format(gps_time(port, type)))
            if port == 'off':
                print("Info: The GPS is off!")
                mylocation = "0.000000,0.000000"
            else:
                print("Info: Trying to connect with GPS!")
                mygps = Gpsmgr(port, type)
                try:
                    print("Info: Reading GPS position!")
                    mylocation = mygps.getpos()
                except:
                    print("Info: Cannot connect to GPS!")
                    mylocation = "0.000000,0.000000"
            print("lat/lng: {}").format(mylocation)
            #tkMessageBox.showinfo("Information", mylocation)
            self.latlng.delete(0, END)
            self.latlng.insert(0, mylocation)
        else:
            tkMessageBox.showerror("Error", "GPS port is not defined!")
        self.progbar.stop()
        #return mylocation


    def usb_test(self):
        import pyudev
        context = pyudev.Context()
        usb_report = ""
        for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
            usb_report +=("* {}; {}; {}\r\n".format(device['DEVNAME'],
                                      device['ID_MODEL_FROM_DATABASE'],
                                      device['ID_VENDOR_FROM_DATABASE']))
        if usb_report.strip() != "":
            tkMessageBox.showinfo("Information", usb_report)
        else:
            tkMessageBox.showinfo("Information", "There is not any USB device connected!")


    def readMessage(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                receivedData = msg.split(';')

                self.latlng.delete(0, END)
                self.latlng.insert(0, receivedData[0])

                self.magn.delete(0, END)
                self.magn.insert(0, receivedData[1])

                #print("Received Message: {}".format(msg))
            except Queue.Empty:
                pass


class AppThread:
    def __init__(self, app):
        self.app = app
        self.queue = Queue.Queue()

        self.gui = RoadscanGui(app, self.queue, self.stopRequest)
        self.running = 1

        self.thread1 = threading.Thread(target=self.simulator)
        self.thread1.start()

        self.readLoop()


    def simulator(self):
        import time
        print("|----> Simulator CALLED!!!")
        count = 0
        while self.running:
            if wt1_running:
                print("simulator: %s - Change position and Magnitude" % count)
                # self.latlng.delete(0, END)
                # self.magn.delete(0, END)
                # self.latlng.insert(0, "%s,%s" % (count, count + 2))
                # self.magn.insert(0, count + 1)
                msg = "{};{}".format(count*10000, count)
                self.queue.put(msg)
                time.sleep(1)
                count += 1

    def stopRequest(self):
        self.running = 0

    def readLoop(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.readMessage()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.app.after(100, self.readLoop)


def main():
    root = Tk()
    #roadscan = RoadscanGui(root)
    roadscan = AppThread(root)
    root.mainloop()


if __name__ == "__main__":
    main()


