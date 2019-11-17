import serial
import time

__author__ = "Slaven Krilic"


class FSH6:
    strcmd = 'CMD\r'
    strlocal = 'LOCAL\r'
    strget = 'GET\r'
    strset = 'SET\r'
    strpreset = 'PRESET\r'

    def __init__(self, fshport):
        # self.fshport = fshport
        self.fsh = serial.Serial()
        # #---DEFINING SERIAL PORT ---
        self.fsh.port = fshport
        self.fsh.baudrate = 19200
        self.fsh.bytesize = 8
        self.fsh.parity = 'N'
        self.fsh.stopbits = 1
        self.fsh.timeout = 1
        self.fsh.xonxoff = 0
        self.fsh.rtscts = 0
        # #---------------------------
        self.fsh.open()

    def close(self):
        self.fsh.write(self.strcmd.encode())
        self.fsh.write(self.strlocal.encode())
        self.fsh.close()

    # FSH6 Types of commands and handling different responses
    def getcmd(self, cmd):
        self.fsh.write(self.strget.encode())
        # response
        self.fsh.write(cmd)
        # response
        return

    def setcmd(self, cmd):
        self.fsh.write(self.strset.encode())
        # response
        self.fsh.write(cmd)
        # response
        return

    def cmd(self, cmd):
        self.fsh.write(self.strcmd.encode())
        # response
        self.fsh.write(cmd)
        # response
        return

    def cmd_rest(self):
        self.cmd(self.strpreset.encode())

    def setmeas(self, fshconfig):
        """
        Set instrument for specfic data.
        """
        reset = int(fshconfig['repetition_reset'])
        fstart = float(fshconfig['fstart'])
        fstop = float(fshconfig['fstop'])

        freqcentral = (fstop + fstart) / 2
        freqspan = (fstop - fstart)
        # #---------------------------
        self.cmd("REMOTE\r".encode())
        # self.setcmd('MEAS,1') # Analyzer mode
        if reset:
            self.cmd('PRESET\r')
            time.sleep(1)
        self.setcmd(('FREQ,{}\r'.format(freqcentral)).encode())
        self.setcmd(('SPAN,{}\r'.format(freqspan)).encode())
        self.setcmd(('SWPTIME,{}\r'.format(fshconfig['sweep_time'])).encode())
        self.setcmd(('SWPCONT,{}\r'.format(fshconfig['sweep_continuous'])).encode())
        # self.cmd('INIT\r') #Initialize sweep
        # self.cmd('WAIT\r') #Wait for end of sweep
        self.setcmd(('UNIT,{}\r'.format(fshconfig['measurement_unit'])).encode())
        self.setcmd(('TRACEMODE,{}\r'.format(fshconfig['trace_mode'])).encode())
        if fshconfig['trace_mode'] == 1:
            self.setcmd(('TRACEAVG,{}\r'.format(fshconfig['trace_type'])).encode())
        self.setcmd(('TRACEDET,{}\r'.format(fshconfig['trace_detector'])).encode())
        #
        self.setcmd(('RBW,{}\r'.format(fshconfig['rbw'])).encode())
        self.setcmd(('VBW,{}\r'.format(fshconfig['vbw'])).encode())
        self.getcmd(('TRACE\r').encode())

    def getresults(self, newlinechar):
        spectrum = self.fsh.readline()
        strspectrum = spectrum.decode("utf-8")
        newlist = []
        for a in strspectrum.split(','):
            b = a.split(newlinechar)
            if b != '' and b != ' ':
                newlist.append(b[len(b) - 1])
        return newlist
