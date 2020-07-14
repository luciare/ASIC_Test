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

from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes


if __name__ == '__main__':
    
    import ok
    MainRoute = './main.bit'

else:
    import JoseCodes.ok as ok
    MainRoute = './JoseCodes/main.bit'


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

Dic_PB ={
    1: (0,0),
    4: (0,0),   
    8: (0,1),   
    16: (1,0),
    32:(1,1)
}

####################DAC CAL
Vres_EL =[2.36,7.14,11.91,16.75,21.55,26.35,31.13,35.92,40.71,45.48,50.28,55.07,59.85,64.64,
       69.42,74.21,79.0,83.78,88.56,93.36,98.14,102.93,107.73,112.53,117.32,122.11,126.90,
       131.69,136.48,141.26,146.05,150.83,155.63,160.42,165.20,169.99,174.78,179.56,184.36,
       189.15,193.93,198.72,203.51,208.30,213.10,217.91,222.69,227.48,232.25,237.05,241.84,
       246.62,251.40,256.19,260.97,265.76,270.54,275.32,280.10,284.89,289.68,294.47,299.25,
       304.03,308.82,313.60,318.39,323.18,327.98,332.77,337.55,342.33,347.13,351.92,356.71,
       361.50,366.28,371.08,375.87,380.66,385.44,390.23,395.02,399.82,404.61,409.39,414.17,
       418.96,423.75,428.55,433.36,438.14,442.93,447.71,452.51,457.31,462.10,466.88,471.67,
       476.45,481.25,486.04,490.82,495.61,500.39,505.18,509.98,514.76,519.55,524.34,529.12,
       533.92,538.70,543.52,548.31,553.10,557.89,562.70,567.48,572.27,577.07,581.85,586.65,
       591.45,596.23,601.02,605.82,610.60,615.40,620.19,624.98,629.77,634.56,639.35,644.14,
       648.96,653.75,658.55,663.33,668.13,672.93,677.72,682.50,687.30,692.09,696.89,
       701.68,706.46,711.26,716.05,720.84,725.65,730.43,735.22,740.02,744.80,749.61,754.40,
       759.22,764.02,768.81,773.60,778.40,783.20,787.98,792.77,797.55,802.34,807.15,811.92,
       816.71,821.50,826.28,831.09,835.89,840.70,845.49,850.28,855.06,859.87,864.68,869.47,
       874.26,879.04,883.83,888.62,893.41,898.21,903.02,907.80,912.60,917.37,922.16,926.96,
       931.76,936.54,941.33,946.11,950.91,955.72,960.51,965.31,970.09,974.90,979.71,984.51,
       989.29,994.09,998.88,1003.66,1008.46,1013.25,1018.04,1022.83,1027.61,1032.41,1037.23,
       1042.02,1046.81,1051.59,1056.38,1061.18,1065.98,1070.77,1075.55,1080.36,1085.16,
       1089.96,1094.74,1099.56,1104.33,1109.11,1113.91,1118.72,1123.50,1128.30,1133.09,
       1137.88,1142.68,1147.48,1152.27,1157.06,1161.84,1166.64,1171.44,1176.22,1181.01,
       1185.80,1190.64,1195.4,1200.20,1205.0,1209.8,1214.5,1219.3,1224.1,1228.9,1233.7,
       1238.5,1243.2,1248.0,1252.8,1257.6,1262.4,1267.2,1272.0,1276.8,1281.6,1286.4,1291.1,
       1295.9,1300.7,1305.5,1310.3,1315.1,1319.9,1324.7,1329.5,1334.3,1339.1,1343.8,1348.6,
       1353.4,1358.2,1363.0,1367.8,1372.6,1377.3,1382.1,1386.9,1391.7,1396.5,1401.3,1406.1,
       1410.9,1415.7,1420.5,1425.3,1430.0,1434.8,1439.6,1444.4,1449.2,1454.0,1458.7,1463.5,
       1468.3,1473.1,1477.9,1482.7,1487.4,1492.2,1497.0,1501.8,1506.6,1511.4,1516.1,1521.0,
       1525.8,1530.5,1535.3,1540.1,1544.9,1549.7,1554.5,1559.3,1564.1,1568.8,1573.6,1578.4,
       1583.2,1588.0,1592.8,1597.6,1602.4,1607.1,1611.9,1616.7,1621.5,1626.3,1631.1,1635.9,
       1640.7,1645.5,1650.3,1655.1,1659.9,1664.7,1669.4,1674.2,1679.0,1683.8,1688.6,1693.4,
       1698.1,1702.9,1707.7,1712.4,1717.3,1722.1,1726.9]

