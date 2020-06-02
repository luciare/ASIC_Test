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
                                      'type': 'list', 
                                      'readonly': True,
                                      'values': [0,0,0,0,1],##La lista deberia de ser hasta 32 posiciones
                                      'value': [0,0,0]})}, #aqui va el valor predeterminado de la lista
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
        #Poner todos los parámetros a los que se quiera acceder o cambiar
        self.FsClock = self.GenConfig.param('FsClock')
        self.addChild(RowConf)
        self.RowsConfig = self.param('RowConfig')

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
        FsTuple = Clk_Freq_D[self.FsClock]
        return FsTuple
    
    def GetGenParams(self):
        self.Generator = {}
        for Config in self.GenConfig.children():
           self.Generator[Config.name()] = Config.value()
           
        return self.Generator
    
    def GetRowsParams(self):
        # self.Rows = {}
        # for Config in self.RowsConfig.children():
        #     for Values in Config.children():
        #         self.Rows[Config.name()][Values.name()] = Values.value()
        
        self.Rows = {}
        for Config in self.RowsConfig.children():
            Rows_S ={}
            for Values in Config.children():
                Rows_S[Values.name()] = Values.value()
            self.Rows[Config.name()] = Rows_S
        
        return self.Rows
    
    def GetRowsParamsDIC(self):
        
        return self.GenConfig
    
    
if __name__ == '__main__':

    n = ASICParameters(name='ASIC Configuration')
    
    n.GetGenParams()
    
    DIC = n.GetRowsParams()


    