import serial
import ConfigParser as configparser
import time

__author__="slaven"


class FSH6mgr:
    def __init__(self, fshport):
        # self.fshport = fshport
        self.fsh=serial.Serial()
        ##---DEFINING SERIAL PORT ---
        self.fsh.port=fshport
        self.fsh.baudrate=19200
        self.fsh.bytesize=8
        self.fsh.parity='N'
        self.fsh.stopbits=1
        self.fsh.timeout=1
        self.fsh.xonxoff=0
        self.fsh.rtscts=0
        ##---------------------------
        self.fsh.open()

    def close(self):
        self.fsh.write('CMD\r')
        self.fsh.write('LOCAL\r')
        self.fsh.close()

    # FSH6 Types of commands and handling different responses
    def getcmd(self,cmd):
        self.fsh.write('GET\r')
        #response
        self.fsh.write('%s' % cmd)
        #response
        return

    def setcmd(self,cmd):
        self.fsh.write('SET\r')
        #response
        self.fsh.write('%s' % cmd)
        #response
        return


    def cmd(self,cmd):
        self.fsh.write('CMD\r')
        #response
        self.fsh.write('%s\r' % cmd)
        #response
        return


    def setmeas( self, fshconfig, reset ):
        """
        Set instrument for specfic data.
        """
        config = configparser.ConfigParser()
        print("Config file is ./conf/{}.ini".format(fshconfig))
        config.read("./conf/%s.ini" % (fshconfig))
        fstart = float(config.get("frequency","start"))
        fstop = float(config.get("frequency","stop"))

        freqcentral = (fstop+fstart)/2
        freqspan = (fstop-fstart)
        ##---------------------------
        self.cmd('REMOTE')
        #self.setcmd('MEAS,1') # Analyzer mode
        if reset == '1':
            self.cmd('PRESET\r')
            time.sleep(1)
        self.setcmd('FREQ,%s\r' % freqcentral)
        self.setcmd('SPAN,%s\r' % freqspan)
        self.setcmd('SWPTIME, %s\r' % (config.get("sweep","time")))
        self.setcmd('SWPCONT,%s\r' % (config.get("sweep","continous")))
        #self.cmd('INIT\r') #Initialize sweep
        #self.cmd('WAIT\r') #Wait for end of sweep
        self.setcmd('UNIT,%s\r' % (config.get("unit","unit")))
        self.setcmd('TRACEMODE,%s\r' % (config.get("trace","mode")))
        if config.get("trace","mode") == 1:
            self.setcmd('TRACEAVG,%s\r' % (config.get("trace","average")))
        self.setcmd('TRACEDET,%s\r' % (config.get("trace","detector")))
        #
        self.setcmd('RBW,%s\r' % (config.get("bandwidth","resolution")))
        self.setcmd('VBW,%s\r' % (config.get("bandwidth","video")))
        self.getcmd('TRACE\r')


    def getresults(self, newlinechar):
        spectrum = self.fsh.readline()
        newlist = []
        for a in spectrum.split(','):
            b = a.split(newlinechar)
            if b != '' and b != ' ':
                newlist.append(b[len(b)-1])
        return newlist