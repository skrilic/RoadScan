from FSH6 import FSH6
import ConfigParser as configparser
from optparse import OptionParser

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

        # parser.add_option("-g", "--gpsport", type="string", dest="gpsport",
        #                   help='On which PORT is GPS device connected? Type "off" for disabling GPS.',
        #                   metavar="GPSPORT")

        parser.add_option("-d", "--directory", type="string", dest="dir",
                          help="Measurement CSV and Plots files go in the DIRECTORY", metavar="DIRECTORY")

        parser.add_option("-c", "--config", type="string", dest="config",
                          help="Full path to the name of instrument configuration file to use", metavar="CONFIGURATION")

        parser.add_option("-t", "--time", type="string", dest="time",
                          help="How long should measurement last? (Default: 10 sec)", metavar="TIME")

        parser.add_option("-s", "--sleep", type="string", dest="sleep",
                          help="SECONDS betweens two consecutive measurements. (Default: 1 sec)", metavar="SECONDS")

        # parser.add_option("-q", "--sqlitedb", type="string", dest="sqldb",
        #                   help="The name of output SQLite database", metavar="SQLITEDB")

        (options, args) = parser.parse_args()
        #
        if options.fshport:
            self.fshport = options.fshport
        else:
            self.callexit("The serial port is not defined!\r\
                    For usage, Please type: <program> --help")
        #
        # if options.gpsport:
        #     self.gpsport = options.gpsport
        # else:
        #     self.gpsport = 'usb:'
        #
        if options.dir:
            self.dirname = options.dir
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
        # if os.path.exists("%s" % ofile):
        #    os.remove("%s" % ofile)
        # Remove previous sqlite database if such exists ...
        # if os.path.exists("%s" % sqlitedb):
        #    os.remove("%s" % sqlitedb)
        #
        return {'fshport': self.fshport,\
                'dirname': self.dirname, \
                'time': self.time, 'sleep': self.sleep, \
                'config': self.config}


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
        'sweep_continuous': config.get("sweep", "continuous"),
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

def draw_pyplot(frequencies, results, datetime, magn_unit):
    datax = frequencies
    datay = results
    plt.ion()
    plt.figure(1)
    plt.subplot(111)
    # # Clear current figure and prepare for the next scan...
    # plt.clf()
    # #---------#
    plt.title('GMT: {}'.format(datetime),
              fontsize=12, fontweight='bold')
    plt.xlabel('Frequency [Hz]', fontsize=12, fontweight='bold')
    plt.ylabel('Magnitude [{}]'.format(magnitude_unit[magn_unit]), fontsize=12, fontweight='bold')
    plt.grid(True)
    plt.plot(datax, datay, color='r', label='the data')
    plt.draw()
    #plt.show(block=True)
    # plt.savefig(graphfile)


def main():

    vars = Getvar().getvars()

    print("Config file: {}".format(vars['config']))
    port = vars['fshport']
    measurement_config_file = "{}".format(vars['config'])

    config = configparser.ConfigParser()
    config.read("{}".format(measurement_config_file))
    #
    #fsh6 = init_measurement(port, measurement_config_file)
    frequencies = list()
    fstart = float(config.get("frequency", "start"))
    fstop = float(config.get("frequency", "stop"))
    magn_unit = config.get("unit", "unit")

    for i in range(300):
        frequencies.append(fstart + i * (fstop-fstart) / 301)
    counter = 0
    start = time.time()
    end = start
    last_draw = False
    while vars['time'] >= (end - start):
        fsh6 = init_measurement(port, measurement_config_file)
        results = measurement(fsh6)
        #
        # For FSH6 length of correct buffer is 301
        # Skip the first measurement, to get rid of FSH6 residual buffer (from previous measurement)
        #
        if len(results) == 301 and counter > 0:
            print(len(results))
            levels = list()
            for magnitude in results:
                if magnitude != '':
                    levels.append(float(magnitude))
            print("Progress time: {}secs of {}secs".format(int(end - start), vars['time']))
            draw_pyplot(frequencies, levels, time_stamp(True), magn_unit)
        time.sleep(vars['sleep'])
        end = time.time()
        counter += 1
    # And one more time to clear the buffer
    #
    fsh6.close()
    print("Measurement has completed ...")
    print("time:%s sec, step: %s sec, span: %s sec" % (vars['time'], vars['sleep'], (end - start)))


if __name__ == '__main__':
    main()


