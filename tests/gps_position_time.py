from Garmin import Gpsmgr
from optparse import OptionParser


class Getvar:

    def callexit(self, message_string):
        print(message_string)
        exit()

    def getvars(self):
        parser = OptionParser()
        parser.add_option("-m", "--gpsmodel", type="string", dest="gpsmodel",
                            help="Supported GPS model (See the list of supported models on GPSBABEL web site). Garmin is default?", metavar="GPSMODEL")

        parser.add_option("-g", "--gpsport", type="string", dest="gpsport",
                            help='On which PORT is GPS device connected? Type "off" for disabling GPS.', metavar="GPSPORT")

        (options, args) = parser.parse_args()
        #
        if options.gpsmodel:
            self.gpsmodel = options.gpsmodel
        # else:
        #     self.callexit("The GPS model is not defined, garmin is going to be used!\r\
        #                     For usage, Please type: <program> --help")
        else:
            self.gpsmodel = 'garmin'
        #
        if options.gpsport:
            self.gpsport = options.gpsport
        else:
            self.gpsport = 'usb:'
            #
        return {'gpsport': self.gpsport, 'gpsmodel': self.gpsmodel }


def latlong(port, type):
    if port == 'off':
        print("Info: The GPS is off!")
        mylocation = "0.000000,0.000000"
    else:
        print("Info: Trying to connect with GPS!")
        mygps = Gpsmgr(port, type)
        try:
            print("Info: Reading GPS position!")
            mylocation=mygps.getpos()
        except:
            print("Info: Cannot connect to GPS!")
            mylocation = "0.000000,0.000000"
    return mylocation

def gps_time(port, type):
    if port == 'off':
        gpstime = "0-0-0 00:00:00"
    else:
        mygps = Gpsmgr(port, type)
        try:
            gpstime=mygps.getgpstime()
        except:
            gpstime = "0-0-0 00:00:00"
    return gpstime


def draw_gmap(latit, longit):
    import gmplot
    latitudes = [latit,]
    longitudes = [longit,]
    heat_lats = [latit, ]
    heat_lngs = [longit, ]
    gmap = gmplot.GoogleMapPlotter(latit, longit, zoom=16)
    #gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=10)
    # gmap.scatter(more_lats, more_lngs, '#3B0B39', size=40, marker=False)
    # gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
    gmap.heatmap(heat_lats, heat_lngs)
    gmap.draw("mymap.html")


def main():
    vars = Getvar().getvars()
    port = vars['gpsport']
    type = vars['gpsmodel']
    latit, longit = latlong(port, type).split(',')
    print("GPS {} is connected to {} port".format(type, port))
    print("Position is {} {}".format(latit, longit))
    print("Time is {}".format(gps_time(port, type)))
    draw_gmap(float(latit), float(longit))

if __name__ == '__main__':
    main()
