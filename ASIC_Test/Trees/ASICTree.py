# -*- coding: utf-8 -*-
"""
Created on Fri May 29 17:16:07 2020

@author: lucia
"""

from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes
import pyqtgraph.parametertree.Parameter as pParams

import numpy as np


if __name__ == '__main__':
    
    Clk_Freq_D_Lw ={
            #Freq: M, D
            "54MHz": (27    ,   25), 
            "28MHz": (14    ,   25), 
            "27MHz": (27    ,   50),   
            "26MHz": (13    ,   25),   
            "25MHz": (26    ,   50),  
            "13MHz": (13    ,   50), 
            "6.5MHz": (13    ,   25), 
            "1MHz": (6    ,   50), 
            }
    
    Gain_AFE_Lw = { 2 : 0,
                 4 : 1,
                 8 : 2,
                 16 :3   
        }
    
    Dic_PB_Lw ={
        4: (0,0),   
        8: (0,1),   
        16: (1,0),
        32:(1,1)
    }
    
    Clk_Freq_D_L = list(Clk_Freq_D_Lw.keys())
    Gain_AFE_L = list(Gain_AFE_Lw.keys())
    Dic_PB_L = list(Dic_PB_Lw.keys())
    
else:
    import JoseCodes.BC_COM_AS2_V3 as AS

    #AS2
    Clk_Freq_D_L = list(AS.Clk_Freq_D.keys())
    
    Gain_AFE_L = list(AS.Gain_AFE.keys())
    
    Dic_PB_L = list(AS.Dic_PB.keys())

GeneratorConfig =  {'name': 'GeneratorConfig',
                    'type': 'group',
                    'children':({'name': 'FsClock',
                                 'title': 'AS Clock Frequency',
                                 'type': 'list',
                                 'readonly': False,
                                 'values': Clk_Freq_D_L,
                                 'value': "27MHz",
                                 'visible': True,
                                 'siPrefix': True,
                                 'suffix': 'MHz'},
                                {'name': 'DAC EL',
                                 'title': 'Reference Electrode DAC',
                                 'value': 1.6,
                                 'type': 'float',
                                 'siPrefix': True,
                                 'suffix': 'V'},
                                {'name': 'DAC E',
                                 'title': 'Offset Cancelation DAC',
                                 'value': 0.9,
                                 'type': 'float',
                                 'siPrefix': True,
                                 'suffix': 'V'},                                   
                                {'name': 'DAC COL',
                                 'title': 'Column DAC',
                                 'value': 0.9,
                                 'type': 'float',
                                 'siPrefix': True,
                                 'suffix': 'V'},
                                {'name': 'SCAN',
                                 'title': 'Column Scan',
                                 'values' : Dic_PB_L,
                                 'value': 1,
                                 'type': 'list'},     
                                {'name': 'MASTER',
                                 'title': 'Master ON',
                                 'value': False,
                                 'type': 'bool'},  
                                {'name': 'Runs',
                                 'title': 'Runs completos',
                                 'value': 8,
                                 'type': 'int'},  
                                
                                )}    
    
    #CONFIGURACION ROWS CON CANCELACION DE OFFSETS
RowConf = {'name': 'RowConfig',
           'type': 'group',
            'children':({'name':'Row 0',
                         'type': 'group',
                         'children':({'name': 'Enable',
                                       'type': 'bool',
                                       'value': True,},
                                     {'name': 'Gain',
                                       'type': 'list',
                                       'values':Gain_AFE_L,
                                       'value': 2,},
                                     {'name':'Offset Vector',
                                      'type': 'str', 
                                      'readonly': False,
                                      'value': "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"}
                                     )}, 
                        {'name':'Row 1',
                         'type': 'group',
                         'children':({'name': 'Enable',
                                       'type': 'bool',
                                       'value': True,},
                                     {'name': 'Gain',
                                       'type': 'list',
                                       'values':Gain_AFE_L,
                                       'value': 2,},
                                     {'name':'Offset Vector',
                                      'type': 'str', 
                                      'readonly': False,
                                      'value': "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"}
                                     )}, 
                        {'name':'Row 2',
                         'type': 'group',
                         'children':({'name': 'Enable',
                                       'type': 'bool',
                                       'value': True,},
                                     {'name': 'Gain',
                                       'type': 'list',
                                       'values':Gain_AFE_L,
                                       'value': 2,},
                                     {'name':'Offset Vector',
                                      'type': 'str', 
                                      'readonly': False,
                                      'value': "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"}
                                     )}, 
                        {'name':'Row 3',
                         'type': 'group',
                         'children':({'name': 'Enable',
                                       'type': 'bool',
                                       'value': True,},
                                     {'name': 'Gain',
                                       'type': 'list',
                                       'values':Gain_AFE_L,
                                       'value': 2,},
                                     {'name':'Offset Vector',
                                      'type': 'str', 
                                      'readonly': False,
                                      'value': "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"}
                                     )}, 
      
                        
                                  ) 
                     }

