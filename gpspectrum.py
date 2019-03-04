#! /usr/bin/python

__author__="skrilic"
__date__ ="$22.05.2010. 21:25:40$"

from datetime import *
import time
from optparse import OptionParser

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import numpy as np

import configparser
#from string import Template
import os
import threading

from devices.Gpsmgr import Gpsmgr as Gpsmgr
from devices.FSH6mgr import FSH6mgr as FSH6

homedir = os.getenv("HOME")


class ResFile:
    def open(self, dir, name, mode):
        self.file=open("%s/%s" % (dir,name),"%s" % mode)

    def append(self, string):
        self.file.write(string)

    def close(self):
        self.file.close()

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


class Getvar:
    def callexit(self, message_string):
        print(message_string)
        exit()

    def getvars(self):
        parser = OptionParser()
        parser.add_option("-p", "--fshport", type="string", dest="fshport",
                            help="On which PORT is FSH connected?", metavar="FSHPORT")

        parser.add_option("-g", "--gpsport", type="string", dest="gpsport",
                            help='On which PORT is GPS device connected? Type "off" for disabling GPS.', metavar="GPSPORT")

        parser.add_option("-d", "--directory", type="string", dest="dir",
                            help="Measurement CSV and Plots files go in the DIRECTORY", metavar="DIRECTORY")
      
        parser.add_option("-c", "--config", type="string", dest="config",
                          help="The name of the instrument configuration file to use", metavar="CONFIGURATION")

        parser.add_option("-t", "--time", type="string", dest="time",
                          help="How long does measurement take in seconds? (Default: 60 sec)", metavar="TIME")

        parser.add_option("-s", "--sleep", type="string", dest="sleep",
                          help="SECONDS betweens two consecutive measurements. (Default: 10 sec)", metavar="SECONDS")
        """
        parser.add_option("-q", "--sqlitedb", type="string", dest="sqldb",
                          help="The name of output SQLite database", metavar="SQLITEDB")
        """
        (options, args) = parser.parse_args()
        #
        if options.fshport:
            self.fshport = options.fshport
        else:
            self.callexit("The serial port is not defined!\r\
                    For usage, Please type: <program> --help")
        #
        if options.gpsport:
            self.gpsport = options.gpsport
        else:
            self.gpsport = 'usb:'
        #
        if options.dir:
            self.dirname = options.dir
        else:
            self.dirname = "default"
            #print("Results are going to be stored at $HOME/gpspectrum/data directory")
            self.callexit("The data otput directory variable missing!\r\
                   For usage, Please type: <program> --help")
        #
        if options.config:
            self.config = options.config
        else:
            self.config = 'bcfm'
        #
        if options.time:
            self.time = float(options.time)
        else:
            self.time = 60
        #
        if options.sleep:
            self.sleep = float(options.sleep)
        else:
            self.sleep = 10
        #
        # if options.sqldb:
        #     sqlitedb = options.sqldb
        # else:
        #     sqlitedb = 'none'
        #     print "No sqlitedb. Never mind for now, it is OK!"
        #     #callexit("There is not output SQLite database variable!\r\
        #     #        For usage, Please type: <program> --help")
        #
        # Remove previous output file if such exists...
        #if os.path.exists("%s" % ofile):
        #    os.remove("%s" % ofile)
        # Remove previous sqlite database if such exists ...
        #if os.path.exists("%s" % sqlitedb):
        #    os.remove("%s" % sqlitedb)
        #
        return { 'fshport':self.fshport, 'gpsport':self.gpsport,\
                 'dirname':self.dirname,\
                 'time': self.time, 'sleep':self.sleep,\
                 'config':self.config}

def read_datafile(file_name):
    data = np.genfromtxt(file_name, delimiter=' ', skip_header=0, skip_footer=0, names=['x', 'y'])
    return data


