import serial
import time

__author__="slaven"


class FSH6:
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
        self.fsh.write('{}'.format(cmd))
        #response
        return


    def setcmd(self,cmd):
        self.fsh.write('SET\r')
        #response
        self.fsh.write('{}'.format(cmd))
        #response
        return


    def cmd(self,cmd):
        self.fsh.write('CMD\r')
        #response
        self.fsh.write('{}\r'.format(cmd))
        #response
        return

    def cmd_rest(self):
        self.cmd('PRESET\r')

    def setmeas( self, fshconfig):
        """
        Set instrument for specfic data.
        """
        reset = int(fshconfig['repetition_reset'])
        fstart = float(fshconfig['fstart'])
        fstop = float(fshconfig['fstop'])

        freqcentral = (fstop+fstart)/2
        freqspan = (fstop-fstart)
        ##---------------------------
        self.cmd('REMOTE')
        #self.setcmd('MEAS,1') # Analyzer mode
        if reset:
            self.cmd('PRESET\r')
            time.sleep(1)
        self.setcmd('FREQ,{}\r'.format(freqcentral))
        self.setcmd('SPAN,{}\r'.format(freqspan))
        self.setcmd('SWPTIME,{}\r'.format(fshconfig['sweep_time']))
        self.setcmd('SWPCONT,{}\r'.format(fshconfig['sweep_continous']))
        #self.cmd('INIT\r') #Initialize sweep
        #self.cmd('WAIT\r') #Wait for end of sweep
        self.setcmd('UNIT,{}\r'.format(fshconfig['measurement_unit']))
        self.setcmd('TRACEMODE,{}\r'.format(fshconfig['trace_mode']))
        if fshconfig['trace_mode'] == 1:
            self.setcmd('TRACEAVG,{}\r'.format(fshconfig['trace_type']))
        self.setcmd('TRACEDET,{}\r'.format(fshconfig['trace_detector']))
        #
        self.setcmd('RBW,{}\r'.format(fshconfig['rbw']))
        self.setcmd('VBW,{}\r'.format(fshconfig['vbw']))
        self.getcmd('TRACE\r')


    def getresults(self, newlinechar):
        spectrum = self.fsh.readline()
        newlist = []
        for a in spectrum.split(','):
            b = a.split(newlinechar)
            if b != '' and b != ' ':
                newlist.append(b[len(b)-1])
        return newlist