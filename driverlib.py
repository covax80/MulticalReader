#!/usr/bin/env python
#-*- coding: koi8-r -*-

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


import sys

from utils import dbmsg,lst2hx
from MC601crc16 import CRC_CCITT16,check_CRC
from struct import pack, unpack
from time import sleep
from serial import *
import constants
"""from constants import Cmd,		 reading_status, \
		      reading_error,	 response_data_len, \
		      response,		 request_data_len, \
		      request,		 end_time, \
		      wait,		 active

from constants import * # other"""
from biteoperations import * 

from driverlib import proccess_bite

# COMMANDS


def MC601Cmd2Rqs(Cmd, n, request):    
    i = bite_counter = b = 0
    if n <= 0: 
	return
    dbmsg(3, "Cmd without CRC %s"%lst2hx(Cmd))
    i = CRC_CCITT16(Cmd, n, 0)
    Cmd = Cmd + list(unpack('BB',pack('>h',i)))
    dbmsg(3,"Cmd with CRC    %s"%lst2hx(Cmd))
    request.append(constants.SB_HdQ)         # ��������� ��������� ����
    bite_counter= 1
    b = 0
    for i in range(n + 2):
        b = Cmd[i]
	b,stuffing_done = Stuffing(b)
        if stuffing_done:
    	    print "stuf enable"
            request.append(constants.SB_Stf)
            bite_counter += 1
        request.append(b)
        bite_counter += 1
    request.append(constants.SB_End)         # ��������� �������� ����
    bite_counter += 1
    #print "request =  %s"%lst2hx(request)    
    return bite_counter, request

def clear_constats_before_reading():
    constants.reading_error = 0
    constants.response_data_len = 0    
    constants.response.clear_array()   
    constants.request_data_len = 0    
    constants.request.clear_array()        
    constants.reading_status = constants.IP_Wait # = 1     - waiting the echo


def start_timer(sec):
    """ ÆÉËÓÉÒÕÅÍ ÓÏÓÔÏÑÎÉÅ ÏÖÉÄÁÎÉÑ """
    constants.end_time = datetime.now() + timedelta(seconds = sec)    
    constants.wait = True
    return
    
def data_recived():
    """ÐÏÌÕÞÅÎÉÅ ÄÁÎÎÙÈ ÐÏ-ÂÉÔÎÏ"""
    constants.response += constants.port.read(1)
    return (constants.reading_status == constants.IP_Void)   
    

def interrupt_reading(err_code):
    """ ÒÁÚÒÙ× Ó×ÑÚÉ  """
    if constants.reading_status != constants.IP_Void:
	constants.reading_error = err_code
	constants.reading_status = constants.IP_Void
    return    

def timer_check():    
    if not constants.wait:
	return # wait = False
    # åÓÌÉ ×ÒÅÍÑ ÔÁÊÍÁÕÔÁ ÚÁËÏÎÞÅÎÏ, ÔÏ ÒÁÚÒÙ×ÁÅÍ Ó×ÑÚØ É ÓÔÁ×ÉÍ ÏÛÉÂËÕ EP_TimeOut
    if datetime.now() > constants.end_time:
	interrupt_reading(constants.EP_TimeOut) 
	constants.wait = False
    return # return wait = False

def check_function():
    #print  constants.request[1:3] ,"  >> ", constants.response[0:2] 
    try:
	return constants.request[1:3] == constants.response[0:2] 
    except IndexError:
	return False

def stop_timer():
    constants.wait = False
    return

def init_port():
    #constants.moxaport = '/dev/ttyr03'
    if isinstance(constants.moxaport,int):
        constants.port = Serial()
        constants.port.port = constants.moxaport      
    else:
        constants.port = Serial(port = constants.moxaport)
    constants.port.baudrate = 1200
    constants.port.parity=PARITY_NONE     #enable parity checking
    constants.port.stopbits=1  	#number of stopbits
    constants.port.timeout=3  	#set a timeout value, None for waiting forever
    constants.port.xonxoff=0              #enable software flow control
    constants.port.rtscts=0
    constants.port.bytesize=EIGHTBITS
    constants.port.open()
    constants.active = True




def SendCommand(command, n):
    #print "sendcommand"        
    if not constants.port:
	init_port()
    clear_constats_before_reading() # ïÂÎÕÌÑÅÍ ÏÛÉÂËÉ ÞÔÅÎÉÑ, ÄÌÉÎÕ-ÏÔ×ÅÔÁ, ÓÔÁÔÕÓ-ÞÔÅÎÉÑ - IP_WAIT
    
    constants.reading_status = constants.IP_Wait    
    
    constants.request_data_len, constants.request = MC601Cmd2Rqs(command, n, constants.request) # ÐÏÌÕÞÅÍ ËÏÌ-×Ï ÏÔÓÙÌÁÅÍÙÈ ÂÁÊÔ + ÐÏÄÇ.ÚÁÐÒÏÓ
    dbmsg(7,"Rqs: %s" % (lst2hx(constants.request)))
    #print "request after MC601Cmd2Rqs = %s type(request) = %s" % (lst2hx(request),repr(type(request)))
    #request = request[:-1]
    Rqs = constants.request    
    #open('tmp.tzt','a').write('locals = %s'%repr(locals()))
    open('tmp.tzt','a').write('Cmd: ' + lst2hx(Rqs) + "\n")    
    
    constants.port.write(Rqs.as_str()) 	# ÏÔÓÙÌÁÅÍ ×Ó£ × ÐÏÒÔ
    
    #raw_response = False
    raw_response = ""
    raw_response_cnt = 6    
    
    while not raw_response and raw_response_cnt:
	if raw_response_cnt < 6:
	    print "attemp(to get data) no.",raw_response_cnt
	    sleep(1)
	    constants.port.write(Rqs.as_str()) 	# ÏÔÓÙÌÁÅÍ ×Ó£ × ÐÏÒÔ
	read_bite = "1"
	"""while read_bite:
	    read_bite = constants.port.read(1)
	    if read_bite:
		#proccess_bite(read_bite)
		raw_response += read_bite"""
	raw_response = constants.port.read(1024)
	raw_response_cnt -= 1 		
    #print "LEN = " + str(len(raw_response))
    open('tmp.tzt','a').write('Rsp: ' + lst2hx(raw_response) + "\n")    
    dbmsg(7,'Rsp: %s \n\n' % lst2hx(raw_response))
    if not raw_response:
	#return constants.port.EP_Line
	dbmsg(6,"heatmeter don't response!")
	return False
	
    constants.reading_status = constants.IP_Void
    proccess_array(raw_response)
    #start_timer(3)	# ÎÁ 3 ÓÅËÕÎÄÙ ×ËÌÀÞÁÅÍ ÆÌÁÇ "wait"
    #while not data_recived(): # ÐÒÏ×ÅÒÑÅÔ reading_status
    #	timer_check() 	      # ÐÒÏ×ÅÒÑÅÍ ÎÅ ×ÙÛÅÌ ÌÉ ÔÁÊÍÁÕÔ × 3 ÓÅËÕÎÄÙ
    
    #stop_timer()	      # ÏÓÔÁÎÁ×ÌÉ×ÁÅÍ ÔÁÊÍÅÒ Ô.Ë. ÕÖÅ ×Ó£ ÐÒÏÞÉÔÁÎÏ
    """if not check_function():
	dbmsg(7,"Request function != response Function = Error")
	constants.reading_error = constants.EP_Violation
	sys.exit(1)	"""
    check_CRC()
    try:
        constants.port.close()
        constants.port = None
        constants.active = False
    except:
        pass
    return constants.reading_error