Vres_COL =[2.88,5.80,9.53,13.80,28.34,23.01,27.71,32.44,37.18,41.94,46.72,51.50,56.27,61.05,
       65.83,70.62,75.41,80.20,84.97,89.75,94.52,99.32,104.12,108.92,113.70,118.48,123.28,
       128.07,132.86,137.63,142.42,147.19,151.98,156.78,161.56,166.35,171.13,175.90,180.70,
       185.50,190.27,195.05,199.83,204.63,209.42,214.24,219.01,223.79,228.56,233.35,238.14,
       242.92,247.70,252.48,257.27,262.07,266.87,271.64,276.43,281.20,285.99,290.78,295.57,
       300.35,305.12,309.90,314.70,319.50,324.31,329.10,333.87,338.65,343.44,348.23,353.02,
       357.80,362.57,367.36,372.16,376.93,381.72,386.50,391.28,396.08,400.88,405.66,410.44,
       415.22,420.01,424.80,429.63,434.40,439.18,443.95,448.76,453.56,458.34,463.12,467.89,
       472.68,477.48,482.27,487.05,491.83,496.60,501.40,506.20,511.0,515.77,520.55,525.33,
       530.11,534.90,539.70,544.48,549.27,554.05,558.84,563.64,568.42,573.20,577.97,582.78,
       587.59,592.38,597.15,601.94,606.74,611.52,616.34,621.10,625.88,630.67,635.45,640.25,
       645.07,649.85,654.62,659.41,664.20,669.01,673.8,678.57,683.34,688.13,692.93,697.74,
       702.51,707.29,712.06,716.85,721.67,726.45,731.24,736.03,740.82,745.61,750.40,755.22,760.00,
       764.77,769.57,774.36,779.16,783.93,788.70,793.46,798.25,803.04,807.83,812.60,817.38,
       822.15,826.94,831.73,836.52,841.29,846.07,850.85,855.64,860.45,865.23,870.01,874.79,
       879.56,884.35,889.13,893.92,898.71,903.50,908.28,913.07,917.85,922.64,927.43,932.21,
       937.01,941.78,946.57,951.36,956.13,960.91,965.70,970.51,975.31,980.10,984.88,989.67,
       994.47,999.25,1004.05,1008.85,1013.64,1018.41,1023.20,1027.99,1032.78,1037.56,1042.35,
       1047.14,1051.92,1056.72,1061.51,1066.28,1071.07,1075.88,1080.67,1085.46,1090.25,1095.03,
       1099.83,1104.61,1109.41,1114.20,1119.00,1123.78,1128.57,1133.37,1138.14,1142.95,1147.73,
       1152.51,1157.29,1162.07,1166.85,1171.63,1176.41,1181.21,1186.01,1190.81,1195.60,
       1200.4,1205.2,1210.0,1214.7,1219.5,1224.3,1229.1,1233.9,1238.7,1243.5,1248.3,1253.0,
       1257.8,1262.6,1267.4,1272.2,1277.0,1281.8,1286.5,1291.4,1296.1,1300.9,1305.7,1310.5,
       1315.3,1320.1,1324.9,1329.7,1334.5,1339.2,1344.0,1348.8,1353.6,1358.4,1363.2,1367.9,
       1372.7,1377.5,1382.3,1387.1,1391.9,1396.6,1401.5,1406.2,1411.0,1415.8,1420.6,1425.4,
       1430.2,1434.9,1439.7,1444.5,1449.3,1454.1,1458.9,1463.6,1468.4,1473.2,1478.0,1482.8,
       1487.6,1492.4,1497.2,1501.9,1506.7,1511.5,1516.3,1521.1,1525.9,1530.7,1535.5,1540.3,
       1545.1,1549.8,1554.6,1559.4,1564.2,1569.0,1573.8,1578.6,1583.4,1588.2,1593.0,1597.8,
       1602.5,1607.3,1612.1,1616.9,1621.7,1626.5,1631.3,1636.1,1640.9,1645.7,1650.5,1655.3,
       1660.1,1664.9,1669.6,1674.4,1679.2,1684.0,1688.8,1693.6,1698.4,1703.2,1708.0,1712.8,
       1717.6,1722.4]

