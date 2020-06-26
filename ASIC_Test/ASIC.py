# -*- coding: utf-8 -*-
"""
Created on Fri May 29 17:42:53 2020

@author: lucia
"""
from __future__ import print_function
import os

import numpy as np
import time

from PyQt5 import Qt

from pyqtgraph.parametertree import Parameter, ParameterTree

import Trees.ASICTree as ASICConfig
# import Functions.SignalGeneration as SigGen
# import Functions.FileModule as FileMod
# import Functions.TimePlot as TimePlt
# import Functions.PSDPlot as PSDPlt

import PyqtTools.FileModule as FileMod
from PyqtTools.PlotModule import Plotter as TimePlt
from PyqtTools.PlotModule import PlotterParameters as TimePltPars
from PyqtTools.PlotModule import PSDPlotter as PSDPlt
from PyqtTools.PlotModule import PSDParameters as PSDPltPars


DEBUG = 0
##ASIC
if DEBUG == 0:
    from JoseCodes.BC_COM_AS2_V4 import ThreadAcq as AS_Thread
    from JoseCodes.BC_COM_AS2_V4 import ASIC as AS
    
from bitstring import ConstBitStream


class MainWindow(Qt.QWidget):
    ''' Main Window '''
    def __init__(self):
        # 'Super' is used to initialize the class from which this class
        # depends, in this case MainWindow depends on Qt.Widget class
        super(MainWindow, self).__init__()
    # buscar esto que son cosas de la ventana de la gui
        self.setFocusPolicy(Qt.Qt.WheelFocus)
        layout = Qt.QVBoxLayout(self)
        # Qt.QPushButton is used to generate a button in the GUI
        self.btnStart = Qt.QPushButton("Start Gen and Adq!")
        layout.addWidget(self.btnStart)
        
        self.btnStartSingleAdq = Qt.QPushButton("Single Adq!")
        layout.addWidget(self.btnStartSingleAdq)
        
        self.ResetGraph = Qt.QPushButton("Reset Graphics")
        layout.addWidget(self.ResetGraph)
        
        #Eliminar########################################
        self.btnSaveData= Qt.QPushButton("Save Data")
        layout.addWidget(self.btnSaveData)
        #################################################
        
        # Set threads as None
        self.threadGeneration = None
        self.threadPlotter = None
        self.threadPsdPlotter = None
        self.threadSave = None
        
# #############################Save##############################

        self.SaveStateParams = FileMod.SaveSateParameters(QTparent=self,
                                                          name='FileState',
                                                          title='Save/load config')
        # With this line, it is initize the group of parameters that are
        # going to be part of the full GUI
        self.Parameters = Parameter.create(name='params',
                                           type='group',
                                           children=(self.SaveStateParams,))
        
# #############################File##############################
        self.FileParams = FileMod.SaveFileParameters(QTparent=self,
                                                     name='Record File')
        self.Parameters.addChild(self.FileParams)

# #############################Plot Parameters#### REVISARRRR
        
        self.PlotParams = TimePltPars(name='TimePlt',
                                      title='Time Plot Options')
        
        self.Parameters.addChild(self.PlotParams)

        self.PsdPlotParams = PSDPltPars(name='PSDPlt',
                                                title='PSD Plot Options')
        
        self.Parameters.addChild(self.PsdPlotParams)


# #############################ASIC##############################
        self.ASICParams = ASICConfig.ASICParameters(QTparent=self,
                                                    name='ASIC Configuration')
        self.Parameters.addChild(self.ASICParams)
        
        ##ASIC 2 Class
        if DEBUG == 0:
            self.ASIC_C = AS(DEBUG =1)
        self.ParamChange = 1
                
        # Connect event for managing event
        
        self.ASICParams.NewConf.connect(self.on_NewASICConf)
        
        self.PsdPlotParams.NewConf.connect(self.on_NewPSDConf)
        self.PlotParams.NewConf.connect(self.on_NewPlotConf)

        # Event for debug print of changes
        # self.Parameters.sigTreeStateChanged.connect(self.on_Params_changed)

        # First call of some events for initializations
        self.on_NewASICConf()
        
        # Event of main button start and stop
        self.ResetGraph.clicked.connect(self.on_ResetGraph)
        
        self.btnStart.clicked.connect(self.on_btnStart)
        
        #Boton adicional
        self.btnStartSingleAdq.clicked.connect(self.on_btnStartSingleAdq)
        
        self.btnSaveData.clicked.connect(self.on_btnSaveData)
        
