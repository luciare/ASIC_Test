# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:09:59 2020

@author: lucia
"""

import numpy as np
import signal
from PyQt5 import Qt
     

class GenerationThread(Qt.QThread):
    NewGenData = Qt.pyqtSignal()

    def __init__(self, Channels, CarrType, tInterrupt, **kwargs):
        '''
        Initialation of the Thread for Generation

        Parameters
        ----------
        :param SigConfig: dictionary, contains all variables related with
                          signal configuration
        SigConfig : dictionary
                    {'Fs': 2000000.0,
                     'nSamples': 20000,
                     'tInterrupt': 0.01,
                     'CarrType': 'sinusoidal',
                     'CarrFrequency': 30000.0,
                     'Phase': 0,
                     'Amplitude': 0.05,
                     'CarrNoise': 0,
                     'ModType': 'sinusoidal',
                     'ModFrequency': 1000.0,
                     'ModFactor': 0.1,
                     'ModNoise': 0
                    }

        Returns
        -------
        None.

        '''
        # super permits to initialize the classes from which this class depends
        super(GenerationThread, self).__init__()
        self.SigConfigKwargs = kwargs
        self.tInterrupt = tInterrupt
        self.FsScope = kwargs['Fs']
        self.BufferSize = kwargs['BufferSize']
        self.Channels = Channels
        
        self.ttimer = ((self.BufferSize/self.FsScope)-0.05)*1000 #1000 para msec
        self.Timer = Qt.QTimer()
        self.Timer.moveToThread(self)

    def run(self):
        '''
        Run function in threads is the loop that will start when thread is
        started.

        Returns
        -------
        None.

        '''
        # while True statement is used to generate a lopp in the run function
        # so, while the thread is active, the while loop is running
        while True:
            # the generation is started
            # The dictionary SigConfig is passed to SignalGenerator class as
            # kwargs, this means you can send the full dictionary and only use
            # the variables in which you are interesed in
            self.OutData = GenAMSignal(**self.SigConfigKwargs)
            self.OutDataReShape = np.reshape(self.OutData,
                                             (self.OutData.size, 1)
                                             )
            self.NewGenData.emit()

            Qt.QThread.msleep(self.tInterrupt)

    def run(self, *args, **kwargs):
        print('start ')      
        self.OutData = np.ndarray((self.BufferSize, len(self.Channels)))
        self.initSessions()
        loop = Qt.QEventLoop()
        loop.exec_()
    
    def GenData(self):
        if not self.isRunning():
            return
        try:
            #Código para realizar el Fetch de adquisición
            Inputs =
            self.Timer.singleShot(self.ttimer, self.GenData)
            # Código para sacar OutData
            # for i, In in enumerate(Inputs):
            #     self.OutData[:, i] = np.array(In.samples)

            self.NewData.emit()

        except Exception:
            print(Exception.args)
            print('Requested data has been overwritten in memory')
            self.stopSessions()
            print('Gen and Scope Sessions Restarted')
            self.initSessions()        
                 
    def initSessions(self):
        #Código para inicializar la generación y la adquisición
        #Para la PXI era: NifGen.session.initiate() y NiScipe.session.initiate()
        self.Timer.singleShot(self.ttimer, self.GenData)
        
    def stopSessions(self):
        #Código para parar la generación y la adquisición
        #Para la PXI era: NifGen.session.abort() y NiScipe.session.abort()
        self.stopTimer()
        
    def stopTimer(self):
        self.Timer.stop()
        self.Timer.killTimer(self.Id)