Vres_E =[8.18,12.22,16.65,21.25,25.93,30.64,35.38,40.13,44.89,49.65,54.44,59.22,63.99,
       68.76,73.53,78.32,83.11,87.90,92.68,97.48,102.25,107.05,111.84,116.66,121.45,
       126.24,131.04,135.84,140.64,145.43,150.23,155.01,159.81,164.61,169.40,174.18,
       178.97,183.77,188.56,193.35,198.15,202.93,207.70,212.50,217.31,222.13,226.93,
       231.72,236.51,241.31,246.12,250.91,255.70,260.49,265.27,270.07,274.86,279.63,
       284.42,289.20,293.99,298.78,303.58,308.36,313.14,317.92,322.71,327.52,332.32,
       337.11,341.90,346.69,351.49,356.30,361.08,365.87,370.65,375.46,380.25,385.05,
       389.84,394.62,399.41,404.20,408.99,413.78,418.57,423.37,428.16,432.95,437.77,
       442.55,447.33,452.11,456.92,461.73,466.51,471.30,476.08,480.87,485.66,490.48,
       495.27,500.06,504.85,509.86,514.44,519.21,524.01,528.79,533.59,538.39,543.18,
       548.00,552.80,557.59,562.37,567.17,571.97,576.76,581.54,586.33,591.13,595.93,
       600.72,605.49,610.27,615.07,619.88,624.68,629.46,634.25,639.04,643.84,648.63,
       653.46,658.24,663.03,667.81,672.62,677.43,682.21,687.00,691.78,696.50,701.37,
       706.16,710.93,715.73,720.53,725.32,730.12,734.91,739.69,744.48,749.27,754.06,
       758.85,763.67,768.45,773.24,778.04,782.83,787.62,792.40,797.2,801.99,806.79,
       811.58,816.38,821.11,825.95,830.74,835.54,840.35,845.14,849.91,854.72,859.51,
       864.31,869.13,873.92,878.70,883.49,888.30,893.07,897.86,902.66,907.47,912.25,
       917.04,921.83,926.60,931.40,936.20,941.00,945.79,950.58,955.36,960.15,964.95,
       969.74,974.54,979.35,984.13,988.92,993.72,998.50,1003.29,1008.08,1012.89,1017.68,
       1022.46,1027.25,1032.03,1036.84,1041.63,1046.42,1051.21,1056.01,1060.79,1065.58,
       1070.39,1075.18,1079.98,1084.40,1089.58,1094.39,1099.18,1103.97,1108.77,1113.55,
       1118.35,1123.16,1127.95,1132.74,1137.54,1142.33,1147.10,1151.90,1156.68,1161.48,
       1166.27,1171.05,1175.84,1180.64,1185.44,1190.23,1195.05,1199.85,1204.70,1209.50,
       1214.2,1219.0,1223.9,1228.6,1233.4,1238.2,1243.0,1247.8,1252.6,1257.4,1262.2,1267.0,
       1271.8,1276.6,1281.4,1286.2,1290.9,1295.7,1300.0,1305.4,1310.2,1315.0,1319.8,1324.5,
       1329.4,1334.1,1338.9,1343.7,1348.5,1353.3,1358.1,1362.9,1367.7,1372.5,1377.3,1382.1,
       1386.9,1391.7,1396.5,1401.03,1406.1,1410.9,1415.7,1420.5,1425.3,1430.1,1434.8,1439.6,
       1444.4,1449.2,1454.0,1458.8,1463.6,1468.4,1473.2,1478.0,1482.8,1487.6,1492.4,1497.2,
       1502.0,1506.8,1511.6,1516.4,1521.2,1526.0,1530.8,1535.6,1540.4,1545.2,1550.0,1554.8,
       1559.6,1564.4,1569.2,1574.0,1578.8,1583.6,1588.4,1593.2,1598.0,1602.8,1607.6,1612.4,
       1617.2,1622.0,1626.8,1631.6,1636.5,1641.3,1646.0,1650.9,1655.7,1660.5,1665.3,1670.1,
       1674.9,1679.7,1684.5,1689.3,1694.1,1698.9,1703.7,1708.5,1713.3,1718.1,1722.9,1727.7,
       1732.6
       ]
           

Vres = {"EL" : Vres_EL,
        "COL" : Vres_COL,
        "E" : Vres_E,
        }

class ASIC_Error(Exception):
    pass

