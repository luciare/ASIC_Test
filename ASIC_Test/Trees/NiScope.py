# -*- coding: utf-8 -*-
"""
Created on Wed May 22 11:39:12 2019

@author: Lucia
"""

from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes
import pyqtgraph.parametertree.Parameter as pParams

import numpy as np

NiScopeAcqParam =  {'name': 'AcqConfig',
                       'type': 'group',
                       'children':({'name': 'FsScope',
                                    'title': 'Sampling Rate',
                                    'type': 'float',
                                    'value': 2e6,
                                    'siPrefix': True,
                                    'suffix': 'Hz'},
                                   {'name': 'BufferSize',
                                    'title': 'Buffer Size',
                                    'type': 'int',
                                    'value': int(20e3),
                                    'readonly': True,
                                    'siPrefix': True,
                                    'suffix': 'Samples'},
                                   {'name': 'tInterrupt',
                                    'title': 'Interrupt Time',
                                    'type': 'float',
                                    'value': 0.5,
                                    'siPrefix': True,
                                    'suffix': 's'},
                                   {'name': 'NRow',
                                    'title': 'Number of Channels',
                                    'type': 'int',
                                    'value': 0,
                                    'readonly': True,
                                    'siPrefix': True,
                                    'suffix': 'Chan'},
                                   )
                 }
NiScopeRowsParam = {'name': 'RowsConfig',
                   'type': 'group',
                   'children':({'name':'Row1',
                                'type': 'group',
                                'children':({'name': 'Enable',
                                             'type': 'bool',
                                             'value': True,},
                                            {'name':'Index',
                                             'type': 'int',
                                             'readonly': True,
                                             'value': 0},
                                            {'name': 'AcqVRange',
                                             'title': 'Voltage Range',
                                             'type': 'list',
                                             'values': [0.05, 0.2, 1, 6],
                                             'value': 1,
                                             'visible': True
                                             }
                                            )},
                               {'name':'Row2',
                                'type': 'group',
                                'children':({'name': 'Enable',
                                             'type': 'bool',
                                             'value': True,},
                                            {'name':'Index',
                                             'type': 'int',
                                             'readonly': True,
                                             'value': 1},
                                            {'name': 'AcqVRange',
                                             'title': 'Voltage Range',
                                             'type': 'list',
                                             'values': [0.05, 0.2, 1, 6],
                                             'value': 1,
                                             'visible': True
                                             }
                                            )},
                               {'name':'Row3',
                                'type': 'group',
                                'children':({'name': 'Enable',
                                             'type': 'bool',
                                             'value': True,},
                                            {'name':'Index',
                                             'type': 'int',
                                             'readonly': True,
                                             'value': 2},
                                            {'name': 'AcqVRange',
                                             'title': 'Voltage Range',
                                             'type': 'list',
                                             'values': [0.05, 0.2, 1, 6],
                                             'value': 1,
                                             'visible': True
                                             }
                                            )},
                               {'name':'Row4',
                                'type': 'group',
                                'children':({'name': 'Enable',
                                             'type': 'bool',
                                             'value': True,},
                                            {'name':'Index',
                                             'type': 'int',
                                             'readonly': True,
                                             'value': 3},
                                            {'name': 'AcqVRange',
                                             'title': 'Voltage Range',
                                             'type': 'list',
                                             'values': [0.05, 0.2, 1, 6],
                                             'value': 1,
                                             'visible': True
                                             })
                                }),
                              }
                       
##############################SCOPE##########################################                                
class NiScopeParameters(pTypes.GroupParameter):
        
    def __init__(self, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)
        
        self.addChild(NiScopeRowsParam)
        
        self.RowsConfig = self.param('RowsConfig')
        
        self.addChild(NiScopeAcqParam)
        self.AcqConfig = self.param('AcqConfig')
        self.FsScope = self.AcqConfig.param('FsScope')
        self.BufferSize = self.AcqConfig.param('BufferSize')
        self.NRows = self.AcqConfig.param('NRow')
        self.tInterrupt = self.AcqConfig.param('tInterrupt')
        self.on_BufferSize_Changed()
        
        self.RowsConfig.sigTreeStateChanged.connect(self.on_RowsConfig_Changed)
        self.on_RowsConfig_Changed()
        self.FsScope.sigValueChanged.connect(self.on_FsScope_Changed)
        self.tInterrupt.sigValueChanged.connect(self.on_BufferSize_Changed)

    def on_RowsConfig_Changed(self):
        self.Rows = []
        for p in self.RowsConfig.children():
            if p.param('Enable').value():
                self.Rows.append(p.name())
        self.NRows.setValue(len(self.Rows))
       
    def on_FsScope_Changed(self):
        self.on_BufferSize_Changed()
        
    def on_BufferSize_Changed(self):
        Fs = self.FsScope.value()
        tF = self.tInterrupt.value()
        Samples = round(tF*Fs)
        tF = Samples/Fs
        self.tInterrupt.setValue(tF)
        self.BufferSize.setValue(Samples)
     
    def GetRowParams(self):
        '''
        Generates a dictionary with Active Rows properties and Adq properties
        
        Scope={'RowsConfig': {'Row1': {'Enable': True, 
                                          'Index': 0, 
                                          'AcqVRange': 1}, 
                                 'Row2': {'Enable': True, 
                                          'Index': 1, 
                                          'AcqVRange': 1}, 
                                 'Row3': {'Enable': True, 
                                          'Index': 2, 
                                          'AcqVRange': 1}, 
                                 'Row4': {'Enable': True, 
                                          'Index': 3, 
                                          'AcqVRange': 1}, 
                                 'Row5': {'Enable': True, 
                                          'Index': 4, 
                                          'AcqVRange': 1}, 
                                 'Row6': {'Enable': True, 
                                          'Index': 5, 
                                          'AcqVRange': 1}, 
                                 'Row7': {'Enable': True, '
                                          Index': 6, 
                                          'AcqVRange': 1}, 
                                 'Row8': {'Enable': True, 
                                          'Index': 7, 
                                          'AcqVRange': 1}
                                 }, 
                  'FsScope': 2000000.0, 
                  'BufferSize': 1000000, 
                  'NRow': 8, 
                  'OffsetRows': 0, 
                  'GainBoard': 10000.0, 
                  'ResourceScope': 'PXI1Slot4'
                  }
        '''
        Scope = {'RowsConfig':{},
                }
        for Config in self.RowsConfig.children():
            if Config.param('Enable').value() == True:
                Scope['RowsConfig'][Config.name()]={}
                for Values in Config.children():
                    if Values == 'Enable':
                        continue
                    Scope['RowsConfig'][Config.name()][Values.name()] = Values.value()
        for Config in self.AcqConfig.children():
            if Config.name() =='tFetch':
                continue
            Scope[Config.name()] = Config.value()

        return Scope
    
    def GetRows(self):
        '''
        Generates a dictionary with Rows Actives and their index
        
        RowNames={'Row1': 0, 
                  'Row2': 1, 
                  'Row3': 2, 
                  'Row4': 3, 
                  'Row5': 4, 
                  'Row6': 5, 
                  'Row7': 6, 
                  'Row8': 7}
        '''
        RowNames = {}
        for i,r in enumerate(self.Rows):
            RowNames[r]=i
        return RowNames
    
    def GetRowsList(self):
        RowsList = []
        for i,r in enumerate(self.Rows):
            RowsList.append(r)
        return RowsList
        

            
            
        
