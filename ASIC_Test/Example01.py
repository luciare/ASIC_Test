# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:18:09 2020

@author: lucia
"""

from __future__ import print_function
import os

import numpy as np
import time

from PyQt5 import Qt

from pyqtgraph.parametertree import Parameter, ParameterTree

import Trees.SignalConfiguration as SigConfig
import Trees.NiScope as ScopeConfig
import Trees.NifGenerator as GenConfig

import Functions.SignalGeneration as SigGen
import Functions.FileModule as FileMod
import Functions.TimePlot as TimePlt
import Functions.PSDPlot as PSDPlt

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

# ############################SignalConfig##############################
        # QTparent indicades that is going to be added a tree in the actual
        # GUI that has already been created.
        # Name is the name that you want as title of your tree in the GUI
        self.GenParams = GenConfig.NifGeneratorParameters(QTparent=self,
                                                          name='Signal Generation SetUp')
        self.Parameters.addChild(self.GenParams)
        
        self.ScopeParams = ScopeConfig.NiScopeParameters(QTparent=self,
                                                         name='Signal Scope SetUp')
        self.Parameters.addChild(self.ScopeParams)


# #############################Plots##############################
        self.PsdPlotParams = PSDPlt.PSDParameters(name='PSD Plot Options')
        self.PsdPlotParams.param('Fs').setValue(self.ScopeParams.FsScope.value())
        self.PsdPlotParams.param('Fmin').setValue(50)
        self.PsdPlotParams.param('nAvg').setValue(50)
        self.Parameters.addChild(self.PsdPlotParams)

        self.PlotParams = TimePlt.PlotterParameters(name='Plot options')
        self.PlotParams.SetChannels(self.ScopeParams.GetRows())
        self.PlotParams.param('Fs').setValue(self.ScopeParams.FsScope.value())

        self.Parameters.addChild(self.PlotParams)
        
# ############################Instancias for Changes######################
        # Statement sigTreeStateChanged.connect is used to execute a function
        # if any parameter of the indicated tree changes
        self.ScopeParams.sigTreeStateChanged.connect(self.on_ScopeConfig_changed)
        
        self.PlotParams.param('PlotEnable').sigValueChanged.connect(self.on_PlotEnable_changed)
        self.PlotParams.param('RefreshTime').sigValueChanged.connect(self.on_RefreshTimePlt_changed)
        self.PlotParams.param('ViewTime').sigValueChanged.connect(self.on_SetViewTimePlt_changed)
        self.PsdPlotParams.param('PSDEnable').sigValueChanged.connect(self.on_PSDEnable_changed)

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
        # Threads are startes as None
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

# ############################Changes Emits##############################
    def on_ScopeConfig_changed(self):
        '''
        This function is used to change the Sampling frequency value and 
        nSamples value of plots to the ones specified in the signal configuration

        '''
        # All Fs values are changed with SigParams.Fs value
        n = round(self.GenParams.FsGen.value()/self.ScopeParams.FsScope.value())
        self.NiScopeParams.FsScope.setValue(self.GenParams.FsGen.value()/n)
        
        self.PlotParams.param('Fs').setValue(self.ScopeParams.FsScope.value())
        self.PsdPlotParams.param('Fs').setValue(self.ScopeParams.FsScope.value())
        self.PlotParams.SetChannels(self.ScopeParams.GetRows())
        self.PlotParams.param('ViewBuffer').setValue(
        self.ScopeParams.BufferSize.value()/self.ScopeParams.FsScope.value())
    

    def on_PSDEnable_changed(self):
        '''
        This function is used to Generate or destroy the PSD plot 

        '''
        if self.threadGeneration is not None:
            self.Gen_Destroy_PsdPlotter()

    def on_PlotEnable_changed(self):
        '''
        This function is used to Generate or destroy the Time plot 

        '''
        if self.threadGeneration is not None:
            self.Gen_Destroy_Plotters()

    def on_RefreshTimePlt_changed(self):
        '''
        This function is used to change the refresh time of Time Plot

        '''
        if self.threadPlotter is not None:
            self.threadPlotter.SetRefreshTime(self.PlotParams.param('RefreshTime').value())

    def on_SetViewTimePlt_changed(self):
        '''
        This function is used to change the View time of Time Plot

        '''
        if self.threadPlotter is not None:
            self.threadPlotter.SetViewTime(self.PlotParams.param('ViewTime').value())

# ############################START##############################
    def on_btnStart(self):
        '''
        This function is executed when the 'start' button is pressed. It is
        used to initialize the threads, emit signals and data that are
        necessary durint the execution of the program. Also in this function
        the different threads starts.

        '''
        # It is checked if the thread of generation is running
        if self.threadGeneration is None: # If it is not running

            self.ScopeKwargs = self.ScopeParams.GetRowParams()
            self.GenConfig = self.GenParams.GetGenParams()
            # The dictionary is passed to the genration thread
            self.threadGeneration = SigGen.GenerationThread(path="C:/Users/lucia/Documents/BiomedCNM/ASIC/PACK/ByteArray.txt",
                                                            GenConfig=self.GenConfig,
                                                            **self.ScopeKwargs)

            self.threadGeneration.NewData.connect(self.on_NewSample)

            self.Gen_Destroy_PsdPlotter()
            self.Gen_Destroy_Plotters()

            self.SaveFiles()

            self.threadGeneration.start()

            self.btnStart.setText("Stop Gen")

            self.OldTime = time.time()

        else:
            # stopped is printed in the console
            print('Stopped')
            # Thread is terminated and set to None
            self.threadGeneration.NewData.disconnect()
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

    def on_NewSample(self):
        '''
        This function is executed when a new amount of values of the signal
        generated are ready so they can be read and processed
        '''
        # It is calculated the period of Generation Thread with the actual
        # time and the one saved in the last iteration
        Ts = time.time() - self.OldTime
        # Time is saved again to calculate the next periot of the thread
        self.OldTime = time.time()
        print('data', self.threadGeneration.OutData)
        # period is printed in the console
        print('Sample time', Ts)
        if self.threadSave is not None:
            self.threadSave.AddData(self.threadGeneration.OutData)
            
        if self.threadPlotter is not None:
            self.threadPlotter.AddData(self.threadGeneration.OutData)

        if self.threadPsdPlotter is not None:
            self.threadPsdPlotter.AddData(self.threadGeneration.OutData)

    def Gen_Destroy_Plotters(self):
        '''
        This function is executed to initialize and start or destroy time plot
        '''
        # If Time plot thread does not exist
        if self.threadPlotter is None:
            # And the plot enable checkbox is selected
            if self.PlotParams.param('PlotEnable').value() is True:
                # A dictionary obtained with Get Params function is saved
                PlotterKwargs = self.PlotParams.GetParams()
                # And is sent to Plotter thread to initialize it
                self.threadPlotter = TimePlt.Plotter(**PlotterKwargs)
                # Then thread is started
                self.threadPlotter.start()
        # If time plot thread exists
        if self.threadPlotter is not None:
            # And plot enable checkbox is not selected
            if self.PlotParams.param('PlotEnable').value() is False:
                # The thread is stopped and set to None
                self.threadPlotter.stop()
                self.threadPlotter = None

    def Gen_Destroy_PsdPlotter(self):
        '''
        This function is executed to initialize and start or destroy PSD plot
        '''
        # If PSD plot thread does not exist
        if self.threadPsdPlotter is None:
            # And the plot enable checkbox is selected
            if self.PsdPlotParams.param('PSDEnable').value() is True:
                # A dictionary obtained with Get Params function is saved
                PlotterKwargs = self.PlotParams.GetParams()
                # And is sent to PSDPlotter thread to initialize it
                self.threadPsdPlotter = PSDPlt.PSDPlotter(ChannelConf=PlotterKwargs['ChannelConf'],
                                                          nChannels=len(self.ScopeParams.GetRowsList()),
                                                          **self.PsdPlotParams.GetParams())
                # Then thread is started
                self.threadPsdPlotter.start()
        # If PSD plot thread exists
        if self.threadPsdPlotter is not None:
            # And plot enable checkbox is not selected
            if self.PsdPlotParams.param('PSDEnable').value() is False:
                # The thread is stopped and set to None
                self.threadPsdPlotter.stop()
                self.threadPsdPlotter = None

# #############################Savind Files##############################
    def SaveFiles(self):
        '''
        This function is executed to initialize and start save thread
        '''
        # The File Name is obtained from the GUI File Path
        FileName = self.FileParams.param('File Path').value()
        # If the is no file name, No file is printed
        if FileName == '':
            print('No file')
        # If there is file name
        else:
            # It is checked if the file exists, if it exists is removed
            if os.path.isfile(FileName):
                print('Remove File')
                os.remove(FileName)
            # Maximum size alowed for the new file is obtained from the GUI
            MaxSize = self.FileParams.param('MaxSize').value()
            # The threas is initialized
            self.threadSave = FileMod.DataSavingThread(FileName=FileName,
                                                       nChannels=len(self.ScopeParams.GetRowsList()),
                                                       MaxSize=MaxSize,
                                                       Fs = self.SigParams.Fs.value(),
                                                       tWait=self.SigParams.tInterrput.value(),
                                                       dtype='float')
            # And then started
            self.threadSave.start()

# ############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()