class ASIC():

    def Error(self,Arg,Exc):
        if(Exc):
            raise ASIC_Error(Arg)
        else:
            print (Arg)
        

    def __init__(self,Clk_Freq_D=Clk_Freq_D, Dac_Dic=Dac_Dic, Row_Translator = Row_Translator, Gain_AFE = Gain_AFE, MAGIC_HEADER=MAGIC_HEADER ,Fclk = "27MHz",Vres = Vres,DEBUG = 0):
        # super permits to initialize the classes from which this class depends
        
        print("#########INIT CLASS")
        self.Clk_Freq_D = Clk_Freq_D
        self.Dac_Dic = Dac_Dic
        self.Row_Translator = Row_Translator
        self.Gain_AFE = Gain_AFE
        self.MAGIC_HEADER = MAGIC_HEADER
        self.Fclk = Fclk
        self.FS = float(self.Fclk[:-3])*1.0e6
        self.DEBUG = DEBUG
        self.Transition_Time = 0.1
        
        # self.Vres = np.array(Vres)/1000.0
        # Vg = np.arange(0.0,1.805,5e-3)       
        # z = np.polyfit(self.Vres, Vg, 3)
        # self.PolyDAC = np.poly1d(z)   
        
        self.Vres = Vres
        Vg = np.arange(0.0,1.805,5e-3)       
        self.Vres_Dic = {}
        for n in self.Vres:
            z = np.polyfit(np.array(self.Vres[n])/1000.0, Vg, 3)
            self.Vres_Dic[n] = np.poly1d(z) 
            # print (n)
        
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
        
        self.tInterrupt = 1000
        self.Runs_Completos = 4
        self.LimiteRuns = 40
            
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
            
            # g = self.xem.ConfigureFPGA('./JoseCodes/main.bit') ##ALTANTO
            g = self.xem.ConfigureFPGA(MainRoute) ##ALTANTO
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
            1: (0,0), 
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
                    
        Valor = self.Vres_Dic[DAC](Valor)
                        
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
        self.OutData = Buffer_Fetch

        if(self.DEBUG):
            print("Tiempo Captura= " , time.time()-Inicio, " s")
    
            Inicio = time.time()
        #     print("Bitstream INIT...")
        
        # ##Pasamos el byte array a bitstring
        # Buffer_bitstream =ConstBitStream(Buffer_Fetch)
        # Buffer_Str = Buffer_bitstream.bin 
        
        # if(self.DEBUG):
        #      print("Bistream_Completo..." ,time.time()-Inicio, " s")
        #      print("Parsing...")
        # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.Bitstream_to_Sep(Buffer_Str=Buffer_Str)
        
        # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 =self.Sep_From_ByteArray(Buffer_Fetch)
        Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.ByteArrayToReshapeSar(Buffer_Fetch)

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
        self.OutData = Buffer_Fetch
        
        if(self.DEBUG):
            print("Tiempo Captura= " , time.time()-Inicio, " s")
    
            Inicio = time.time()
        #     print("Bitstream INIT...")
        
        # Buffer_Str = self.Buffer_Fetch_to_Bitstream(Buffer_Fetch=Buffer_Fetch)
        
        # if(self.DEBUG):
        #      print("Bistream_Completo..." ,time.time()-Inicio, " s")
        #      print("Parsing...")
             
        # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.Bitstream_to_Sep(Buffer_Str=Buffer_Str)

        # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 =self.Sep_From_ByteArray(Buffer_Fetch)
        Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.ByteArrayToReshapeSar(Buffer_Fetch)



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

    
    def Dict_To_InstructionSimple(self,Data_Gen_Buffer):
                   
        for n,c in enumerate(Data_Gen_Buffer):
                
                if(c == 'FsClock'):
                    if(self.DEBUG):
                        print(c ,Data_Gen_Buffer[c])               
                    
                    #Se puede hacer una lista de frequencias??
                    Freq = Data_Gen_Buffer[c]
                    
                    self.FS = float(Freq[:-3])*1.0e6
                    self.DCM_Config_New_Freq(Freq)    
                    DCM_Prog_Lock = self.IsDcmProgDone_and_locked()
                
                if(c[0:3] == 'DAC'):
                    if(self.DEBUG):
                        print(c ,Data_Gen_Buffer[c])
        
                    #Se pueden poner limites en el tree? La misma que el Clk_Freq_D
                    self.Asic_DAC(c[4:],Data_Gen_Buffer[c])
                    time.sleep(0.1) #Pongo un timer porque no se que tardara el SPI en enviar el dato
               
                if(c == 'SCAN'):
                    if(self.DEBUG):
                        print(c ,Data_Gen_Buffer[c])
                        
                    #encendemos el asic    
                    self.Asic_Write()
                    #Se pueden poner una lista? [4,8,16,32]
                    self.ASIC_PBx(Data_Gen_Buffer[c])
                    time.sleep(0.1) #Pongo un timer porque no se que tardara el SPI en enviar el dato
                
                if(c == 'MASTER'):
                    if(self.DEBUG):
                        print(c ,Data_Gen_Buffer[c])
                    
                    #ARRANQUE DE FREQUENCIAS
                    if Data_Gen_Buffer[c]:
                        self.ASIC_Mx(Rst=0,ON=1)
                        time.sleep(0.1)
                        self.ASIC_Mx(Rst=1,ON=1)
                        time.sleep(0.1)
                    
                    else:
                        self.ASIC_Mx(Rst=0,ON=0)
                        time.sleep(0.1)
            
                if(c[0:3] == 'Row'):
                    if(self.DEBUG):
                        print(c ,Data_Gen_Buffer[c]) 
                   
                    ##Primero se tiene que configurar y despues encender la fila
                    B = self.Row_Translator[c[4:]][0]
                    F = self.Row_Translator[c[4:]][1]
            
                    if (isinstance(Data_Gen_Buffer[c]['Offset Vector'],list)):
                        
                        Vect_IN = Data_Gen_Buffer[c]['Offset Vector']
                    else:
                        Vect_IN = np.array([Data_Gen_Buffer[c]['Offset Vector']])
        
                    self.Asic2_AFE_CAN(B,F,Vect_IN)
                    time.sleep(0.1)  
            
                    #Encendemos si se tiene que encender
                    if(Data_Gen_Buffer[c]['Enable']):
                        Gain = Data_Gen_Buffer[c]['Gain']
                        if(DEBUG):
                            print ("ENCENDEMOS FILA ", c[4:], " Gain " ,Gain)
                        self.Asic2_Row_AFE_SAR(B = B ,F = F ,Gain = Gain ,ON = 1 ,RST = 0)
                        time.sleep(0.1)
                        self.Asic2_Row_AFE_SAR(B = B ,F = F ,Gain = Gain ,ON = 1 ,RST = 1)
                        time.sleep(0.1)


    def StopRun(self):
        
        self.Asic_Write()
        time.sleep(0.1)

        # ##Volvemos a poner el MUX en la posicion de PLL 
        ##Uno es para poder hacer multirun i el otro para la senyal externa del pll
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,9, 0)  #Senyal externa
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,8, 0) #Senyal multiRub

        time.sleep(0.1)


    def RunLocal(self):
        '''
        Run function in threads is the loop that will start when thread is
        started.
        Returns
        -------
        None.
        '''
        # while True statement is used to generate a lopp in the run function
        # so, while the thread is active, the while loop is running
        
        #Asic en modo lectura
        self.Asic_Read()
        
        a = self.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,8, 1)      
        time.sleep(10)
        
        ##encendemos el ASIC en modo lectura i esperamos a que se llene la RAM
        self.Single_Run_E()
        self.inte = 0
        
        #Buffer ByteArray
        self.OutData = []

        # while True:
        Salida = 1
        while(Salida):            
            # the generation is started
            # The dictionary SigConfig is passed to SignalGenerator class as
            # kwargs, this means you can send the full dictionary and only use
            # the variables in which you are interesed in
            
            #Unidad minima son 1024 bytes (las palabras con de 2 bytes)
            #Cada RunCompleto equivale a 2560000 bytes 
            #Si FS = 27MHz tenemos 27e6/2.0/32.0 = 421875 Hz cada trama de 64 bits
            #Entonces 2560000 bytes * 8 / 64 bits = 320000 Tramas
            #En tiempo seria 320000 Tramas / 421875 Hz = 0.75 segundos de captura
            
            if(self.NumOfWordsRam() >= 2*(2560000*self.Runs_Completos/2.0)):
                
                Buffer = self.Fetch(self.Runs_Completos)
                
                if(self.inte == 0):
                    self.OutData =  Buffer
                else:
                    self.OutData = self.OutData + Buffer
                
                self.inte = self.inte + 1
            
            time.sleep(1)
            print("Inside RunLocal " , self.NumOfWordsRam(), " int ", self.inte )
            
            if(self.inte >= self.LimiteRuns):
                print("End RunLocal")
                # break
                Salida = 0
            
        #Paramos el ASIC
        self.StopRun()
        
    def Conver(self,Data,Scale):
        Y_Data = 2.0*(Data-(2**(13.0-1))+0.5)/2**13.0
        if Scale:
            Y_Data = Y_Data/4.0/25e3
        return Y_Data
            
        
    def Bitstream_to_Matrix(self,Buffer_Str,nCols,nChannels,Scale):
        #Buscamos el inicio
        Indice = 0      
        
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
            
        ##BUFFER SALIDA
        X_Axis = COL
        nsamples = int(len(X_Axis)/nCols)
        Buffer_Matrix = np.zeros((nsamples,nChannels))
            
        if(Error):
            print ("ERROR Salto ")

        else:      
            
            #Si es igual a 1 no hi ha 
            if nCols == 1:
                Buffer_Matrix[:,0] = COL
                Buffer_Matrix[:,1] = COL
                Buffer_Matrix[:,2] = COL
                Buffer_Matrix[:,3] = COL
            else:        
                
                Contador = 0
                for pos,val in enumerate(X_Axis):
            
                    Buffer_Matrix[Contador][val] = self.Conver(SAR_0[pos],0)
                    Buffer_Matrix[Contador][val+nCols] = self.Conver(SAR_1[pos],0)
                    Buffer_Matrix[Contador][val+2*nCols] = self.Conver(SAR_2[pos],0)
                    Buffer_Matrix[Contador][val+3*nCols] = self.Conver(SAR_3[pos],0)
                    
                    if val == nCols-1:
                        Contador = Contador + 1
        
        return Buffer_Matrix
          
    
    def ByteArrayToReshape(self,Buffer_Fetch,Gain_Vec,nCols,nChannels,ScaleVgs = 0):
        
        Gain_Vec = 1.0/(2*25e3*np.array(Gain_Vec)) #########DESCOMENTAR
        
        dt = np.dtype('uint16')
        dt = dt.newbyteorder('>') ##Atento byte order
        
        Buffer_np = np.frombuffer(Buffer_Fetch, dtype=dt) 
                
        if(np.where(Buffer_np[0:20] == 5)[0][0] != 0):
            print("INDICE RECIBIDO DISTINTO DE 5@pos0")
        
        nVector = int(len(Buffer_np)/8.0) #Son 8 palabras o 16 bytes
    
        Buffer_np = Buffer_np.reshape((nVector,8))

        Buffer_np = 2.0*((np.abs(np.array([8191,8191,0,0]) - Buffer_np[:, 2:-2]))-(2**(13.0-1))+0.5)/2**13.0
            
        Buffer_np = Buffer_np * np.array([(Gain_Vec[0]),(Gain_Vec[1]),(Gain_Vec[2]),(Gain_Vec[3])]) ##ERROR EN LA PCB
    
        Buffer_np = np.reshape(Buffer_np,(int(nVector/nCols),nChannels))
        
        return Buffer_np
    
    def ByteArrayToReshapeSar(self,Buffer_Fetch):
        dt = np.dtype('uint16')
        dt = dt.newbyteorder('>') ##Atento byte order
        
        Buffer_np = np.frombuffer(Buffer_Fetch, dtype=dt) 
        
        Error = 0
        
        if(np.where(Buffer_np[0:20] == 5)[0][0] != 0):
            print("INDICE RECIBIDO DISTINTO DE 5@pos0")
            Error = 1
        
        nVector = int(len(Buffer_np)/8.0) #Son 8 palabras o 16 bytes
    
        Buffer_np = Buffer_np.reshape((nVector,8))
        
        # Buffer_np = 2.0*(Buffer_np[:, 2:-2]-(2**(13.0-1))+0.5)/2**13.0
        Buffer_np = Buffer_np[:, 1:-2]
        
        # Buffer_np = Buffer_np * np.array([(Gain_Vec[0]),(Gain_Vec[1]),(Gain_Vec[2]),(Gain_Vec[3])])
        Col = Buffer_np[:,0]
        Sar_0 = 8191-Buffer_np[:,1]
        Sar_1 = 8191-Buffer_np[:,2]
        Sar_2 = Buffer_np[:,3]
        Sar_3 = Buffer_np[:,4]
        
        return Error,Col,Sar_0,Sar_1,Sar_2,Sar_3    
    
    
    def GlobalVREFE(self, Vmin,Vmax,Steps,nChannels,nCols,DIC_C):
        
        DIC_R = {'Row 0': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
                 'Row 1': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
                 'Row 2': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
                 'Row 3': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]}}
        
        self.Dict_To_InstructionSimple(DIC_C) 
        self.Dict_To_InstructionSimple(DIC_R)
        
        Vcancel = np.linspace(Vmin,Vmax,Steps)
        Vres = np.ones(len(Vcancel))*9999
        Vres_min = 99999
        for n,val in enumerate(Vcancel):
            print ('IT ',n , ' Val ', val)
            DIC_C = {'DAC E': val}
            self.Dict_To_InstructionSimple(DIC_C)
            time.sleep(5)
            
            Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = self.ReadAcqS()
            # plt.plot(Sar_0)
            
            self.StopRun()
           
            Buffer = self.ByteArrayToReshape(Buffer_Fetch=self.OutData,Gain_Vec=[1,1,1,1],nCols=nCols,nChannels=nChannels)        
            Buffer = np.abs(Buffer)    
            Vres[n] = np.sum(Buffer ,axis = 1)[-1]
            print ('IT ',n , ' Val ', val, ' Res ', Vres[n])
            if(Vres_min >= Vres[n]):
                Vres_min = Vres[n]
            else:
                break
    
        print('MinVal for VREF_E ' ,Vcancel[np.where(Vres == np.min(Vres))[0][0]],' V')
        
        # plt.figure(1000)
        # plt.plot(Vcancel,Vres)
    
        return Vcancel[np.where(Vres == np.min(Vres))[0][0]]

    
    def ParamCalc(self,DIC_R,DIC_C,nCols,nChannels):
        Trans = {
                0: 14286.6,
                1: 12500.775,
                2: 11111.80,
                3: 10000.62,
                4:  9091.472,
                5:  8333.85,
                6:  7692.78,
                7:  7143.3
            }
        
        VREF_E = DIC_C['DAC E']
        
        I_Vec = np.zeros((nChannels))
        Gain_Vec = np.ones((len(DIC_R)))
        
        for t,val in enumerate(DIC_R):
            Gain_Vec[t] = DIC_R[val]['Gain']
            for u in range(nCols):
                # print(t+u*4)
                # print(DIC_R[val]['Offset Vector'][-1-u])
                I_Vec[t+u*4] = Trans[DIC_R[val]['Offset Vector'][-1-u]]
                
        I_Vec = (0.8991-VREF_E)/I_Vec
        # I_Vec = Buffer + I_Vec
    
        return I_Vec,Gain_Vec