# ############################GuiConfiguration##############################
        # Is the same as before functions but for 'Parameters' variable,
        # which conatins all the trees of all the Gui, so on_Params_changed
        # will be execute for any change in the Gui
        self.Parameters.sigTreeStateChanged.connect(self.on_Params_changed)
    # EXPLICAR ESTO TAMBIEN QUE TIENE QUE VER CON LA GUI
        self.treepar = ParameterTree()
        self.treepar.setParameters(self.Parameters, showTop=False)
        self.treepar.setWindowTitle('pyqtgraph example: Parameter Tree')

        layout.addWidget(self.treepar)

        self.setGeometry(550, 10, 300, 700)
        self.setWindowTitle('MainWindow')


# ############################Changes Control##############################
    def on_Params_changed(self, param, changes):
        '''
        This function is used to print in the consol the changes that have
        been done.

        '''
        print("tree changes:")
        for param, change, data in changes:
            path = self.Parameters.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
        print('  parameter: %s' % childName)
        print('  change:    %s' % change)
        print('  data:      %s' % str(data))
        print('  ----------')
        
        #Flag
        self.ParamChange
        
        
    def on_NewASICConf(self):
        self.PlotParams.SetChannels(self.ASICParams.GetChannels())
        self.PsdPlotParams.ChannelConf = self.PlotParams.ChannelConf
        nChannels = self.PlotParams.param('nChannels').value()
        self.PsdPlotParams.param('nChannels').setValue(nChannels)

        Fs = self.ASICParams.Fs
        print(Fs)
        nCols = self.ASICParams.nCols
        Fs = Fs/2.0/32.0/nCols
        
        self.PlotParams.param('Fs').setValue(Fs)
        self.PsdPlotParams.param('Fs').setValue(Fs)
        
        

    def on_NewPSDConf(self):
        if self.threadPsdPlotter is not None:
            nFFT = self.PsdPlotParams.param('nFFT').value()
            nAvg = self.PsdPlotParams.param('nAvg').value()
            self.threadPsdPlotter.InitBuffer(nFFT=nFFT, nAvg=nAvg)

    def on_NewPlotConf(self):
        if self.threadPlotter is not None:
            ViewTime = self.PlotParams.param('ViewTime').value()
            self.threadPlotter.SetViewTime(ViewTime)        
            RefreshTime = self.PlotParams.param('RefreshTime').value()
            self.threadPlotter.SetRefreshTime(RefreshTime)        

    def on_ResetGraph(self):
        if self.threadGeneration is None:
            return

        # Plot and PSD threads are stopped
        if self.threadPlotter is not None:
            self.threadPlotter.stop()
            self.threadPlotter = None

        if self.threadPsdPlotter is not None:
            self.threadPsdPlotter.stop()
            self.threadPsdPlotter = None

        if self.PlotParams.param('PlotEnable').value():
            Pltkw = self.PlotParams.GetParams()
            self.threadPlotter = TimePlt(**Pltkw)
            self.threadPlotter.start()

        if self.PsdPlotParams.param('PlotEnable').value():
            PSDKwargs = self.PsdPlotParams.GetParams()
            self.threadPsdPlotter = PSDPlt(**PSDKwargs)
            self.threadPsdPlotter.start()        
        
        
# ############################START##############################
    def on_btnStart(self):
        '''
        This function is executed when the 'start' button is pressed. It is
        used to initialize the threads, emit signals and data that are
        necessary durint the execution of the program. Also in this function
        the different threads starts.

        '''
        
        if self.threadGeneration is None:
            print('########## Starting Adquisition ##########')    

            #Actualizacion de los parametros de configuracion
            DIC_C = self.ASICParams.GetGenParams()
            DIC_R = self.ASICParams.GetRowsParams()
            
            #Chapuza
            # self.threadGeneration = self.ASIC_C
            self.threadGeneration = AS_Thread(ASP = self.ASIC_C,nChannels = self.ASICParams.nChannels,nCols = self.ASICParams.nCols,Scale = [2,2,2,2])
            
            #Solo aplicar cambios si es necesario
            if(self.ParamChange):
                self.ASIC_C.Dict_To_InstructionSimple(DIC_C)
                self.ASIC_C.Dict_To_InstructionSimple(DIC_R)
                self.ParamChange = 0
            
            #Runs completos
            self.ASIC_C.Runs_Completos = self.ASICParams.RunsCompletos
            self.ASIC_C.tInterrupt = 1000
            
            self.threadGeneration.NewGenData.connect(self.on_NewSample)
            
            
            
            if self.FileParams.param('Enabled').value():
                FilekwArgs = {'FileName': self.FileParams.FilePath(),
                              'nChannels': self.ASICParams.nChannels,
                              'Fs': None,
                              'ChnNames': None,
                              'MaxSize': None,
                              'dtype': 'float',
                              }
                self.threadSave = FileMod.DataSavingThread(**FilekwArgs)
            
                self.threadSave.start()
            #Reset Plots
            self.on_ResetGraph()
            
            # Start generation
            self.OldTime = time.time()
            self.threadGeneration.start()
            self.btnStart.setText("Stop Gen and Adq!")
        
        else:
            print('########## Stoping Adquisition  ##########')   
            #Pone el ASIC en Standby
            self.ASIC_C.StopRun()
            
            # Thread is terminated and set to None
            self.threadGeneration.NewGenData.disconnect()
            self.threadGeneration.terminate()
            self.threadGeneration = None
        
         # Plot and PSD threads are stopped
            if self.threadPlotter is not None:
                self.threadPlotter.stop()
                self.threadPlotter = None

            if self.threadPsdPlotter is not None:
                self.threadPsdPlotter.stop()
                self.threadPsdPlotter = None

            # Also save thread is stopped
            if self.threadSave is not None:
                self.threadSave.stop()
                self.threadSave = None
            # Button text is changed again
            self.btnStart.setText("Start Gen and Adq!")
        
                        