def draw_pyplot(datafile, graphfile, myposition, datetime):
    data = read_datafile(datafile)
    plt.figure(1)
    plt.subplot(111)
    # Clear current figure and prepare for the next scan...
    plt.clf()
    plt.title('GPS: {}  GMT: {}'.format(myposition, datetime),
              fontsize=12, fontweight='bold')
    plt.xlabel('Frequency [Hz]', fontsize=12, fontweight='bold')
    plt.ylabel('Magnitude [dBm]', fontsize=12, fontweight='bold')
    plt.grid(True)
    plt.plot(data['x'], data['y'], color='r', label='the data')
    #plt.show()
    plt.savefig(graphfile)


def latlong(port, type):
    if port == 'off':
        mylocation = "0.000000,0.000000"
    else:
        mygps = Gpsmgr(port, type)
        # mygps.setport(port)
        # mygps.setgpstype(type)
        try:
            mylocation=mygps.getpos()
            print("i read location: {} ".format(mylocation))
        except:
            mylocation = "0.000000,0.000000"
        #gpstime=mygps.getgpstime()
    return mylocation


def findpeaks(list):
    vmax0=float(list[0])
    vmin0=float(list[0])
    for v in list:
        if v != '':
            if float(v) > vmax0:
                vmax0 = float(v)
            if float(v) < vmin0:
                vmin0 = float(v)
    return {'ymax':vmax0, 'ymin':vmin0}


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

    return ("{}-{}-{} {}:{}:{}".format(dtnow.tm_year, dtnow.tm_mon, dtnow.tm_mday, dtnow.tm_hour, dtnow.tm_min, dtnow.tm_sec))


def onestep(fshport,gpsport,csvdirname,imagedirname,allresfile,measlogfile,fshconfig,threshold,counter):
    """
    Function creates log files for further analysis in a GPS position. For every GPS position
    this function is called to create log and picture specific for that point.
    """
    config = configparser.ConfigParser()
    config.read("conf/%s.ini" % (fshconfig))
    #
    fstart = float(config.get("frequency","start"))
    fstop = float(config.get("frequency","stop"))
    #
    varreset = config.get("repetition","reset")
    fsh6 = FSH6(fshport)
    fsh6.setmeas(fshconfig,varreset)

    # If this is first cycle then clear the buffer ... and do nothing with it.
    if counter == 0:
        fsh6.getresults(newlinechar='\r')
        # Wait for new buffer ...
        time.sleep(0.1)
        results = fsh6.getresults(newlinechar='\r')

    # If Max-hold mode is required ...
    if config.get("trace","mode") == '2':
        cycle = float(config.get("repetition","cycle"))
        # In this mode preset results are in buffer, so first  clear it ... and do nothing with it.
        fsh6.getresults(newlinechar='\r')
        # Wait for new buffer ...
        time.sleep(cycle)
        results=fsh6.getresults(newlinechar='\r')
    # If Min-hold mode is required ...
    elif config.get("trace","mode") == '3':
        cycle = float(config.get("repetition","cycle"))
        # In this mode preset results are in buffer, so first  clear it ... and do nothing with it.
        fsh6.getresults()
        # Wait for new buffer ...
        time.sleep(cycle)
        results=fsh6.getresults(newlinechar='\r')
    else:
        results=fsh6.getresults(newlinechar='\r')
    fsh6.close()
    dattim = time_stamp(gmt=True)

    myposition = latlong(gpsport,'garmin')
    stepcount  = (len(results) - 1)
    filename_base = dattim.replace(':', '-').replace(' ','_')
    csvfile = "%s_%s.csv" % (myposition.replace(',','-').replace('.','_'),filename_base)
    pngfile = "%s.png" % filename_base
    #
    # First, make sure the file is created, or cleared if already exists...
    # Open file with results for all GPS locations ...
    # And temporary file for Biggles graph ...
    #
    # JUST CREATE FILES
    f1 = AsyncWrite("{}/{}".format(csvdirname, csvfile), "w", "")
    b1 = AsyncWrite("{}/biggles.tmp".format(csvdirname), "w", "")
    f1.start()
    b1.start()

    # Then the file is ready for results gathering ...

    print("-------------------------")

    # How many steps there is?
    #if stepcount > 0:
    i = 1
    for rez in results:
        freq = fstart + (i-1)*(fstop - fstart)/stepcount
        if rez != '' and rez != ' ':
            linefull = "%s,%s,%f,%f,%s,%s\r\n" % (dattim, myposition, float(freq), float(rez), csvfile, pngfile)
            line = "%i,%s,%s\r\n" % (i, freq, rez)
            bigglesline = "%s %s\r\n" % (freq, rez)
            allrf1 = AsyncWrite(allresfile, "a", linefull)
            allrf1.start()

            f2 = AsyncWrite("{}/{}".format(csvdirname, csvfile), "a", line)
            b2 = AsyncWrite("{}/biggles.tmp".format(csvdirname), "a", bigglesline)
            f2.start()
            b2.start()
        i = i+1
    print(results)
    max_min=findpeaks(results)
    if (max_min['ymax'] - threshold) < 0:
        abovethreshold = 0
    else:
        abovethreshold = max_min['ymax'] - threshold
        mlf1 = AsyncWrite(measlogfile, "a", "%s,%s,%s,%s,%s\r\n" % (dattim, myposition, abovethreshold, csvfile, pngfile))
        mlf1.start()

    time.sleep(1)

    draw_thread = threading.Thread(target=draw_pyplot, args=("{}/biggles.tmp".format(csvdirname), "{}/{}".format(imagedirname, pngfile), myposition, dattim))
    draw_thread.start()

    print("GPS position: %s" % myposition)
    print("Max. %s" % max_min['ymax'])
    print("Min. %s" % max_min['ymin'])
    print("-------------------------")