##############################ASIC##########################################
class ASICParameters(pTypes.GroupParameter):
    
    NewConf = Qt.pyqtSignal()
    def __init__(self, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.addChild(GeneratorConfig)
        self.GenConfig = self.param('GeneratorConfig')
        # self.DACEL = self.GenConfig.param('DAC EL')
        #Poner todos los parámetros a los que se quiera acceder o cambiar
        self.Fs = int(self.GenConfig.param('FsClock').value().replace('MHz',''))*10**6
        
        self.addChild(RowConf)
        self.RowsConfig = self.param('RowConfig')
        self.RowsConfig.sigTreeStateChanged.connect(self.on_RowsConfig_changed)

    
        self.nRows = len(self.RowsConfig.children())
        self.nCols = self.GenConfig.param('SCAN').value()
        self.nChannels = self.nRows * self.nCols
        
        self.RunsCompletos = self.GenConfig.param('Runs').value()
        
        #######
        self.GenConfig.sigTreeStateChanged.connect(self.on_GenConfig_change)
        
    def on_RowsConfig_changed(self):
        for pars in self.RowsConfig.children():
            if pars.param('Enable').value():
                self.OffVectStr = ""
                self.OffVect = pars.param('Offset Vector').value().split(",")
                for ind in self.OffVect:
                    if int(ind) < 0:
                        self.OffVect[self.OffVect.index(ind)] = '0'
                    elif int(ind) > 6:
                        self.OffVect[self.OffVect.index(ind)] = '6'

                while len(self.OffVect) < 32:
                    print("Less than 32 values, adding 0s")
                    self.OffVect.append('0')
                while len(self.OffVect) > 32:
                    print("More than 32 values, removing last values")
                    self.OffVect.remove(self.OffVect.index(len(self.OffVect)))
                
                self.OffVectStr = ','.join(self.OffVect)
                pars.param('Offset Vector').setValue(self.OffVectStr)
            
        self.nRows = len(self.RowsConfig.children())
        self.nChannels = self.nRows * self.nCols
        self.NewConf.emit()


            
    def on_GenConfig_change(self):
        
        for child in self.GenConfig.children(): 
            if(child.name()[0:3] == "DAC"):
                ##Limites dac
                if(child.value() >= 1.8):
                    self.GenConfig.param(child.name()).setValue(1.8)
        
                if(child.value() <= 0.0):
                    self.GenConfig.param(child.name()).setValue(0.0)
        
        self.nCols = self.GenConfig.param('SCAN').value()
        self.nChannels = self.nRows * self.nCols
        self.Fs = int(self.GenConfig.param('FsClock').value().replace('MHz',''))*10**6
        self.RunsCompletos = self.GenConfig.param('Runs').value()

        self.NewConf.emit()
    
    def GetFsClock(self):
        Clk_Freq_D ={
                    #Freq: M, D
                    "54MHz": (27    ,   25),
                    "28MHz": (14    ,   25),
                    "27MHz": (27    ,   50),
                    "26MHz": (13    ,   25),
                    "25MHz": (26    ,   50),
                    "13MHz": (13    ,   50),
                    "6.5MHz": (13    ,   25),
                    "1MHz": (6    ,   50),
                    }
        
        FsTuple = Clk_Freq_D[self.FsClock.value()]
        FS = int(self.FsClock.value().replace('MHz',''))*10**6
        return FS, FsTuple

    def GetGenParams(self):
        self.Generator = {}
        for Config in self.GenConfig.children():
           self.Generator[Config.name()] = Config.value()
           
        return self.Generator

    def GetRowsParams(self):
        self.Rows = {}
        for Config in self.RowsConfig.children():
            Rows_S ={}
            for Values in Config.children():
                if Values.name() == 'Offset Vector':
                    Rows_S[Values.name()] = list(map(int,Values.value().split(",")))

                else:
                    Rows_S[Values.name()] = Values.value()
            self.Rows[Config.name()] = Rows_S


        # self.Rows = {}
        # for Config in self.RowsConfig.children():
        #     Rows_S ={}
        #     for Values in Config.children():
        #         Rows_S[Values.name()] = Values.value()
        #     self.Rows[Config.name()] = Rows_S
        
        # return self.Rows
        return self.Rows

    def GetRowsParamsDIC(self):
        
        return self.GenConfig
    
    
    def GetChannels(self):
        """
        Return the channels dictionary.
        Returns
        -------
        Channels : Dictionary, where key is the channel name
                   and value is an integer which indicate the index of the
                   input data array.
        """
        Channels = {}
        for i in range(self.nChannels):
            Name = 'Ch' + str(i)
            Channels[Name] = i
        return Channels
    
if __name__ == '__main__':

    n = ASICParameters(name='ASIC Configuration')
    
    n.GetGenParams()
    
    DIC = n.GetRowsParams()
      
    n.GenConfig.children()    
    
    n.GenConfig["DAC EL"] = 2

    n.GenConfig.param('SCAN').value()
    
    n.nChannels    
    n.nRows
    n.nCols
    
    n.GenConfig.param('SCAN').setValue(1)