# ############################Single Adquisition Long##############################
    def on_btnStartSingleAdq(self):
        '''
        This function is executed when the 'start' button is pressed. It is
        used to initialize the threads, emit signals and data that are
        necessary durint the execution of the program. Also in this function
        the different threads starts.

        '''
        print('########## Starting single Adq ##########')    
        
        if self.threadGeneration is None:
            #Actualizacion de los parametros de configuracion
            DIC_C = self.ASICParams.GetGenParams()
            DIC_R = self.ASICParams.GetRowsParams()
            
            #Chapuza
            self.threadGeneration = self.ASIC_C
            
            self.threadGeneration.Dict_To_InstructionSimple(DIC_C)
            self.threadGeneration.Dict_To_InstructionSimple(DIC_R)
            # self.ASIC_C.Dict_To_InstructionSimple(DIC_C)
            # self.ASIC_C.Dict_To_InstructionSimple(DIC_R)
                    
        
            # #Short Run Adquisicion
            # self.Error,self.Col,self.Sar_0,self.Sar_1,self.Sar_2,self.Sar_3 = self.ASIC_C.ReadAcqS()
            self.Error,self.Col,self.Sar_0,self.Sar_1,self.Sar_2,self.Sar_3 = self.ASIC_C.ReadAcqL()
            
            #Pone el ASIC en Standby
            self.threadGeneration.StopRun()
            self.threadGeneration = None
            
        else:
            print('########## Stoping single Adq ##########')      


    def on_NewSample(self):
        """To call when new data ready to read."""

        Ts = time.time() - self.OldTime
        self.OldTime = time.time()
        # Debug print of interruption time
        print('Sample time', Ts)
        # print('Data ', self.threadGeneration.OutData)
                            
        if self.threadPlotter is not None:
            self.threadPlotter.AddData(self.threadGeneration.OutData)
            
        if self.threadSave is not None:
            self.threadSave.AddData(self.threadGeneration.OutData)

        if self.threadPsdPlotter is not None:
            self.threadPsdPlotter.AddData(self.threadGeneration.OutData)
    
    
    ###########ELIMINAR
    def on_btnSaveData(self):
        print("SAVING DATA")
        
        print ("Len Sar 0", len(self.Sar_0))
        print ("Len Sar 1", len(self.Sar_1))
        print ("Len Sar 2", len(self.Sar_2))
        print ("Len Sar 3", len(self.Sar_3))
        
        letra = '2000504_Sar_CDS_999999999'
        
        path_f = "/home/jcisneros/Downloads/DAta_rouleta"
        
        file_name = "SAR_0_AS2t" + letra + ".txt"
        
        self.ASIC_C.Gravar_M_Conversion(path=path_f,filename=file_name,Data=self.Sar_0,Limite= len(self.Sar_0),Conversion=1)
        
        file_name = "SAR_1_AS2t" + letra + ".txt"
        
        self.ASIC_C.Gravar_M_Conversion(path=path_f,filename=file_name,Data=self.Sar_1,Limite= len(self.Sar_1),Conversion=1)
        
        file_name = "SAR_2_AS2t" + letra + ".txt"
        
        self.ASIC_C.Gravar_M_Conversion(path=path_f,filename=file_name,Data=self.Sar_2,Limite= len(self.Sar_2),Conversion=1)
        
        file_name = "SAR_3_AS2t" + letra + ".txt"
        
        self.ASIC_C.Gravar_M_Conversion(path=path_f,filename=file_name,Data=self.Sar_3,Limite= len(self.Sar_3),Conversion=1)
        
        print("END SAVING DATA")

        
        
# ############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()