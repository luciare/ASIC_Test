#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on march 2020
Python 3.7
@author: jcisneros
"""
import numpy as np
import matplotlib.pyplot as plt

# import binascii
import time

import ok

DEBUG = True

from bitstring import ConstBitStream

    #WIRE IN    

Add_Reset_MOD_IN = 0x00

Add_dataclk_M_D_IN = 0x01  #M -->{ 1'b0, ep01wirein[15:8] };  D--> { 1'b0, ep01wirein[7:0] };

Add_LED_IN = 0x02
                                                            
Add_DATA_IO_to_ASIC_W_IN = 0x03      
                                                      
Add_DATA_DAC_SPI_EL = 0x04 #DATA del DAC (Din)
Add_DATA_DAC_SPI_E = 0x06 #DATA del DAC (Din)
Add_DATA_DAC_SPI_COL = 0x05 #DATA del DAC (Din)

Add_OSC_Reset = 0x10
Add_SAR_Reset = 0x11

Add_ADD_AS = 0x12
Add_DATA_AS = 0x13
                                                            
    #WIRE OUT    
Add_LSB_NumWords_Out = 0x20
Add_MSB_NumWords_Out = 0x21
                          
Add_MSB_Magic_Header_Out = 0x22
Add_LSB_Magic_Header_Out = 0x23
                          
Add_DCM_Prog_And_Locked_OUT = 0x24 #Wireout25 { 14'b0, DCM_prog_done, dataclk_locked };

Add_dataclk_M_OUT = 0x25   #{8'b0,dataclk_M};
Add_dataclk_D_OUT = 0x26   #{8'b0,dataclk_D};

Add_MODE_0_1_OUT = 0x27     #{ 14'b0, MODE_1_W,MODE_0_W};
Add_CCLK_ACQS_HZ_OUT = 0x28     #{ 14'b0, CCLK_W,ACQS_HZ};

Add_LED_R_OUT = 0x29     #LED_R;

Add_DATA_IO_to_ASIC_W_OUT =0x2a 
                            
Add_DATA_DAC_SPI_OUT = 0x32

    #TRIGGER IN                                              
Add_triggerin_DCM_Prog = 0x40
Add_triggerin_RAM = 0x41
Add_triggerin_Run = 0x42
Add_triggerin_SPI = 0x43

Add_PipeOut_RAM = 0xa0


MAGIC_HEADER = 0xC791199927021942

###########ADD ASIC#############3
ADD_ASIC_Gen_COL = [1,2,3,4]

ADD_ASIC_AFE_ROW = [5,6,7,8,9,10,11,12]

ADD_ASIC_SAR_ROW = [13,14,15,16,17,18,19,20]

ADD_ASIC_CLKI_DIV = 21

################constantes

Transition_Time = 1;
usb3 = 0

#################rutinas

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

Dac_Dic ={
    #Freq: M, D
    "EL": Add_DATA_DAC_SPI_EL, 
    "E": Add_DATA_DAC_SPI_E,   
    "COL": Add_DATA_DAC_SPI_COL,   
    }

Row_Translator = { '0' : (0,0),
                   '1' : (0,1),
                   '2' : (0,2),
                   '3' : (0,3),
    }

Gain_AFE = { 2 : 0,
             4 : 1,
             8 : 2,
             16 :3   
    }

class ASIC_Error(Exception):
    pass

class ASIC:
    
    def Error(self,Arg,Exc):
        if(Exc):
            raise ASIC_Error(Arg)
        else:
            print (Arg)
        

    def __init__(self,Clk_Freq_D=Clk_Freq_D, Dac_Dic=Dac_Dic, Row_Translator = Row_Translator, Gain_AFE = Gain_AFE, MAGIC_HEADER=MAGIC_HEADER ,Fclk = "27MHz",DEBUG = 0):
        
        self.Clk_Freq_D = Clk_Freq_D
        self.Dac_Dic = Dac_Dic
        self.Row_Translator = Row_Translator
        self.Gain_AFE = Gain_AFE
        self.MAGIC_HEADER = MAGIC_HEADER
        self.Fclk = Fclk
        self.FS = float(self.Fclk[:-3])*1.0e6
        self.DEBUG = DEBUG
        self.Transition_Time = 0.1
        
        self.xem = ok.FrontPanel()

        if(self.xem.OpenBySerial("") == -1):
            self.Error("FPGA BOARD NOT CONNECTED?",1)
            
        #Config Board + Bitstream
        if(self.Config_Board()):
            self.Error("ERROR Config_Board()" ,1)
        #Reset
        self.Reset_Board()
        
        #PLL Frequency
        self.DCM_Config_New_Freq(CLK = self.Fclk)
        
        #RAM TEST
        if(self.Ram_test(self.MAGIC_HEADER)):
            self.Error("ERROR RAM TEST",0)
            
            
    def Config_Board(self):
        if self.DEBUG:
            print ("#################### INIT BOARD ######################")
    
        Board_Model = self.xem.GetBoardModel()
        g = 1
        if Board_Model == 13:
            if(self.DEBUG):
                print ("Connected Dev = XEM6110LX45")
            g = self.xem.ConfigureFPGA('mainant.bit')
        
        
        if Board_Model == 21:
            if(self.DEBUG):
                print ("Connected Dev = XEM6310LX45")
            g = self.xem.ConfigureFPGA('main.bit')
            global usb3 
            usb3= 1
    #        a = xem.ConfigureFPGA('main_x.bit')
        #xem.LoadDefaultPLLConfiguration()
        
        #LED_FRONTAL PARPADEO COMPROBACION BIT_STREAM
        a=self.xem.SetWireInValue(Add_Reset_MOD_IN,0x00) #Reseteo inicial
        b=self.xem.SetWireInValue(Add_DATA_IO_to_ASIC_W_IN,0x00) #Reseteo inicial
                                
        c=self.xem.SetWireInValue(Add_LED_IN,0xFF)
        d=self.xem.UpdateWireIns()
        time.sleep(1)
        e=self.xem.SetWireInValue(Add_LED_IN,0x00)
        f=self.xem.UpdateWireIns()
        
        if (self.DEBUG and abs(a+b+c+d+e+f+g)>0):
            print ("ERROR Config_Board " + str(a+10*b+100*c+1000*d+10000*e+100000*f+1000000*g)  )   
        if self.DEBUG:
            print ("#################### INIT BOARD END ##################")
        return a+b+c+d+e+f+g

    def Reset_Board(self):
        #El reset arrancara la maquina de estados y el DCM
        
        #xem.SetWireInValue(Direccion,Valor,PosicionVector)
        a = self.xem.SetWireInValue(Add_Reset_MOD_IN,0x01,0x01)
        b = self.xem.UpdateWireIns()        
        time.sleep(0.1)
        c = self.xem.SetWireInValue(Add_Reset_MOD_IN,0x00,0x01)
        d = self.xem.UpdateWireIns()    
        time.sleep(1)
    
        if (self.DEBUG and (a+b+c+d)>0):
            print ("ERROR Reset_Board " + str(a+10*b+100*c+1000*d))   
      
        return a+b+c+d

    def Reset_SDRam(self):
        #El reset solo afecta la SDRam i la maquina de estados de la lectura
        
        #xem.SetWireInValue(Direccion,Posicion,Valor)
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,7, 1)      
        time.sleep(0.1)
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,7, 0)      
        time.sleep(1)
    
        if (self.DEBUG and (a+b)>0):
            print ("ERROR Reset_Board " + str(a+10*b))     
      
        return a+b
    
    
    def DCM_Config_New_Freq(self,CLK):
        
        if(DEBUG):
            print ("")
            print ("############ DCM New Frequency fo clkout #############")
    
    #==============================================================================
    # // Assuming a 100 MHz reference clock is provided to the module, the output frequency is given
    # // by:
    # //       clkout frequency = 100 MHz * (M/D) / 2 el dos es por la salida de CLK CLKFXDV
    # //
    # // Restrictions:  M must have a value in the range of 2 - 256
    # //                D must have a value in the range of 1 - 256
    # //                M/D must fall in the range of 0.05 - 3.33
    #==============================================================================
            
        a= 0
        b = 0
        c = 0
        d = 0
        timeout = time.time() + 60*1   # 5 minutes from now
        #Esperar a que el DCM estigui programat per poder tornar a programar
        while True:
            Res_already_prog = self.IsDcmProgDone_and_locked()
            if (Res_already_prog > 0)  or time.time() > timeout:
                break
        
        if(Res_already_prog > 0):
            #Add_dataclk_M_D_IN = 0x01  #M -->{ 1'b0, ep01wirein[15:8] };  D--> { 1'b0, ep01wirein[7:0] };
        
            #Val M i D
            Val_M_D = (256*self.Clk_Freq_D[CLK][0] +self.Clk_Freq_D[CLK][1])    
            a = self.xem.SetWireInValue(Add_dataclk_M_D_IN,Val_M_D)
            b = self.xem.UpdateWireIns()
            #delay
            time.sleep(0.5)
            c = self.xem.UpdateWireOuts()    
            M_Rec = self.xem.GetWireOutValue(Add_dataclk_M_OUT)    
            D_Rec = self.xem.GetWireOutValue(Add_dataclk_D_OUT)    
    
            if(DEBUG):
                print ("Freq= " + CLK +" Sel M/D= " + str(self.Clk_Freq_D[CLK][0]) + "/" + str(self.Clk_Freq_D[CLK][1]) + " Read M/D= " + str(M_Rec) + "/" + str(D_Rec) )
        
            d = self.xem.ActivateTriggerIn(Add_triggerin_DCM_Prog, 0)
            
            timeout = time.time() + 60*1   # 5 minutes from now
            while True:
                Res_already_prog = self.IsDcmProgDone_and_locked()
                if (Res_already_prog > 0)  or time.time() > timeout:
                    Res_already_prog = 20
                    break
            
        else:
            a = 1;
            if(DEBUG):
                if(Res_already_prog == 20):
                    print ("First Timeout exceeded you should Reset_Board()")
                else:
                    print ("Second Timeout exceeded you should Reset_Board()")
    
        if (DEBUG and (a+b+c+d)>0):
            print ("ERROR DCM_Config_New_Freq " + str(a+10*b+100*c+1000*d))  
        if DEBUG:
            print ("############ DCM New Frequency fo clkout END #########")
        return a+b+c+d


    
    def IsDcmProgDone_and_locked(self):
        #Indica el LOCK del PLL
        self.xem.UpdateWireOuts()
        
    #    0x24 --> { 14'b0, DCM_prog_done, dataclk_locked };
        Data0x24 = self.xem.GetWireOutValue(Add_DCM_Prog_And_Locked_OUT)
        return Data0x24

    def NumOfWordsRam(self):
        
        self.xem.UpdateWireOuts()
        MSB_Words = self.xem.GetWireOutValue(Add_MSB_NumWords_Out)    
        LSB_Words = self.xem.GetWireOutValue(Add_LSB_NumWords_Out)    
    
        return (MSB_Words <<16) + LSB_Words


    def Ram_test(self,HEADER):
        
        ##MUX para Recibir senyal de clock del PLL
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 0)      
        time.sleep(0.1)
        ###
        
        # HEADER = MAGIC_HEADER
        N_ANS = self.NumOfWordsRam()
        d = self.xem.ActivateTriggerIn(Add_triggerin_RAM, 0)
        time.sleep(10)
        N_ACT_W = self.NumOfWordsRam()
        R1 = 1
        F1_S = "W_&_R Fail"
        R1_S = "Fail"
        N_ACT_R = 0
        
        if DEBUG:
            print ("")
            print ("#################### RAM_TEST ########################")
            
        if(N_ACT_W > N_ANS):
        
            Buffer = bytearray(1024)
            self.xem.ReadFromBlockPipeOut(0xa0, 1024, Buffer)
            
            Data_C = self.ByteArrayToDec(Buffer[0:8])
            
            N_ACT_R = 512-(N_ACT_W - self.NumOfWordsRam())
                
            F1 = 0
            F1_S = "W_&_R Perfect"
    
            if(N_ACT_R >0):
                F1 = 2
                F1_S = "W_Ok R_Fail Perfect"
    
            else:
                if(Data_C == HEADER):
                    R1 = 0
                    R1_S = "HEADER Perfect"
                else:
                    R1 = 1
                    R1_S = "HEADER Wrong"
        else:
            F1 = 1
            F1_S = "W_&_R Fail"
            R1_S = "Fail"
    
        
        if DEBUG:
    #        print ""
    #        print "################# RAM_TEST ##########################"
            print ("NOfW_INIT= " + str(N_ANS) + " NOfW_AFT_W= " +str(N_ACT_W) + " NOfW_AFT_R= " +str(N_ACT_R) )
            print ("ERRORS=  " + F1_S + " Header= " + R1_S + "    Code " + str(R1*10+F1+d) )
            print ("#################### RAM_TEST END ####################" )
    
        return R1*10+F1+d


    def ByteArrayToDec(self,Buff_Int):   
        Data_C = 0
        for i,n in enumerate(Buff_Int):
            Data_C += n*(2**(8*i))     #Formato antiguo 
            
        return Data_C  

    def ByteArrayToDecNova(self,Buff_Int):   
        Data_C = 0
        for i,n in enumerate(Buff_Int):
            Data_C += n*(2**(8*(1-i)))  
            #Data_C += n*(2**(8*i))     #Formato antiguo 
            
        return Data_C  
    
    def Switch_ON_OFF_WireInPos(self,Address,Posicio, ON):
        
        a = self.xem.SetWireInValue(Address,ON*2**Posicio,2**Posicio)
        b = self.xem.UpdateWireIns()  
        if (self.DEBUG and (a+b)>0):
            print ("ERROR Switch_ON_OFF_WireInPos " + str(a+10*b) + " ADD " + str(Address))
          
        return a + b

    
    def Asic_Off(self):
        time.sleep(Transition_Time)
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,1, 0) #MODE 0
        c = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,2, 0) #MODE 1
        
        if (self.DEBUG and (b+c)>0):
            print ("ERROR Asic_Off " + str(10*b+100*c) )    
      
        return b+c
        
    def Asic_Write(self):
    
        time.sleep(self.Transition_Time)
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,1, 0) #MODE 0
        c = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,2, 1) #MODE 1
        time.sleep(Transition_Time)
        
        if (self.DEBUG and (b+c)>0):
            print ("ERROR Asic_Write " + str(10*b+100*c))      
              
        return b+c
    
    def Asic_Read(self):
        time.sleep(self.Transition_Time)
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,1, 1) #MODE 0
        c = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,2, 1) #MODE 1
    
        if (self.DEBUG and (b+c)>0):
            print ("ERROR Asic_Read " + str(10*b+100*c) )    
            
        return b+c


    def ASIC_PBx(self,val):
        
        Dic ={
            0: (0,0), 
            4: (0,0),   
            8: (0,1),   
            16: (1,0),
            32:(1,1)
        }
        #Rutina encender o apagar los OSC reset General
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,5, Dic[val][1]) #PB0
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,6, Dic[val][0]) #PB1
        time.sleep(self.Transition_Time)
        
        return b

    def ASIC_Mx(self,Rst,ON):
        #Rutina encender o apagar los OSC reset General
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,3, ON) #M0
        b = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,4, Rst) #M1
        time.sleep(self.Transition_Time)
        
        return b


    def Asic_DAC(self,DAC,Valor):
        #EJEMPLO: Asic_DAC_EL(0.001)
        
        # Dac_Dic ={
        #     #Freq: M, D
        #     "EL": Add_DATA_DAC_SPI_EL, 
        #     "E": Add_DATA_DAC_SPI_E,   
        #     "COL": Add_DATA_DAC_SPI_COL,   
        #     }
        
        
        if(Valor >=1.8): 
            Valor = 1.8
            
        Result = int((Valor/1.8)*2**16 - 1)
        
        if(Valor <=0): 
            Result = 0 
        

        a = self.xem.SetWireInValue(self.Dac_Dic[DAC],Result)

        b = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 1) #RUN DAC
    
        
        if (DEBUG and (a+b+c)>0):
            print ("ERROR SPI DAC " + str(a+10*b+100*c) )    
            
        return a+10*b+100*c

    def Asic2_Row_AFE_SAR(self,B,F,Gain,ON,RST):
        
        Gain = self.Gain_AFE[Gain]
        
        a = self.Asic_Write()
           
        if(Gain >=3): 
            Gain = 3
    
        if(RST >=1): 
            RST = 1 
            
        if(ON >=1): 
            ON = 1 
            
        if(B>=7):
            B = 7
        
        if(F >= 3):
            F =3
        
        ADD = (B<<5) + (F<<3)+6
        
        Result = (ON <<15)+(RST <<14)+ Gain
        
        if self.DEBUG:
            print ("ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.1)
    
        # Asic_CCLK_Pulse()
        
        if (self.DEBUG and (a+b+c)>0):
            print ("ERROR Asic2_AFE_SAR" + str(a+10*b+100*c) )    
            
        return a+b+c
    
    
    def Asic2_AFE_CAN(self,B,F,Vect_IN):
        ### Vect_IN = [0,0,0,0] MSB....LSB
        self.Asic_Write()
        
        if(B>=7):
            B = 7
        
        if(F >= 3):
            F =3
        
        if len(Vect_IN) > 32 :
            print("Input VECTOR larger than 32")
            Vect_IN = Vect_IN[:(32-len(Vect_IN))]
        
        if len(Vect_IN) <32:
            print("Input VECTOR len < 32 -> adding zeros")
            Vect_IN = np.append(np.zeros(32-len(Vect_IN),int), Vect_IN)    
        
        Roff_0 = []
        Roff_1 = []
        Roff_2 = []
        
        for n in range(len(Vect_IN)):
            if (Vect_IN[n] >= 7):
                Roff_0.append(1)
                Roff_1.append(1)
                Roff_2.append(1)
                
            if (Vect_IN[n] == 6):
                Roff_0.append(0)
                Roff_1.append(1)
                Roff_2.append(1)
        
            if (Vect_IN[n] == 5):
                Roff_0.append(1)
                Roff_1.append(0)
                Roff_2.append(1)
        
            if (Vect_IN[n] == 4):
                Roff_0.append(0)
                Roff_1.append(0)
                Roff_2.append(1)
        
            if (Vect_IN[n] == 3):
                Roff_0.append(1)
                Roff_1.append(1)
                Roff_2.append(0)
        
            if (Vect_IN[n] == 2):
                Roff_0.append(0)
                Roff_1.append(1)
                Roff_2.append(0)
        
            if (Vect_IN[n] == 1):
                Roff_0.append(1)
                Roff_1.append(0)
                Roff_2.append(0)
        
            if (Vect_IN[n] == 0):
                Roff_0.append(0)
                Roff_1.append(0)
                Roff_2.append(0)
        
        Roff_0_R1 = 0
        Roff_1_R3 = 0
        Roff_2_R5 = 0
        
        for p in range(0,16):
            # print(p)    
            Roff_0_R1 += Roff_0[p]*2**(31-p)
            Roff_1_R3 += Roff_1[p]*2**(31-p)
            Roff_2_R5 += Roff_2[p]*2**(31-p)
        
        Roff_0_R0 = 0
        Roff_1_R2 = 0
        Roff_2_R4 = 0
        
        for p in range(16,32):
            # print(p)    
            Roff_0_R0 += Roff_0[p]*2**(31-p)
            Roff_1_R2 += Roff_1[p]*2**(31-p)
            Roff_2_R4 += Roff_2[p]*2**(31-p)
        
        #R0
        ADD = (B<<5) + (F<<3)
        Result = Roff_0_R0
        
        if self.DEBUG:
            print ("R0 ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.2)
        
        #R1
        ADD = (B<<5) + (F<<3) + 1
        Result = Roff_0_R1
        
        if self.DEBUG:
            print ("R1 ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.2)
        
        #R2
        ADD = (B<<5) + (F<<3) + 2
        Result = Roff_1_R2
        
        if self.DEBUG:
            print ("R2 ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.2)
        
        #R3
        ADD = (B<<5) + (F<<3) + 3
        Result = Roff_1_R3
        
        if self.DEBUG:
            print ("R3 ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.2)
        
        #R4
        ADD = (B<<5) + (F<<3) + 4
        Result = Roff_2_R4
        
        if self.DEBUG:
            print ("R4 ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.2)
        
        #R5
        ADD = (B<<5) + (F<<3) + 5
        Result = Roff_2_R5
        
        if self.DEBUG:
            print ("R5 ADD ",bin(ADD)," DATA ",str(bin(Result)))
            
        b = self.xem.SetWireInValue(Add_ADD_AS,ADD)
        b = self.xem.SetWireInValue(Add_DATA_AS,Result)
        c = self.xem.UpdateWireIns() 
        time.sleep(0.01)
        c = self.xem.ActivateTriggerIn(Add_triggerin_SPI, 2) #RUN SPI
        time.sleep(0.2)

    def Dict_To_Instruction(self,DIC):
            
        Data_Gen_Buffer = DIC['children']
        
        Name_Dict = DIC['name']
        
        if Name_Dict == 'GeneratorConfig' :
                
            for n,c in enumerate(Data_Gen_Buffer):
                
                if(c['name'] == 'FsClock'):
                    if(self.DEBUG):
                        print(c['name'])
                        
                    #Se puede hacer una lista de frequencias??
                    Freq = str(c['value']) +c['suffix'] 
                    self.FS = float(c['value'])*1.0e6
                    self.DCM_Config_New_Freq(Freq)    
                    DCM_Prog_Lock = self.IsDcmProgDone_and_locked()
                    
                if(c['name'][0:3] == 'DAC'):
                    if(self.DEBUG):
                        print(c['name'])
                        
                    #Se pueden poner limites en el tree? La misma que el Clk_Freq_D
                    self.Asic_DAC(c['name'][4:],c['value'])
                    time.sleep(0.1) #Pongo un timer porque no se que tardara el SPI en enviar el dato
              
                if(c['name'] == 'SCAN'):
                    if(self.DEBUG):
                        print(c['name'])
                        
                    #Se pueden poner una lista? [4,8,16,32]
                    self.ASIC_PBx(c['value'])
                    time.sleep(0.1) #Pongo un timer porque no se que tardara el SPI en enviar el dato
                
                if(c['name'] == 'MASTER'):
                    if(DEBUG):
                        print(c['name'])
                        
                    #ARRANQUE DE FREQUENCIAS
                    if c['value']:
                        self.ASIC_Mx(Rst=0,ON=1)
                        time.sleep(0.1)
                        self.ASIC_Mx(Rst=1,ON=1)
                        time.sleep(0.1)
                    
                    else:
                        self.ASIC_Mx(Rst=0,ON=0)
                        time.sleep(0.1)
    
        if Name_Dict == 'RowConfig' :
                
            for n,c in enumerate(Data_Gen_Buffer):
                
                
                if(c['name'][0:3] == 'Row'):
                    if(self.DEBUG):
                        print(c['name'])
                    
                    ##Primero se tiene que configurar y despues encender la fila
                    B = self.Row_Translator[c['name'][4:]][0]
                    F = self.Row_Translator[c['name'][4:]][1]
                    
                    Vect_IN = c['children'][2]['value']
                    
                    self.Asic2_AFE_CAN(B,F,Vect_IN)
                    time.sleep(0.1)
                    
                    #Encendemos si se tiene que encender
                    if(c['children'][0]['value']):
                        Gain = c['children'][1]['value']
                        if(DEBUG):
                            print ("ENCENDEMOS FILA ", c['name'][4:], " Gain " ,Gain)
                        self.Asic2_Row_AFE_SAR(B = B ,F = F ,Gain = Gain ,ON = 1 ,RST = 0)
                        time.sleep(0.1)
                        self.Asic2_Row_AFE_SAR(B = B ,F = F ,Gain = Gain ,ON = 1 ,RST = 1)
                        time.sleep(0.1)
                    
    def ConfigAcq(self,DICS):
        #Encendemos las referencias de corriente del AS
        self.Asic_Write()
        time.sleep(0.1)
        
        for i in DICS:
            self.Dict_To_Instruction(i)
        
    def ReadAcqL(self):
        
        self.Asic_Read()
        time.sleep(10)
        
            
    def Single_Run(self):
        
        ##MUX para Recibir senyal de clock de la FPGA
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 0)      
        time.sleep(0.3)    

        ##Encendemos el asic i lo ponemos en modo lectura
        self.Asic_Read()
        self.Reset_SDRam()
        time.sleep(0.3)    
        
        ##MUX para Recibir senyal de clock del ASIC
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 1)      
        
        time.sleep(1)
    
        d = self.xem.ActivateTriggerIn(Add_triggerin_Run, 0)
        
        time.sleep(1)
        # FPGA_SAR_ON(1) #Arranca el SCLK DESCOMENTAR PARA PATTERN
    
        
        start_time = time.time()
        Salida = 1
        while(Salida):
            self.xem.UpdateWireOuts()
            if(self.xem.GetWireOutValue(0x2f)):    #chivato Ram_Full_Indicator
              Salida = 0
    #          print "Salida"
            time.sleep(1)
            if(time.time()>= (start_time+20000)):
              Salida = 0
              if(self.DEBUG):
                  print ("TimeOut")
    
    
        
        if(self.NumOfWordsRam() < 2**26):  
            if(self.DEBUG):
                print ("Not enough Words in Ram second atempt " + str(self.NumOfWordsRam()) + " Words 67108864")
            self.Reset_SDRam()
            time.sleep(1)
            d = self.xem.ActivateTriggerIn(Add_triggerin_Run, 0)
            
            start_time = time.time()
            Salida = 1
            while(Salida):
                self.xem.UpdateWireOuts()
                if(self.xem.GetWireOutValue(0x2f)):    #chivato
                  Salida = 0
                  if(self.DEBUG):
                      print ("Salida")
                time.sleep(1)
                if(time.time()>= (start_time+20000)):
                  Salida = 0
                  if(self.DEBUG):
                      print ("TimeOut")  
                      
        ##MUX para Recibir senyal de clock de la FPGA
        time.sleep(0.1)              
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 0)  


    def FPGA_SAR_ON(self,val):
        #Rutina encender o apagar los OSC reset General
        b = self.Switch_ON_OFF_WireInPos(Add_SAR_Reset,0, val) #reset local 
        time.sleep(0.1)
        return b
    
    
    def Single_R_to_Buffer(self):
        
        if(self.NumOfWordsRam() >= 2**26):    
            
            Runs_Completos = int(self.NumOfWordsRam() / (2560000/2.0))
                                          
            Buffer_Fetch = self.Fetch(Runs_Completos)
    
            
            if(len(Buffer_Fetch) != 1280000*Runs_Completos*2): #word to byte "*2"
                print ("ERROR Diff Fetch length than expected" )
                
            else:
                if DEBUG:
                    print ("Fetch Perfecto...")
                         
        else:
            Buffer_Str = "-1"
    
        return Buffer_Fetch

    def Fetch(self,Runs_Completos):
        if self.DEBUG:
            print ("Fetch ")
            
        Buffer_R = []
        Contador = 1
        for b in range(int(Runs_Completos)):
            
    #        Buffer = bytearray(1024*2*2*2*2*2*2*2)    #max size without usb3 problems
            # se traduce de palabras de 16 bits a bytes de 8 bits por eso el factor 2 de fuera con el de dentro
            # igualmente la memoria maxima es de 2**26 = 67108864 entonces con la configuracion actual se aprovechan 
            # 17 runs completos * 2560000 * 0.5 para passar de bytes a words * 3 pasadas para que quede completo i el siguiente 
            #fetch tenga la cabecera en su sitio = 65280000 de palabras
            # (16.0 steps sar * 17 runs completos * 2560000 bytes * 0.5 word/byte * 3.0 pasadas)/(12.0 palabras por muestra * 27e6 clock sar) = 3.22 segundos 
            
            Buffer = bytearray(2560000)    #max size without usb3 problems
            # Buffer = bytearray(1024*2*2*2*2)    #max size without usb3 problems
            e = self.xem.ReadFromBlockPipeOut(0xa0, 512, Buffer)   
            if(b == 0):
                Buffer_R = Buffer
            else:
                Buffer_R = Buffer_R + Buffer
            if DEBUG:    
                Proceso = (b/(Runs_Completos))*100.0
                if(Proceso>=10*Contador):
                    print (str(10*Contador) + " %")
                    Contador += 1
                if(b>=int(Runs_Completos)-1):
                    print ("100 %")
                    
        return Buffer_R


    def Bitstream_to_Sep(self,Buffer_Str):
        #Buscamos el inicio
        Indice = 0
        # for n in range(len(Buffer_Str)-7):
        # for n in range(len(Buffer_Str)-12):
            
        #     # if(Buffer_Str[n:n+7] == '1000101'):
        #     if(Buffer_Str[n:n+12] == '100010100000'):
        #         Indice = n
        #         break
        # #otra forma de buscar el indice    
        # Indice_1 = Buffer_Str.find('100010100000') 
        
        
        for n in range(len(Buffer_Str)-64+8+4):
            # if(Buffer_Str[n:n+7] == '1000101'):
            #if((Buffer_Str[n:n+12] == '100010100000') and (Buffer_Str[n+64:n+64+8+4] == '100010100001')):
            if((Buffer_Str[n:n+8] == '10100000') and (Buffer_Str[n+60:n+64+8] == '100010100001')):
                Indice = n
                break
            
        #separamos cada sar contador etc
        CAB = []
        COL = []
        SAR_0 = []
        SAR_1 = []
        SAR_2 = []
        SAR_3 = []
        FOOT = []
        
        # Indice = Indice + 4
        Buffer_Str_S = Buffer_Str[Indice:]
        
        for r in range(int((len(Buffer_Str_S))/64.0)):
            # r = 1
            DATAP = Buffer_Str_S[r*64:r*64+64]
            # print(r)
            CAB.append(int(DATAP[0:3],2))
            COL.append(int(DATAP[3:8],2))
            SAR_0.append(int(DATAP[8:21],2))
            SAR_1.append(int(DATAP[21:34],2))
            SAR_2.append(int(DATAP[34:47],2))
            SAR_3.append(int(DATAP[47:60],2))
            FOOT.append(int(DATAP[60:64],2))
        
        CAB = np.array(CAB)
        COL = np.array(COL)
        SAR_0 = np.array(SAR_0)
        SAR_1 = np.array(SAR_1)
        SAR_2 = np.array(SAR_2)
        SAR_3 = np.array(SAR_3)
        
        Time_Stamp_Diff = np.diff(CAB)
        
        Error = len(np.where(Time_Stamp_Diff != 0)[0]) # si la diferencia entre ellos es uno entonces esta bien
       
        if (CAB[0] == 0) or (CAB[0] !=5):
            Error = Error +1
            
        if(Error):
            print ("ERROR Salto ")
        
        return Error,COL,SAR_0,SAR_1,SAR_2,SAR_3

    def ReadAcqL(self):
        
        if(self.DEBUG):
            print ("")
            print ("#################### SINGLE LONG RUN AS2 ######################")
        
        self.Asic_Read()
        time.sleep(10)
        
        if(self.DEBUG):
            Inicio = time.time()
        
        ##encendemos el ASIC en modo lectura i esperamos a que se llene la RAM
        self.Single_Run()
        
        ##Fetch del ByteArray
        Buffer_Fetch = self.Single_R_to_Buffer()
    
        if(self.DEBUG):
            print("Tiempo Captura= " , time.time()-Inicio, " s")
    
            Inicio = time.time()
            print("Bitstream INIT...")
        
        ##Pasamos el byte array a bitstring
        Buffer_bitstream =ConstBitStream(Buffer_Fetch)
        Buffer_Str = Buffer_bitstream.bin 
        
        if(self.DEBUG):
             print("Bistream_Completo..." ,time.time()-Inicio, " s")
             print("Parsing...")
        Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.Bitstream_to_Sep(Buffer_Str=Buffer_Str)
        
        if(self.DEBUG):
            print("Parsing_Completo...")
            print("Tiempo Fetch Parsing antiguo= " , time.time()-Inicio, " s")
            print ("")
            print ("#################### SINGLE LONG RUN AS2 END ####################")

        return Error,Col,Sar_0,Sar_1,Sar_2,Sar_3
    
    def ReadAcqS(self):
        
        if(self.DEBUG):
            print ("")
            print ("#################### SINGLE SHORT RUN AS2 ######################")
        
        self.Asic_Read()
        time.sleep(10)
        
        if(self.DEBUG):
            Inicio = time.time()
        
        ##encendemos el ASIC en modo lectura i esperamos a que se llene la RAM
        self.Single_Run_E()
        
        # FPGA_SAR_ON(1) #Arranca el SCLK Solo para Pattern Gen
        
        Salida = 1
        while(Salida):
            # if(NumOfWordsRam() >= (1024*2*2*2*2)*5):
            if(self.NumOfWordsRam() >= 1024*3):
                Salida = 0;

        Buffer_Fetch = self.FetchS()
        
        if(self.DEBUG):
            print("Tiempo Captura= " , time.time()-Inicio, " s")
    
            Inicio = time.time()
            print("Bitstream INIT...")
        
        Buffer_Str = self.Buffer_Fetch_to_Bitstream(Buffer_Fetch=Buffer_Fetch)
        
        if(self.DEBUG):
             print("Bistream_Completo..." ,time.time()-Inicio, " s")
             print("Parsing...")
             
        Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.Bitstream_to_Sep(Buffer_Str=Buffer_Str)


        # ##Volvemos a poner el MUX en la posicion de PLL 
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 0)  
        time.sleep(0.1)
        # FPGA_SAR_ON(0) 
                

        if(self.DEBUG):
            print("Parsing_Completo...")
            print("Tiempo Fetch Parsing antiguo= " , time.time()-Inicio, " s")
            print ("")
            print ("#################### SINGLE SHORT RUN AS2 END ####################")

        return Error,Col,Sar_0,Sar_1,Sar_2,Sar_3


    def Single_Run_E(self):
    
        ##MUX para Recibir senyal de clock del ASIC
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 0)      
        time.sleep(0.1)
        
        ##Encendemos el asic i lo ponemos en modo lectura
        self.Asic_Read()
        self.Reset_SDRam()
        time.sleep(0.1)    
        
        ##MUX para Recibir senyal de clock del ASIC
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 1)      
        
        time.sleep(0.1)
    
        d = self.xem.ActivateTriggerIn(Add_triggerin_Run, 0)
        
        return d+a

    def FetchS(self):        
            
        Buffer_R = []
        
    #        Buffer = bytearray(1024*2*2*2*2*2*2*2)    #max size without usb3 problems
        # se traduce de palabras de 16 bits a bytes de 8 bits por eso el factor 2 de fuera con el de dentro
        # igualmente la memoria maxima es de 2**26 = 67108864 entonces con la configuracion actual se aprovechan 
        # 17 runs completos * 2560000 * 0.5 para passar de bytes a words * 3 pasadas para que quede completo i el siguiente 
        #fetch tenga la cabecera en su sitio = 65280000 de palabras
        # (16.0 steps sar * 17 runs completos * 2560000 bytes * 0.5 word/byte * 3.0 pasadas)/(12.0 palabras por muestra * 27e6 clock sar) = 3.22 segundos 
        
        # Buffer = bytearray(2560000)    #max size without usb3 problems
        Buffer = bytearray(1024)    #max size without usb3 problems
        e = self.xem.ReadFromBlockPipeOut(0xa0, 512, Buffer)   
        Buffer_R = Buffer
                
        return Buffer_R

    def Buffer_Fetch_to_Bitstream(self,Buffer_Fetch):
        #segunda version
        #convertimos el bitstream a un str ordenado
        Buffer_Str = ""
        Intermedio = ""
        for j in range(int(len(Buffer_Fetch)/2)):
            # print("pointer ",j , " Entre " , j*2 , " y " , j*2+2)
            # print(ByteArrayToDec(Buffer_Fetch[j*2:j*2+2]))
            if(bin(self.ByteArrayToDecNova(Buffer_Fetch[j*2:j*2+2]))== '0b0'):
                Intermedio = "0000000000000000"
            else:
                Intermedio = bin(self.ByteArrayToDecNova(Buffer_Fetch[j*2:j*2+2]))[2:]
                for i in range(16-len(Intermedio)):
                    Intermedio = '0' + Intermedio
            Buffer_Str = Buffer_Str + Intermedio
        
        return Buffer_Str
        
    
    def Save_File(self,path,Data_X,Data_Y):
        
        wfile = open(path,'w')
        
        for n in range(len(Data_X)-2):
            wfile.write(str(Data_X[n]) +"\t"+str(Data_Y[n])+"\n")
    
    
    def Gravar_M_Conversion(self,path,filename,Data,Limite,Conversion):
        
        path = path +"/"+ filename
        
        # Limite = 1066
        # FS = 1687500.0
        FSampling = (self.FS/2.0)/32.0
        
        Y_Data = []
        if(len(Data)>= Limite):
            Limites = Limite - 2
        else:
            Limites = len(Data) -2 
            
        X_Data = np.arange(0.0,Limites*1.0/FSampling,1.0/FSampling)
           
        Y_Data = Data[:Limites]
        #Conversion 
        if Conversion:
            # Conversion = 2.0*(4095-(2**(13.0-1))+0.5)/2**13.0
            Y_Data = 2.0*(Y_Data-(2**(13.0-1))+0.5)/2**13.0
        
        self.Save_File(path = path,Data_X=X_Data,Data_Y=Y_Data)

   

    def Save_File_ByteArray(self,path,Data):
        
        wfile = open(path,'wb')
        wfile.write(Data)
        
    def Open_File_ByteArray(self,path):
        
        wfile = open(path,'rb')
        return wfile.read()
    
    def Conversion(self,Data, FS):
        
        FS = FS/(2.0*32.0)
        X_Data = np.arange(0.0,len(Data)*1.0/FS,1.0/FS)
           
        # Conversion = 2.0*(4095-(2**(13.0-1))+0.5)/2**13.0
        Y_Data = 2.0*(Data-(2**(13.0-1))+0.5)/2**13.0
            
        return X_Data, Y_Data



#############################################################MAIN
                           
if __name__ == '__main__':

    

    AS2 = ASIC(DEBUG =1)
    
    #CONFIGURACION DACS i AUXILIARES
    GeneratorConfig =  {'name': 'GeneratorConfig',
                           'type': 'group',
                           'children':({'name': 'FsClock',
                                        'title': 'AS Clock Frequency',
                                        'type': 'float',
                                        'readonly': True,
                                        'value': 27,
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
                                        'value': 4,
                                        'type': 'int',
                                        'siPrefix': True, ###FALSE??
                                        'suffix': ''},     
                                       {'name': 'MASTER',
                                        'title': 'Master ON',
                                        'value': False,
                                        'type': 'bool',
                                        'siPrefix': True, ###FALSE??
                                        'suffix': ''},     
                                       
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
                                                 'type': 'int',
                                                 'value': 2,},
                                               {'name':'Offset Vector',
                                                'type': 'int', ##Lista de valores???
                                                'readonly': True,
                                                'value': [0,0,0,0,1]})}, ##La lista deberia de ser hasta 32 posiciones
                                  {'name':'Row 1',
                                   'type': 'group',
                                   'children':({'name': 'Enable',
                                                 'type': 'bool',
                                                 'value': False,},
                                               {'name': 'Gain',
                                                 'type': 'int',
                                                 'value': 2,},
                                               {'name':'Offset Vector',
                                                'type': 'int', ##Lista de valores???
                                                'readonly': True,
                                                'value': [0,0,0,0,0]})}, ##La lista deberia de ser hasta 32 posiciones
                                  {'name':'Row 2',
                                   'type': 'group',
                                   'children':({'name': 'Enable',
                                                 'type': 'bool',
                                                 'value': False,},
                                               {'name': 'Gain',
                                                 'type': 'int',
                                                 'value': 2,},
                                               {'name':'Offset Vector',
                                                'type': 'int', ##Lista de valores???
                                                'readonly': True,
                                                'value': [0,0,0,0,0]})}, ##La lista deberia de ser hasta 32 posiciones

                                  {'name':'Row 3',
                                   'type': 'group',
                                   'children':({'name': 'Enable',
                                                 'type': 'bool',
                                                 'value': False,},
                                               {'name': 'Gain',
                                                 'type': 'int',
                                                 'value': 2,},
                                               {'name':'Offset Vector',
                                                'type': 'int', ##Lista de valores???
                                                'readonly': True,
                                                'value': [0,0,0,0,0]})}, ##La lista deberia de ser hasta 32 posiciones

                                            ) 
                               }
    
    # AS2.Dict_To_Instruction(GeneratorConfig)
    # AS2.Dict_To_Instruction(RowConf)
    # Esto seria en el start de la gui y tendrias:
    # ASICTree.GetGenParams() y ASICTree.GetRowsParams()
    DICS = [GeneratorConfig,RowConf]
    AS2.ConfigAcq(DICS)
    
    #Long Run
    # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.ReadAcqL()
    
    #Short Run
    Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.ReadAcqS()
    
    
    
    # AS2.ASIC_Off()
    
    #Gravar en fichero

    letra = '2000504_Sar_CDS_11111111111'
    
    path_f = "/home/jcisneros/Downloads/DAta_rouleta"
    
    file_name = "SAR_0_AS2t" + letra + ".txt"
    
    
    AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_0,Limite= len(Sar_0),Conversion=1)
    
    file_name = "SAR_1_AS2t" + letra + ".txt"
    
    AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_1,Limite= len(Sar_1),Conversion=1)
    
    file_name = "SAR_2_AS2t" + letra + ".txt"
    
    AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_2,Limite= len(Sar_2),Conversion=1)
    
    file_name = "SAR_3_AS2t" + letra + ".txt"
    
    AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_3,Limite= len(Sar_3),Conversion=1)
    
