# -*- coding: utf-8 -*-
from measurements.mobile import *
import ConfigParser as configparser
import os
import time
import threading
import matplotlib.pyplot as plt



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

def draw_pyplot(self, frequencies, datetime, magn_unit, output):
    datax = frequencies
    datay = self.measurement() #results
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


def play_sound(self, sound_file):
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


def main():
    import sys

    # Get Variables
    measdev = sys.argv[1]
    gpsdev = sys.argv[2]
    gpsmodel = sys.argv[3]
    directory = sys.argv[4]
    measconfig = sys.argv[5]
    time_span = sys.argv[6]
    sleep = sys.argv[7]
    audio = sys.argv[8]

    # measEq Controls FSH6 and GPS garmin
    measEq = MeasurementStep(measdev, gpsdev, gpsmodel, directory, measconfig)

    print("Config file: {}".format(measconfig))
    # measdev = measEq.measdev
    # gpsport = gps_lvl.gpsdev
    # gpsmodel = gps_lvl.gpsmodel
    # measconfig = measEq.measconfig
    # dirname = directory
    # audio = audio

    config = configparser.ConfigParser()
    config.read("{}".format(measconfig))

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
    print("Time span: {} and ")
    while float(time_span) >= (end - start):
        # JUST CREATE FILES FOR STORING RESULTS
        # Names for files at first ...

        filename_base = time_stamp(gmt=True).replace(':', '-').replace(' ', '_')
        myposition = measEq.latlong()
        print("GPS: {}".format(myposition))
        csvfile = "%s_%s.csv" % (myposition.replace(',', '-').replace('.', '_'), filename_base)
        pngfile = "%s.png" % filename_base

        fsh6 = measEq.init_measurement()
        results = fsh6.measurement()
        print("Length of FSH6 Output is: {}".format(len(results)))
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
            print("Progress time: {}secs of {}secs".format(int(end - start), time_span))

            # Save links to measurement to file
            max_min = measEq.findpeaks(levels)
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
                measEq.draw_pyplot(frequencies, levels, measEq.time_stamp(True), magn_unit, "%s/%s/png/%s" % (directory, datetimestring, pngfile))

            # Play the sound
            if audio == 'on':
                # sound_thread = threading.Thread(target=play_sound, args=("{}".format("./sounds/Electronic_Chime.wav")))
                # sound_thread.start()
                measEq.play_sound("./sounds/Electronic_Chime.wav")

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
        end = time.time()
        delta = end - start
        print("***Time now is {} passed {} of {}.".format(end, delta, time_span))
        counter += 1
        ## Save CSV file and PNG of measured data in the cycle to appropriate place

        ## Add raw to the measlog.csv file that links GPS positions with appropriate CSV and PNG files and above threashold


    # And one more time to clear the buffer
    #
    fsh6.close()
    print("Measurement has completed ...")
    print("time:%s sec, step: %s sec, span: %s sec" % (time_span, sleep, (end - start)))


if __name__ == '__main__':
    main()
