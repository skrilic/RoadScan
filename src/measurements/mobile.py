# -*- coding: utf-8 -*-
from devices import FSH6, gps_device

# from devices.Garmin import Gpsmgr
import configparser

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


class MeasurementStep:

    def __init__(self, measdev, gpsdev, directory, measconfig):
        self.measdev = measdev
        self.gpsdev = gpsdev
        self.directory = directory
        self.measconfig = measconfig

    # Connect FSH6
    def connect(self):
        """
        Open up port and connect to the instrument
        :param self.measdev: Port where the instrument is connected
        :return: Return Instrument object
        """
        fsh6 = FSH6(self.measdev)
        return fsh6

    # Initialize measurement
    def init_measurement(self):
        """
        Set instrument for specfic data.
        """
        fsh6 = self.connect()
        config = configparser.ConfigParser()
        # print("Config file is {}".format(self.config))
        config.read("{}".format(self.measconfig))

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

    def release(self):
        fsh6 = self.connect()
        fsh6.close()

    # Perform measurement
    def measurement(self):
        fsh6 = self.init_measurement()
        results = fsh6.getresults(newlinechar='\r')
        return results

    def latlong(self):
        if self.gpsdev == 'off':
            mylocation = "0.000000,0.000000"
        else:
            lat_long = gps_device.get_gps_data()['position']
            mylocation = f"{lat_long[0]},{lat_long[1]}"
        return mylocation