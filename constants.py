#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Copyright (c) 2009, Artyom Breus <artyom.breus@gmail.com>
All rights reserved.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE."""


from datetime import datetime

#CONSTANTS ERRORS

reading_error = 0
EP_None = 0        # Всё ОК
EP_Line = 1        # Ошибки на линии связи
EP_TimeOut = 2     # Нет ответа (таймаут)
EP_Raving = 3      # Незапрошенный обмен
EP_Violation = 4   # Нарушение протокола
EP_Stuff = 5       # Неправильная замена
EP_CRC = 6         # Ошибка CRC
EP_TooMany = 7     # Слишком много данных 

reading_error_log = { \
    EP_None 	:'EP_None',
    EP_Line 	:'EP_Line ',	
    EP_TimeOut	:'EP_TimeOut',
    EP_Raving 	:'EP_Raving ',
    EP_Violation:'EP_Violation',
    EP_Stuff 	:'EP_Stuff ',	
    EP_CRC 	:'EP_CRC ',	 
    EP_TooMany  :'EP_TooMany '}

#CONSTANTS STATUS
reading_status = 0   #  Состояние автомата приёма (default = 0 = IP_Void)
IP_Void = 0   #  Приём выключен
IP_Wait = 1   #  Приём эха
IP_Echo = 2   #  Приём эха
IP_Paus = 3   #  Приём ответа
IP_Resp = 4   #  Приём ответа
IP_Stuf = 5   #  Приём замены

reading_status_log = { \
    IP_Void : 'IP_Void',
    IP_Wait : 'IP_Wait',
    IP_Echo : 'IP_Echo',
    IP_Paus : 'IP_Paus',
    IP_Resp : 'IP_Resp',
    IP_Stuf : 'IP_Stuf' }


# Bites for request
SB_HdQ = 0x80;St_HdQ = 0x7F  # Старт-байт запроса
SB_HdR = 0x40;St_HdR = 0xBF  # Старт-байт ответа
SB_End = 0x0D;St_End = 0xF2  # Стоп-байт
SB_Stf = 0x1B;St_Stf = 0xE4  # Байт префикса замены
SB_Ack = 0x06;St_Ack = 0xF9  # Подтверждени


#class
class BiteSequences(list):

    def __init__(self,array=None):
	if array:
	    if isinstance(array,list):		
		#self += array
		self.from_array(array)
	    elif isinstance(array,str):		
		self.from_str(array)

    def as_array(self):
	return self

    def as_str(self):
	return "".join([chr(x) for x in self])

    def from_str(self,string=""):
	self.clear_array()
	self += list([ord(x) for x in string])

    def from_array(self,array=[]):
	self.clear_array()
	self += array

    def clear_array(self):
	self = self.__delslice__(0,self.__len__())

    def __getslice__(self,i,j):
        return BiteSequences(list(self)[i:j])

    def __add__(self,y):
        return BiteSequences(list(self) + y)    



#GLOBAL VARIABLES
port = None      
MaxRsp   	  = 1023
Rqs 	 	  = BiteSequences() 
Cmd 	 	  = BiteSequences() 
request  	  = BiteSequences() 
request_data_len  = 0 		    
response 	  = BiteSequences() 
response_data_len = 0 		    
register = 0
data = []		    	    
table = {}			    

#---------- timing -------------
end_time = datetime.now()
wait = False
#--------- Status -------------- 
active = False
connection_error = [ "Error 1", "Error 2","MSComm32 Error","Error 4"] 

#---------headmeter-------	
date_time = datetime.now()
heatmeter_number = 0