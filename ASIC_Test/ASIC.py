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
import Functions.FileModule as FileMod
import Functions.TimePlot as TimePlt
import Functions.PSDPlot as PSDPlt


##ASIC
import JoseCodes.BC_COM_AS2_V3 as AS
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
        
        #Eliminar########################################
        self.btnSaveData= Qt.QPushButton("Save Data")
        layout.addWidget(self.btnSaveData)
        #################################################


# #############################Save##############################
        self.SaveStateParams = FileMod.SaveTreeSateParameters(QTparent=self,
                                                              name='State')
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
        self.PlotParams = TimePlt.PlotterParameters(name='Plot options')
        self.Parameters.addChild(self.PlotParams)


# #############################ASIC##############################
        self.ASICParams = ASICConfig.ASICParameters(QTparent=self,
                                                    name='ASIC Configuration')
        self.Parameters.addChild(self.ASICParams)
        
        ##ASIC 2 Class
        self.ASIC_C = AS.ASIC(DEBUG =1)
        self.ParamChange = 1
                
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
        # It is connected the action of click a button with a function
        self.btnStart.clicked.connect(self.on_btnStart)
        
        #Boton adicional
        self.btnStartSingleAdq.clicked.connect(self.on_btnStartSingleAdq)
        
        self.btnSaveData.clicked.connect(self.on_btnSaveData)


        # Set threads as None
        self.threadGeneration = None
        self.threadPlotter = None
        self.threadPsdPlotter = None
        self.threadSave = None

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
            self.threadGeneration = self.ASIC_C
            
            #Solo aplicar cambios si es necesario
            if(self.ParamChange):
                self.threadGeneration.Dict_To_InstructionSimple(DIC_C)
                self.threadGeneration.Dict_To_InstructionSimple(DIC_R)
                self.ParamChange = 0
            
            #Runs completos
            self.threadGeneration.Runs_Completos = 4
            self.threadGeneration.tInterrupt = 1000
            
            self.threadGeneration.NewGenData.connect(self.on_NewSample)
            
            # Start generation
            self.OldTime = time.time()
            self.threadGeneration.start()
            self.btnStart.setText("Stop Gen and Adq!")
            
            self.Sar_0 = []
            self.Sar_1 = []
            self.Sar_2 = []
            self.Sar_3 = []           
            
            # #Short Run Adquisicion
            # self.Error,self.Col,self.Sar_0,self.Sar_1,self.Sar_2,self.Sar_3 = self.ASIC_C.ReadAcqS()
            
            # sense FPGA carregar dades:
            
            # convertir sars
            # cridat plots ams row data (probar amb plt.plot())
            
        # desentrallar amb la funcio: 
        
        # cridar plots amd data desentrallada (probar amb plt.plot())
        
        # Save amb FileModule    
        
        else:
            print('########## Stoping Adquisition  ##########')   
            #Pone el ASIC en Standby
            self.threadGeneration.StopRun()
            
            # Thread is terminated and set to None
            self.threadGeneration.NewGenData.disconnect()
            self.threadGeneration.terminate()
            self.threadGeneration = None
        
                        
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
            
            # sense FPGA carregar dades:
            
            # convertir sars
            # cridat plots ams row data (probar amb plt.plot())
            
            # desentrallar amb la funcio: 
        
            # cridar plots amd data desentrallada (probar amb plt.plot())
        
            # Save amb FileModule    
        
        else:
            print('########## Stoping single Adq ##########')      


    def on_NewSample(self):
        """To call when new data ready to read."""

        Ts = time.time() - self.OldTime
        self.OldTime = time.time()
        # Debug print of interruption time
        print('Sample time', Ts)
        # print('Data ', self.threadGeneration.OutData)
        

        Buffer_bitstream =ConstBitStream(self.threadGeneration.OutData)
        Buffer_Str = Buffer_bitstream.bin 
        
        self.Error,self.Col,self.Sar_0_I,self.Sar_1_I,self.Sar_2_I,self.Sar_3_I = self.threadGeneration.Bitstream_to_Sep(Buffer_Str=Buffer_Str)
        
        if(self.Error):

            print("ERROR threadGeneration Captura")
        
        else:
            self.Sar_0 = np.append(self.Sar_0,self.Sar_0_I)
            self.Sar_1 = np.append(self.Sar_1,self.Sar_1_I)
            self.Sar_2 = np.append(self.Sar_2,self.Sar_2_I)
            self.Sar_3 = np.append(self.Sar_3,self.Sar_3_I)
            
        if self.threadPlotter is not None:
            self.threadPlotter.AddData(self.threadGeneration.OutData)
        
        
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