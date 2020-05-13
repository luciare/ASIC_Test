# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:09:59 2020

@author: lucia
"""

import numpy as np
import signal
from PyQt5 import Qt
     

class GenerationThread(Qt.QThread):
    NewData = Qt.pyqtSignal()

    def __init__(self, GenConfig, NRow, tInterrupt, **kwargs):
        '''
        Initialation of the Thread for Generation

        Parameters
        ----------
        :param :

        Returns
        -------
        None.

        '''
        # super permits to initialize the classes from which this class depends
        super(GenerationThread, self).__init__()
        self.GenKwargs = GenConfig
        self.ScopeKwargs = kwargs
        self.tInterrupt = tInterrupt
        self.FsScope = kwargs['FsScope']
        self.BufferSize = kwargs['BufferSize']
        self.nRows = NRow
        
        self.tTimer = (self.tInterrupt-0.05)*1000 #1000 para msec
        self.Timer = Qt.QTimer()
        self.Timer.moveToThread(self)

    def run(self, *args, **kwargs):
        print('start ')      
        self.OutData = np.ndarray((self.BufferSize, self.nRows))
        self.initSessions()
        loop = Qt.QEventLoop()
        loop.exec_()
    
    def GenData(self):
        if not self.isRunning():
            return
        try:
            #Código para realizar el Fetch de adquisición
            # Inputs =
            self.Timer.singleShot(self.tTimer, self.GenData)
            # Código para sacar OutData
            # for i, In in enumerate(Inputs):
            #     self.OutData[:, i] = np.array(In.samples)
            # self.OutData = #matriz 4xvalues
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
        self.Timer.singleShot(self.tTimer, self.GenData)
        
    def stopSessions(self):
        #Código para parar la generación y la adquisición
        #Para la PXI era: NifGen.session.abort() y NiScipe.session.abort()
        self.stopTimer()
        
    def stopTimer(self):
        self.Timer.stop()
        self.Timer.killTimer(self.Id)