class ThreadAcq(Qt.QThread):
    NewGenData = Qt.pyqtSignal()
    def __init__(self,ASP,nChannels,nCols,DIC_C,DIC_R):
        super(ThreadAcq, self).__init__()
        self.ASP = ASP
        
        self.nChannels = nChannels
        self.nCols = nCols
        self.DIC_R = DIC_R
        self.DIC_C = DIC_C
        
        self.EndCap = 0
        
        #Lista tareas
        self.Lista = None
        
        self.I_Vec,self.Gain = self.ASP.ParamCalc(DIC_R = self.DIC_R, DIC_C = self.DIC_C, nCols = self.nCols, nChannels = self.nChannels)
        
    
    def run(self):
        '''
        Run function in threads is the loop that will start when thread is
        started.
        Returns
        -------
        None.
        '''
        # while True statement is used to generate a lopp in the run function
        # so, while the thread is active, the while loop is running
        
        #Asic en modo lectura
        self.ASP.Asic_Read()
        
        a = self.ASP.Switch_ON_OFF_WireInPos(Add_Reset_MOD_IN,8, 1)   
        
        # self.ASP.FPGA_SAR_ON(1) #Arranca el SCLK Solo para Pattern Gen
        
        time.sleep(1)
        
        ##encendemos el ASIC en modo lectura i esperamos a que se llene la RAM
        self.ASP.Single_Run_E()
        
        self.inte = 0
        while True:
            # the generation is started
            # The dictionary SigConfig is passed to SignalGenerator class as
            # kwargs, this means you can send the full dictionary and only use
            # the variables in which you are interesed in
            
            #Unidad minima son 1024 bytes (las palabras con de 2 bytes)
            #Cada RunCompleto equivale a 2560000 bytes 
            #Si FS = 27MHz tenemos 27e6/2.0/32.0 = 421875 Hz cada trama de 64 bits
            #Entonces 2560000 bytes * 8 / 64 bits = 320000 Tramas
            #En tiempo seria 320000 Tramas / 421875 Hz = 0.75 segundos de captura
            
            if(self.Lista is not None):
                self.ASP.Dict_To_InstructionSimple(self.Lista)
                self.ASP.Single_Run_E()
                self.Lista = None
                print("GALLINA")
            
            if(self.ASP.NumOfWordsRam() >= 2*(2560000*self.ASP.Runs_Completos/2.0)):
                
                if(self.EndCap == 2):
                    self.EndCap = 1
                else:
                    
                    Buffer_Fetch = self.ASP.Fetch(self.ASP.Runs_Completos)
                     
                    
                    OutData_Temp = self.ASP.ByteArrayToReshape(Buffer_Fetch,
                                                               Gain_Vec = self.Gain,
                                                               nCols = self.nCols,
                                                               nChannels = self.nChannels)
                    
                    self.OutData =self.I_Vec + OutData_Temp
                    
                    # print('Buffer',self.OutData[:1,:16])
    
                    self.NewGenData.emit()
                    self.inte = self.inte + 1
            
            print("Inside Run " , self.ASP.NumOfWordsRam(), " int ", self.inte )
            self.EndCap = 0

            Qt.QThread.msleep(self.ASP.tInterrupt)

