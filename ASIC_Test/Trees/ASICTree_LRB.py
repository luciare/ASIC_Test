# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 12:31:28 2020

@author: lucia
"""
from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes
import pyqtgraph.parametertree.Parameter as pParams

import numpy as np

Clk_Freq_D_Lw ={#Freq: M, D
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

Dic_PB_Lw ={4: (0,0),   
            8: (0,1),   
            16: (1,0),
            32:(1,1)
            }

Clk_Freq_D_L = list(Clk_Freq_D_Lw.keys())
Gain_AFE_L = list(Gain_AFE_Lw.keys())
Dic_PB_L = list(Dic_PB_Lw.keys())
    
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
                                 'value': 4,
                                 'type': 'list'},     
                                {'name': 'MASTER',
                                 'title': 'Master ON',
                                 'value': False,
                                 'type': 'bool'},     
                                
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
                        # {'name':'Row 1',
                        #  'type': 'group',
                        #  'children':({'name': 'Enable',
                        #                'type': 'bool',
                        #                'value': False,},
                        #              {'name': 'Gain',
                        #                'type': 'int',
                        #                'value': 2,},
                        #              {'name':'Offset Vector',
                        #               'type': 'int', ##Lista de valores???
                        #               'readonly': True,
                        #               'value': [0,0,0,0,0]})}, ##La lista deberia de ser hasta 32 posiciones
                        # {'name':'Row 2',
                        #  'type': 'group',
                        #  'children':({'name': 'Enable',
                        #                'type': 'bool',
                        #                'value': False,},
                        #              {'name': 'Gain',
                        #                'type': 'int',
                        #                'value': 2,},
                        #              {'name':'Offset Vector',
                        #               'type': 'int', ##Lista de valores???
                        #               'readonly': True,
                        #               'value': [0,0,0,0,0]})}, ##La lista deberia de ser hasta 32 posiciones
    
                        # {'name':'Row 3',
                        #  'type': 'group',
                        #  'children':({'name': 'Enable',
                        #                'type': 'bool',
                        #                'value': False,},
                        #              {'name': 'Gain',
                        #                'type': 'int',
                        #                'value': 2,},
                        #              {'name':'Offset Vector',
                        #               'type': 'int', ##Lista de valores???
                        #               'readonly': True,
                        #               'value': [0,0,0,0,0]})}, ##La lista deberia de ser hasta 32 posiciones
    
                                  ) 
                     }

##############################ASIC##########################################
class ASICParameters(pTypes.GroupParameter):
    def __init__(self, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.addChild(GeneratorConfig)
        self.GenConfig = self.param('GeneratorConfig')
        self.DACEL = self.GenConfig.param('DAC EL')
        #Poner todos los parámetros a los que se quiera acceder o cambiar
        self.FsClock = self.GenConfig.param('FsClock')
        self.addChild(RowConf)
        self.RowsConfig = self.param('RowConfig')
        self.RowsConfig.sigTreeStateChanged.connect(self.on_RowsConfig_changed)
        self.DACEL.sigValueChanged.connect(self.on_DACEL_changed)
        
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

    def on_DACEL_changed(self):
        if self.DACEL.value() > 1.8:
            self.DACEL.setValue(1.8)

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
            #se puede implementar este if else para guardar directamente el tuple
            if Config.name() == 'FsClock':
                self.Generator["FS"], self.Generator[Config.name()] = self.GetFsClock()
            else:
                self.Generator[Config.name()] = Config.value()

        return self.Generator

    def GetRowsParams(self):
        self.Rows = {}
        for Config in self.RowsConfig.children():
            Rows_S ={}
            for Values in Config.children():
                if Values.name() == 'Offset Vector':
                    Rows_S[Values.name()] = Values.value().split(",")

                else:
                    Rows_S[Values.name()] = Values.value()
            self.Rows[Config.name()] = Rows_S

        return self.Rows

    def GetRowsParamsDIC(self):
        
        return self.GenConfig