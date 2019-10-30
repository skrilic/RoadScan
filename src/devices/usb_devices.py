# import re
# import subprocess
# device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
# df = subprocess.check_output("lsusb", shell=True)
# devices = []
# for i in df.split('\n'):
#     if i:
#         info = device_re.match(i)
#         if info:
#             dinfo = info.groupdict()
#             dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
#             devices.append(dinfo)
# for usb_dev in devices:
#     print("Port: {} - Description: {}".format(usb_dev['device'], usb_dev['tag']))

import pyudev

context = pyudev.Context()

for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
	#pprint.pprint(dict(device))
    #print(dict(device))
    print("{}, {}, {}".format(device['DEVNAME'], device['ID_VENDOR_ID'], device['ID_VENDOR_FROM_DATABASE']))
