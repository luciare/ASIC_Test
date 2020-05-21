# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:18:09 2020

@author: lucia
"""
import numpy as np

def Open_File_ByteArray(path):
    
    wfile = open(path,'rb')
    return wfile.read()

def Buffer_Fetch_to_Bitstream(Buffer_Fetch):
    #segunda version
    #convertimos el bitstream a un str ordenado 
    Buffer_Str = ""
    Intermedio = ""
    for j in range(int(len(Buffer_Fetch)/2)):
        if(bin(ByteArrayToDec(Buffer_Fetch[j*2:j*2+2]))== '0b0'):
            Intermedio = "0000000000000000"
        else:
            Intermedio = bin(ByteArrayToDec(Buffer_Fetch[j*2:j*2+2]))[2:]
            for i in range(16-len(Intermedio)):
                Intermedio = '0' + Intermedio
        Buffer_Str = Buffer_Str + Intermedio
    
    return Buffer_Str

def ByteArrayToDec(Buff_Int):   
    Data_C = 0
    for i,n in enumerate(Buff_Int):
        
        Data_C += n*(2**(8*i))      
        
    return Data_C  

def Conversion(Data, FS):
    
    X_Data = np.arange(0.0,len(Data)*1.0/FS,1.0/FS)
       
    # Conversion = 2.0*(4095-(2**(13.0-1))+0.5)/2**13.0
    Y_Data = 2.0*(Data-(2**(13.0-1))+0.5)/2**13.0
        
    return X_Data, Y_Data