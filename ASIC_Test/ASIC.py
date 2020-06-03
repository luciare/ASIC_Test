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
# import JoseCodes.BC_COM_AS2_V3 as AS


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

# #############################ASIC##############################
        self.ASICParams = ASICConfig.ASICParameters(QTparent=self,
                                                    name='ASIC Configuration')
        self.Parameters.addChild(self.ASICParams)

        # self.ASIC_C = AS.ASIC(DEBUG =1)
                
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
        
# ############################START##############################
    def on_btnStart(self):
        '''
        This function is executed when the 'start' button is pressed. It is
        used to initialize the threads, emit signals and data that are
        necessary durint the execution of the program. Also in this function
        the different threads starts.

        '''
        
        print('started')
        
# ############################Single Adquisition Long##############################
    def on_btnStartSingleAdq(self):
        '''
        This function is executed when the 'start' button is pressed. It is
        used to initialize the threads, emit signals and data that are
        necessary durint the execution of the program. Also in this function
        the different threads starts.

        '''
        print('########## Starting single Adq ##########')      
        #Actualizacion de los parametros de configuracion
        # DIC_C = self.ASICParams.GetGenParams()
        # DIC_R = self.ASICParams.GetRowsParams()
    
        # self.ASIC_C.Dict_To_InstructionSimple(DIC_C)
        # self.ASIC_C.Dict_To_InstructionSimple(DIC_R)
        
        # #Short Run Adquisicion
        # self.Error,self.Col,self.Sar_0,self.Sar_1,self.Sar_2,self.Sar_3 = self.ASIC_C.ReadAcqS()
        
        # sense FPGA carregar dades:
        
        # convertir sars
        # cridat plots ams row data (probar amb plt.plot())
        
        # desentrallar amb la funcio: 
        
        # cridar plots amd data desentrallada (probar amb plt.plot())
        
        # Save amb FileModule
        
        print('########## Starting single Adq ##########')      

        
        
        
        
# ############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()