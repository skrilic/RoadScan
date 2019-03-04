from tkinter import *
import ttk
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
# import tkFileDialog
# import tkMessageBox
import threading
import queue as Queue
import os
import configparser
from measurements.mobile import *
# from devices.GpsDevice import GpsMgr
import matplotlib.pyplot as plt
import gps
import threading
import time


magnitude_unit = {
    '0': 'dBm',
    '1': 'dBmV',
    '2': 'dBuV',
    '3': 'dBuV/m',
    '4': 'dBuA/m',
    '5': 'dB',
    '6': 'Volt',
    '7': 'Watt',
    '8': 'V/m'
}


gpsd = None
gpsp = None

class GpsMgr(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next()  # this will continue to loop and grab EACH set of gpsd info to clear the buffer



# Variable to control working Loop from GUI
wt1_running = False

measdev = ""
gpsdev = ""
measconf = "./conf/default.ini"
audio_switch = 0
gpsmodel = 'garmin'
measEq = None
app_cwd = os.getcwd()  # Find Current dir
sound_file = "{}/{}".format(app_cwd, "/sounds/Electronic_Chime.wav")
directory = '%s/data' % app_cwd  # Output results folder
sleep = 0  # Sleep between measurements cycles

# Output values
frequencies = list()
levels = list()

class AsyncWrite(threading.Thread):
    def __init__(self, output_file, file_mode, text):
        threading.Thread.__init__(self)
        self.output_file = output_file
        self.file_mode = file_mode
        self.text = text

    def run(self):
        f = open(self.output_file, self.file_mode)
        f.write(self.text)
        f.close()


def time_stamp(gmt):
    """
    Return timestamp for log file and spectrum plot
    :param gmt: True or False
    :return: Date-time string
    """
    if gmt:
        dtnow = time.gmtime()
    else:
        dtnow = time.localtime()

    return ("{}-{}-{} {}:{}:{}".format(dtnow.tm_year, dtnow.tm_mon, dtnow.tm_mday, dtnow.tm_hour, dtnow.tm_min,
                                       dtnow.tm_sec))

def draw_pyplot(datetime, magn_unit, output):
    global frequencies
    global levels
    datax = frequencies
    datay = levels
    plt.ion()
    plt.figure(1)
    plt.subplot(111)
    # # Clear current figure and prepare for the next scan...
    plt.clf()
    # #---------#
    plt.title('GMT: {}'.format(datetime),
              fontsize=12, fontweight='bold')
    plt.xlabel('Frequency [Hz]', fontsize=12, fontweight='bold')
    plt.ylabel('Magnitude [{}]'.format(magnitude_unit[magn_unit]), fontsize=12, fontweight='bold')
    plt.grid(True)
    plt.plot(datax, datay, color='r', label='the data')

    if output == "display":
        plt.draw()
    else:
        # plt.show(block=True)
        plt.savefig(output)


def play_sound(sound_file):
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


def findpeaks(list):
    vmax0 = float(list[0])
    vmin0 = float(list[0])
    for v in list:
        if v != '':
            if float(v) > vmax0:
                vmax0 = float(v)
            if float(v) < vmin0:
                vmin0 = float(v)
    return {'ymax': vmax0, 'ymin': vmin0}


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
        """
        Check if all variables are set and then change Working Thread 1 control
        so the loop in WT1 can start and stop accordingly
        :return:
        """
        global wt1_running

        global measdev
        global gpsdev
        global measconf
        global audio_switch
        global measEq

        if (self.cnffile == "" or self.gpsport.get() =="" or self.fsh6port.get() == ""):
            tkMessageBox.showerror("Error", "Configuration file, GPS or Instrument were not selected or present!")
        elif (self.fsh6port == "" or self.fsh6port == "Unknown"):
            tkMessageBox.showerror("Error", "Meas. device is not connected or unknown!")
        else:
            #tkMessageBox.showinfo("Information", "Lets start ...")
            if (self.start['text'] == "Start"):
                wt1_running = True
                self.progbar.start()
                self.start['text'] = "Stop"
                # measEq Controls FSH6 and GPS garmin
                measdev = self.fsh6port.get()
                gpsdev = self.gpsport.get()
                measconf = self.cnffile
                # print("*FSH: {}\n*GPS: {}\n*Config: {}".format(measdev, gpsdev, measconf))
                measEq = MeasurementStep(measdev, gpsdev, gpsmodel, directory, measconf)
            else:
                wt1_running = False
                self.progbar.stop()
                self.start['text'] = "Start"

            # Set global vars so the thread can read from
            measdev = self.fsh6port.get()
            gpsdev = self.gpsport.get()
            measconf = self.cnffile
            audio_switch = self.audioon.get()

            # print("Config file: {}".format(self.cnffile))
            # print("Measurement device port: {}".format(self.fsh6port.get()))
            # print("GPS device port: {}".format(self.gpsport.get()))
            # print("Sound enabled: {}".format(self.audioon.get()))


    def gps_test(self):
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
                # mygps = Gpsmgr(port, type)
                mygps = GpsMgr()
                mygps.start()
                try:
                    print("Info: Reading GPS position!")
                    # mylocation = mygps.getpos()
                    gpsd.data
                    mylocation = "{},{}".format(gpsd.fix.latitude. gpsd.fix.longitude)
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

                # Draw PLOT
                draw_pyplot(receivedData[2], receivedData[3], receivedData[4])

                #print("Received Message: {}".format(msg))
            except Queue.Empty:
                pass


class AppThread:
    def __init__(self, app):
        self.app = app
        self.queue = Queue.Queue()

        self.gui = RoadscanGui(app, self.queue, self.stopRequest)
        self.running = 1

        self.thread1 = threading.Thread(target=self.measLoop)
        self.thread1.start()

        self.readLoop()

    def measLoop(self):
        # measEq Controls FSH6 and GPS garmin
        global measEq
        global frequencies
        global levels

        print("Config file: {}".format(measconf))

        config = configparser.ConfigParser()
        config.read("{}".format(measconf))

        fstart = float(config.get("frequency", "start"))
        fstop = float(config.get("frequency", "stop"))
        magn_unit = config.get("unit", "unit")
        threshold = float(config.get("level", "threshold"))

        # Clear Frequency and Levels List
        frequencies = list()

        for i in range(300):
            frequencies.append(fstart + i * (fstop - fstart) / 301)
        counter = 0

        datetimestring = time_stamp(gmt=True).replace(':', '-').replace(' ', '_')
        csvdirname = "%s/%s/csv" % (directory, datetimestring)
        imagedirname = "%s/%s/png" % (directory, datetimestring)
        # Create folder infrastructure ...
        os.makedirs(csvdirname)
        os.makedirs(imagedirname)

        # Now, create it ...
        measlogfile = "{}/measlog.csv".format(csvdirname)
        measlog_thread = AsyncWrite(measlogfile, "a",
                                    "datetime,latitude,longitude,abovethreshold,csvfile,pngfile\r\n")
        measlog_thread.start()
        while self.running:
            # JUST CREATE FILES FOR STORING RESULTS
            # Names for files at first ...

            filename_base = time_stamp(gmt=True).replace(':', '-').replace(' ', '_')
            if measEq != None:
                myposition = measEq.latlong()
                # print("GPS: {}".format(myposition))
                csvfile = "%s_%s.csv" % (myposition.replace(',', '-').replace('.', '_'), filename_base)
                pngfile = "%s.png" % filename_base

                results = measEq.measurement()
                # print("Length of FSH6 Output is: {}".format(len(results)))
                #
                # For FSH6 length of correct buffer is 301
                # Skip the first measurement, to get rid of FSH6 residual buffer (from previous measurement)
                #
                dattim = time_stamp(gmt=True)
                if len(results) == 301 and counter > 0 and wt1_running:

                    # Clear levels
                    levels = list()

                    for magnitude in results:
                        if magnitude != '':
                            levels.append(float(magnitude))

                    # Save links to measurement to file
                    max_min = findpeaks(levels)
                    if (max_min['ymax'] - threshold) < 0:
                        abovethreshold = 0
                    else:
                        abovethreshold = max_min['ymax'] - threshold

                    # Files for the cycle
                    # For every cycle write to the cycle measurement file
                    csv_thread1 = AsyncWrite("{}/{}".format(csvdirname, csvfile), "w", "i, frequency, magnitude\r\n")
                    csv_thread1.start()
                    k = 0

                    # print("Level, Freq. {} {}".format(len(levels), len(frequencies)))

                    for lvl in levels:
                        csv_thread2 = AsyncWrite("{}/{}".format(csvdirname, csvfile), "a",
                                                 "{},{},{}\r\n".format(k, frequencies[k], lvl))
                        csv_thread2.start()
                        k += 1

                    # Draw to pngfile
                    plot_file = "%s/%s/png/%s" % (directory, datetimestring, pngfile)
                    # draw_pyplot(frequencies, levels, time_stamp(True), magn_unit, plot_file)

                    msg = "{};{};{};{};{}".format(myposition, max_min['ymax'], time_stamp(True), magn_unit, plot_file)
                    self.queue.put(msg)

                    # Play the sound
                    if audio_switch:
                        sound_thread = threading.Thread(target=play_sound, args=(sound_file,))
                        sound_thread.start()
                        # play_sound("%s/sounds/Electronic_Chime.wav" % app_cwd)

                    # Global Link file
                    mlf1 = AsyncWrite(measlogfile, "a",
                                      "%s,%s,%s,%s,%s\r\n" % (dattim,
                                                              myposition,
                                                              abovethreshold,
                                                              "{}/{}".format(csvdirname, csvfile),
                                                              "{}/{}".format(imagedirname, pngfile))
                                      )
                    mlf1.start()
            time.sleep(float(sleep))
            counter += 1

        measEq.release()
        print("Measurement has completed ...")


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