def meascontrol():
    variables = Getvar()
    vars = variables.getvars()
    # Open up file with stored GPS points of measurement, date and time of measurements,
    # and names of files where measurements are stored
    dirname = vars['dirname']
    datetimestring = time_stamp(gmt=True).replace(':', '-').replace(' ','_')
    csvdirname = "%s/%s/csv" % (dirname,datetimestring)
    imagedirname = "%s/%s/image" % (dirname,datetimestring)
    os.makedirs(csvdirname)
    os.makedirs(imagedirname)
    #
    # Open up file for storing measured values for a GPS point ...
    # # And write the table header ...
    #
    # Open up file for storing all measured results from whole path (GPS locations)
    # #First line is populated by names of columns
    # The File holds only names of detailed measurement files and abovetreshold value
    measlog = AsyncWrite("{}/measlog.csv".format(csvdirname), "a",
                         "datetime,latitude,longitude,abovethreshold,csvfile,pngfile\r\n")
    measlog.start()
    # The file holds every measured value and links to the specific detailed files
    allres = AsyncWrite("{}/total.csv".format(csvdirname), "a", "datetime,latitude,longitude,frequency,magnitude,csvfile,pngfile")
    allres.start()
    #
    # First CLEAR output buffer of FSH-6
    # for i in range(3):
    #     clearfsh = FSH6(vars['fshport'])
    #     # Read output and do nothing...
    #     clearfsh.getresults(newlinechar='\r')
    #     clearfsh.close()
    # #
    config = configparser.ConfigParser()
    print("Config file: ./conf/{}.ini".format(vars['config']))
    config.read("./conf/%s.ini" % (vars['config']))
    threshold = float(config.get("level","threshold"))
    #
    counter = 0
    start = time.time()
    end = start
    while vars['time'] >= (end - start):
        onestep( vars['fshport'],
                 vars['gpsport'],
                 csvdirname,
                 imagedirname,
                 "{}/total.csv".format(csvdirname),
                 "{}/measlog.csv".format(csvdirname),
                 vars['config'],
                 threshold,
                 counter)
        time.sleep(vars['sleep'])
        end = time.time()
        counter += 1
    
    print("Measurement has completed ...")
    print("time:%s sec, step: %s sec, span: %s sec" % (vars['time'], vars['sleep'], (end - start)))

def main():
    meascontrol()

if __name__ == "__main__":
    main()
