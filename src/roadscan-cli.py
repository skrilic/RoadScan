from devices.FSH6 import FSH6
from devices.Garmin import Gpsmgr
import ConfigParser as configparser
from optparse import OptionParser
import os
import threading
# import matplotlib
# matplotlib.use('vga')
import matplotlib.pyplot as plt

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

# Read command line options
class Getvar:
    def callexit(self, message_string):
        print(message_string)
        exit()

    def getvars(self):
        parser = OptionParser()
        parser.add_option("-p", "--fshport", type="string", dest="fshport",
                          help="On which PORT is FSH connected?", metavar="FSHPORT")

        parser.add_option("-m", "--gpsmodel", type="string", dest="gpsmodel",
                          help="Supported GPS model (See the list of supported models on GPSBABEL web site). Garmin is default?",
                          metavar="GPSMODEL")

        parser.add_option("-g", "--gpsport", type="string", dest="gpsport",
                          help='On which PORT is GPS device connected? Type "off" for disabling GPS.',
                          metavar="GPSPORT")

        parser.add_option("-d", "--directory", type="string", dest="dirname",
                          help="Measurement CSV and Plots files go in the DIRECTORY", metavar="DIRECTORY")

        parser.add_option("-c", "--config", type="string", dest="config",
                          help="Full path to the name of instrument configuration file to use", metavar="CONFIGURATION")

        parser.add_option("-t", "--time", type="string", dest="time",
                          help="How long should measurement last? (Default: 10 sec)", metavar="TIME")

        parser.add_option("-s", "--sleep", type="string", dest="sleep",
                          help="SECONDS betweens two consecutive measurements. (Default: 1 sec)", metavar="SECONDS")

        parser.add_option("-a", "--audio", type="string", dest="audio",
                          help="Audio notification for every measurement cycle (on/off). (Default: off)", metavar="AUDIO")

        # parser.add_option("-q", "--sqlitedb", type="string", dest="sqldb",
        #                   help="The name of output SQLite database", metavar="SQLITEDB")

        (options, args) = parser.parse_args()
        #
        if options.fshport:
            self.fshport = options.fshport
        else:
            self.callexit("The serial port is not defined!\r\
                    For usage, Please type: <program> --help")

        if options.gpsmodel:
            self.gpsmodel = options.gpsmodel
        else:
            self.gpsmodel = 'garmin'

        if options.gpsport:
            self.gpsport = options.gpsport
        else:
            self.gpsport = 'usb:'

        if options.dirname:
            self.dirname = options.dirname
        else:
            self.dirname = "default"
            # print("Results are going to be stored at $HOME/gpspectrum/data directory")
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
            self.time = 10
        #
        if options.sleep:
            self.sleep = float(options.sleep)
        else:
            self.sleep = 1

        if options.audio:
            self.audio = options.audio
        else:
            self.audio = 'off'

        return {'fshport': self.fshport,
                'gpsport': self.gpsport,
                'gpsmodel': self.gpsmodel,
                'dirname': self.dirname,
                'time': self.time, 'sleep': self.sleep,
                'config': self.config,
                'audio': self.audio}


# Connect FSH6
def connect(fsh6port):
    """
    Open up port and connect to the instrument
    :param fsh6port: Port where the instrument is connected
    :return: Return Instrument object
    """
    fsh6 = FSH6(fsh6port)
    return fsh6


# Initialize measurement
def init_measurement(port, measurement_config_file):
    """
    Set instrument for specfic data.
    """
    fsh6 = connect(port)
    config = configparser.ConfigParser()
    print("Config file is {}".format(measurement_config_file))
    config.read("{}".format(measurement_config_file))

    measurement_config = {
        'fstart': float(config.get("frequency", "start")),
        'fstop': float(config.get("frequency", "stop")),
        'repetition_reset': float(config.get("repetition", "reset")),
        'sweep_time': config.get("sweep", "time"),
        'sweep_continous': config.get("sweep", "continous"),
        'measurement_unit': config.get("unit", "unit"),
        'trace_mode': config.get("trace", "mode"),
        'trace_type': config.get("trace", "average"),
        'trace_detector': config.get("trace", "detector"),
        'rbw': config.get("bandwidth", "resolution"),
        'vbw': config.get("bandwidth", "video")
    }
    fsh6.setmeas(measurement_config)
    return fsh6

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


# Perform measurement
def measurement(fsh6):

    results = fsh6.getresults(newlinechar='\r')
    return results


def draw_pyplot(frequencies, results, datetime, magn_unit, output):
    datax = frequencies
    datay = results
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
        #plt.show(block=True)
        plt.savefig(output)


def play_sound(sound_file):
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