#############################################################MAIN
                           
if __name__ == '__main__':

    

    AS2 = ASIC(DEBUG =1)
    
   
    ##NUEVA VERSION
    DIC_C = {'FsClock': '27MHz',
             'DAC EL': 0.9,
             'DAC E': 0.9,
             'DAC COL': 0.9,
             'SCAN': 4,
             'MASTER': False}
    
    #NUEVA VERSION
    # DIC_C = {'FsClock': '27MHz',
    #           'DAC EL': 1.2,
    #           'DAC E': 0.80,
    #           'DAC COL': 0.9+16e-3,
    #           # 'DAC COL': 0.9+0.3,
    #           'SCAN': 4,
    #           'MASTER': False}
    
    # DIC_R = {'Row 0': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,4,3,2,1]},
    #           'Row 1': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,2,1,4]},
    #           'Row 2': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,2,1,4,3]},
    #           'Row 3': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,1,4,3,2]}}
    
    DIC_R = {'Row 0': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
         'Row 1': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
         'Row 2': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
         'Row 3': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]}}
   
    DIC_R = {'Row 0': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
         'Row 1': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
         'Row 2': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]},
         'Row 3': {'Enable': True, 'Gain': 2, 'Offset Vector': [3,3,3,3,3,3,3,3,3]}}    
    AS2.Dict_To_InstructionSimple(DIC_C)
    AS2.Dict_To_InstructionSimple(DIC_R)
    
    a[0]
    # AS2.FPGA_SAR_ON(1) ##Pattern generation
    
    #Long Run
    Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.ReadAcqL()
    
    #Short Run
    Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.ReadAcqS()
    # a[0]

    
    Sar_0_I = 2.0*(Sar_0-(2**(13.0-1))+0.5)/2**13.0
    Sar_1_I = 2.0*(Sar_1-(2**(13.0-1))+0.5)/2**13.0
    Sar_2_I = 2.0*(Sar_2-(2**(13.0-1))+0.5)/2**13.0
    Sar_3_I = 2.0*(Sar_3-(2**(13.0-1))+0.5)/2**13.0
    
    # Sar_0_I = 2.0*(Sar_0)/((2**13.0)-1) #PCB ERROR para que este centrado en zero
    # Sar_1_I = 2.0*(Sar_1)/((2**13.0)-1) #PCB ERROR
    # Sar_2_I = 2.0*(Sar_2)/((2**13.0)-1)
    # Sar_3_I = 2.0*(Sar_3)/((2**13.0)-1)
    
    # a[0]
    plt.figure(1002)
    
    plt.plot(Sar_0_I)
    plt.plot(Sar_1_I)
    plt.plot(Sar_2_I)
    plt.plot(Sar_3_I)
    
    
    #DEBUG RESISTENCIAS
    Vcol = 16e-3
    Vrefe = 0.8
    Ieq = Sar_0_I[:4]/(2*2.0*25e3)+((0.8991-Vrefe)/10000.62)
    Req = Vcol/Ieq    
    print(Req)
    
    Ieq = Sar_1_I[:4]/(2*2.0*25e3)+((0.8991-Vrefe)/10000.62)
    Req = Vcol/Ieq    
    print(Req)    
    
    Ieq = Sar_2_I[:4]/(2*2.0*25e3)+((0.8991-Vrefe)/10000.472)
    Req = Vcol/Ieq    
    print(Req) 
    
    Ieq = Sar_3_I[:4]/(2*2.0*25e3)+((0.8991-Vrefe)/10000.62)
    Req = Vcol/Ieq    
    print(Req) 
    
    
    
    DIC_Cw ={'DAC E': 0.7}
    AS2.Dict_To_InstructionSimple(DIC_Cw)

    nCols = 4
    nChannels = 16

    I_Vec, Gain = AS2.ParamCalc(DIC_R,
                                DIC_C,
                                nCols=nCols,
                                nChannels=nChannels)
    
    Buffer = AS2.ByteArrayToReshape(Buffer_Fetch=AS2.OutData,
                                    Gain_Vec=Gain,
                                    nCols=nCols,
                                    nChannels=nChannels)

    I_Vec = Buffer + I_Vec
    R = 13e-3/I_Vec[:1,:16]

    # print('Buffer',self.OutData[:1,:16])



    

    a[0]
    
    Vmin = 0.0
    Vmax = 0.2
    Steps = 10
    nChannels = 16
    nCols = 4
    # a[0]

    VREF_E_G = AS2.GlobalVREFE(Vmin,Vmax,Steps,nChannels,nCols,DIC_C)
    
    AS2.StopRun()
    DIC_Cw ={'DAC E': VREF_E_G}
    AS2.Dict_To_InstructionSimple(DIC_Cw)

    
    a[0]

    #Multiples Runs
    #Variables
    #2560000bytes * 8 * 13 / 16 bytes por trama = 16640000 tramas * 421.875kHz = 39.44 s
    AS2.Runs_Completos = 8
    AS2.LimiteRuns = 4*13 #13 (6.5 con 8)  aproximadamente lo que se hacia antes para 40 segundos
    
    Inicio = time.time()
    
    AS2.RunLocal()
    # Buffer_Fetch  = AS2.OutData
    print("Tiempo Captura ",time.time()-Inicio, " s")
    # print("Bitstream Init...")
    # Buffer_bitstream =ConstBitStream(AS2.OutData)
    # Buffer_Str = Buffer_bitstream.bin 
    a[0]

    # print("Bistream_Completo..." ,time.time()-Inicio, " s")
    print("Parsing...")
    
    # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.Bitstream_to_Sep(Buffer_Str=Buffer_Str)
    # Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.Sep_From_ByteArray(AS2.OutData)
    Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.ByteArrayToReshapeSar(AS2.OutData)
    
    Buffer = AS2.ByteArrayToReshape(Buffer_Fetch=AS2.OutData,Gain_Vec=[1,1,1,1],nCols=4,nChannels=16)
    
    print("Parsing Completo...",time.time()-Inicio, " s")
    
    a[0]

    # AS2.ASIC_Off()
    
    #Gravar en fichero
    print("Saving Files...")
    
    
    print ("Len Sar 0", len(Sar_0))
    print ("Len Sar 1", len(Sar_1))
    print ("Len Sar 2", len(Sar_2))
    print ("Len Sar 3", len(Sar_3))

    Contador = 303
    
    Error,Col,Sar_0,Sar_1,Sar_2,Sar_3 = AS2.ReadAcqL()
    
    Contador = Contador + 1
    letra = 'ByteArray_'+str(Contador)
    
    path_f = "/home/jcisneros/Downloads/DAta_rouleta/"
    
    file_name = path_f + letra + ".txt"


    AS2.Save_File_ByteArray(path = file_name, Data = AS2.OutData)

    # DIC_Cw ={'DAC E': 0.95}
    # AS2.Dict_To_InstructionSimple(DIC_Cw)
    
    
    
    # # AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_0,Limite= len(Sar_0),Conversion=1)
    
    # file_name = "SAR_1_AS2t" + letra + ".txt"
    
    # # AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_1,Limite= len(Sar_1),Conversion=1)
    
    # file_name = "SAR_2_AS2t" + letra + ".txt"
    
    # # AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_2,Limite= len(Sar_2),Conversion=1)
    
    # file_name = "SAR_3_AS2t" + letra + ".txt"
    
    # # AS2.Gravar_M_Conversion(path=path_f,filename=file_name,Data=Sar_3,Limite= len(Sar_3),Conversion=1)
    
    # print("Saving Files...")
    
    # # AS2.Save_File_ByteArray(path=path_f+"/"+file_name,Data=Buffer_Fetch)