def latlong(port, type):
    if port == 'off':
        mylocation = "0.000000,0.000000"
    else:
        mygps = Gpsmgr(port, type)
        try:
            mylocation=mygps.getpos()
        except:
            mylocation = "0.000000,0.000000"
    return mylocation


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


def main():

    vars = Getvar().getvars()

    print("Config file: {}".format(vars['config']))
    fshport = vars['fshport']
    gpsport = vars['gpsport']
    gpsmodel = vars['gpsmodel']
    measurement_config_file = "{}".format(vars['config'])
    dirname = vars['dirname']
    audio = vars['audio']


    config = configparser.ConfigParser()
    config.read("{}".format(measurement_config_file))
    #
    #fsh6 = init_measurement(port, measurement_config_file)
    frequencies = list()
    fstart = float(config.get("frequency", "start"))
    fstop = float(config.get("frequency", "stop"))
    magn_unit = config.get("unit", "unit")
    threshold = float(config.get("level", "threshold"))

    for i in range(300):
        frequencies.append(fstart + i * (fstop-fstart) / 301)
    counter = 0
    start = time.time()
    end = start

    datetimestring = time_stamp(gmt=True).replace(':', '-').replace(' ', '_')
    csvdirname = "%s/%s/csv" % (dirname, datetimestring)
    imagedirname = "%s/%s/png" % (dirname, datetimestring)
    # Create folder infrastructure ...
    os.makedirs(csvdirname)
    os.makedirs(imagedirname)

    # Now, create it ...
    measlogfile = "{}/measlog.csv".format(csvdirname)
    measlog_thread = AsyncWrite(measlogfile, "a",
                         "datetime,latitude,longitude,abovethreshold,csvfile,pngfile\r\n")
    measlog_thread.start()

    while vars['time'] >= (end - start):
        # JUST CREATE FILES FOR STORING RESULTS
        # Names for files at first ...

        filename_base = time_stamp(gmt=True).replace(':', '-').replace(' ', '_')
        myposition = latlong(gpsport, gpsmodel)
        print("GPS: {}".format(myposition))
        csvfile = "%s_%s.csv" % (myposition.replace(',', '-').replace('.', '_'), filename_base)
        pngfile = "%s.png" % filename_base

        fsh6 = init_measurement(fshport, measurement_config_file)
        results = measurement(fsh6)
        #
        # For FSH6 length of correct buffer is 301
        # Skip the first measurement, to get rid of FSH6 residual buffer (from previous measurement)
        #
        dattim = time_stamp(gmt=True)
        if len(results) == 301 and counter > 0:
            print(len(results))
            levels = list()
            for magnitude in results:
                if magnitude != '':
                    levels.append(float(magnitude))
            print("Progress time: {}secs of {}secs".format(int(end - start), vars['time']))

            # Save links to measurement to file
            max_min = findpeaks(levels)
            if (max_min['ymax'] - threshold) < 0:
                abovethreshold = 0
            else:
                abovethreshold = max_min['ymax'] - threshold
            # Files for the cycle
            ## For every cycle write to the cycle measurement file
            csv_thread1 = AsyncWrite("{}/{}".format(csvdirname, csvfile), "w", "i, frequency, magnitude\r\n")
            csv_thread1.start()
            k = 0
            for lvl in levels:
                csv_thread2 = AsyncWrite("{}/{}".format(csvdirname, csvfile), "a", "{},{},{}\r\n".format(k, frequencies[k], lvl))
                csv_thread2.start()
                k += 1

            # Draw to pngfile
            # draw_pyplot(frequencies, levels, time_stamp(True), magn_unit, "display")
            draw_pyplot(frequencies, levels, time_stamp(True), magn_unit, "%s/%s/png/%s" % (dirname, datetimestring, pngfile))

            # Play the sound
            if audio == 'on':
                # sound_thread = threading.Thread(target=play_sound, args=("{}".format("./sounds/Electronic_Chime.wav")))
                # sound_thread.start()
                play_sound("./sounds/Electronic_Chime.wav")

            # Global Link file
            mlf1 = AsyncWrite(measlogfile, "a",
                              "%s,%s,%s,%s,%s\r\n" % (dattim,
                                                      myposition,
                                                      abovethreshold,
                                                      "{}/{}".format(csvdirname, csvfile),
                                                      "{}/{}".format(imagedirname, pngfile))
                              )
            mlf1.start()

        time.sleep(vars['sleep'])
        end = time.time()
        counter += 1
        ## Save CSV file and PNG of measured data in the cycle to appropriate place

        ## Add raw to the measlog.csv file that links GPS positions with appropriate CSV and PNG files and above threashold


    # And one more time to clear the buffer
    #
    fsh6.close()
    print("Measurement has completed ...")
    print("time:%s sec, step: %s sec, span: %s sec" % (vars['time'], vars['sleep'], (end - start)))


if __name__ == '__main__':
    main()


