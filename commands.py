#!/usr/bin/env python
#-*- coding: utf8 -*-

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


#---sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys--------sys-----
from sys import argv
from serial import * # Serial
from datetime import datetime, timedelta, date as ddate,time as dtime
from struct import pack, unpack
#from dateutil.relativedelta import relativedelta
#---my---------my---------my---------my---------my---------my---------my---------my---------my---------my---------my---------my---------my---------my---------my---------my------
from biteoperations import doublebites_to_hi_bite, ChLLng, I2Bytes,Bytes2L, Byte2Mantiss, Byte2Factor
from multicaldate import mult2python_date, mult2python_time,Date2YYMMDD, months_left
from MC601crc16 import CRC_CCITT16, check_CRC
"""from constants import Cmd,data,response,request,request_data_len,response_data_len,active
from constants import * """
import constants
from driverlib import SendCommand
from utils import dbmsg, lst2hx
#--------------------------------------------------------------------------------------------------------------------------------


def read_current(register):
    constants.active = True
    """if not constants.active:
	dbmsg(7,"Not Active")
	return 0"""
    #Cmd.from_array([0x3f,0x10,0x1,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0])   
    constants.Cmd.from_array([0x3f,0x10,0x1,0x0,0x0])   
    constants.Cmd = I2Bytes(register,constants.Cmd,3)
    if SendCommand(constants.Cmd , 5) != 0:	
	dbmsg(6,"ERROR of SendCommand")
	return # error
    
    if constants.response_data_len <= 7:
	dbmsg(6,"return empty response")
	print "empty current response"
	return 0 # empty response    
    #print "CuRR_response_data_len = %d " % constants.response_data_len
    return Byte2Mantiss(constants.response,constants.response[5],7) * Byte2Factor(constants.response[6])


def read_datetime():    
    date = read_current(1003)
    #print "date = %d" % date 
    if date == 0:
        date = ddate.today() 
    else:
	date = mult2python_date(date)
    time = read_current(1002)
    #print "time = %d" % time
    if time == 0:
        time = datetime.now().time()
    else:	
	time = mult2python_time(int(time))
    
    return date,time


def read_heatmeter_number():
    constants.Cmd.from_array([0x3f,0x2])
    if SendCommand(constants.Cmd,2) != 0:
	dbmsg(6,"ERROR of SendCommand in read_heatmeter_number function") 
	return # error    
    res = Bytes2L(constants.response,4,2)
    print "Heatmeter number = %d" % res
    return res


def empty_hour_arch(registr,datetime):    
    return { 1003 : [datetime - timedelta(days = 1)]*24, 1002 :range(1,25) }.get(registr,[0]*24)
    #return { 1003 : [datetime]*24, 1002 :range(1,25) }.get(registr,[0]*24)

def read_hour_arch(registr, date):    
    records_amount = mantis_size = iPos = factor = b = 0       
    dbmsg(6,"REGISTR (%d)"%registr)    
    if registr in ( 1002 , 1003):
	return empty_hour_arch( registr, date ) 
    res = [0] * 24
    #date = date + timedelta(hours = +1)
    constants.Cmd.from_array([0x7f,0x63]) 					
    constants.Cmd = I2Bytes(registr, constants.Cmd, 2)				
    constants.Cmd += [(date.year - 2000), (date.month), (date.day), 0x0 ]     	
    constants.reading_error = SendCommand(constants.Cmd, 8)			
    if constants.reading_error != 0:
	print "Detected some errors during reading process - try again"
        return False
    #dbmsg(6," >>> response (%s)"%lst2hx(response))
    mantis_size = constants.response[5]               	# Размер мантиссы
    factor = Byte2Factor(constants.response[6])  		# Фактор
    print "response_data_len = ",constants.response_data_len
    records_amount = (constants.response_data_len - 8) / mantis_size   # Количество отчётов полученное (24)
    #sys.exit(1)
    if records_amount <= 0:
        reading_error = 99
        print "Error reading hour arch NO records"
        return res
    iPos = 8				
    if records_amount > 24:
	   records_amount = 24
    tmp = 0
    print "here! KKK = %d"%records_amount
    for j in range(0,records_amount):
	#print "---<> resp = %s, mantis=%d, ipos=%d	"%(lst2hx(constants.response), mantis_size, iPos)
        tmp = Byte2Mantiss(constants.response, mantis_size, iPos)		# 1234
	res[j] = tmp * factor					# 1234 * 0.01 = 12.34
        iPos = iPos + mantis_size				
        #dbmsg(6,"res[%d] = %2f "%(j,res[j]))        
        #print "+++	" , repr(res)
    res.reverse()
    return res
    

def empty_day_arch(registr, date, from_date, days_amount ):
    constants.response_data_len = days_amount 
    constants.data = [0] * days_amount 
    return constants.data

def read_day_arch(registr, from_date, days_amount, day ):
    print "from_date = ",from_date,"| days_amount= ", days_amount
    constants.active = True
    if not constants.active:	
	return empty_day_arch(registr,from_date, days_amount, day)
    records_amount = mantis_size = iPos = factor = 0            
    data = [0] * days_amount
    #print "here"
    constants.Cmd.from_array([0x3f,0x66]) 				
    constants.Cmd = I2Bytes(registr, constants.Cmd, 2)			
    f_date = from_date
    day = 0       
    while day < days_amount:
	constants.Cmd = I2Bytes(f_date, constants.Cmd, 4)
	constants.reading_error = SendCommand(constants.Cmd, 6)
	if constants.reading_error != 0:
		dbmsg(5,"some errors")
    		return data
    	try:
    	    mantis_size = constants.response[5]               			# Размер мантиссы    	    
    	except IndexError:
    	    print "response[5]=" , constants.response             			# Размер мантиссы    	    
    	    break
    	print 'mantis_size = ', mantis_size
    	if mantis_size == 0:
    	    break
	factor = Byte2Factor(constants.response[6]) 		 		# Фактор
        records_amount = (constants.response_data_len - 7) / mantis_size   	# Количество отц·чётов полученное
        if records_amount == 0:
    	    return data    	
    	iPos = 7
        #for j in range(records_amount):
        #for j in range(days_amount):
        print "records_amount = ",records_amount
        for j in range(records_amount):
    	    if day == days_amount:
    		break 
    	    #print "DAY = ",day,"records_amount =",records_amount
    	    try:	    
                data[day] = Byte2Mantiss(constants.response, mantis_size, iPos) * factor
            except:
        	print "ERROR day = %d | response = %s | mant = %d | pos = %d"%(day,lst2hx(constants.response),mantis_size, iPos)
        	sys.exit(2)
            iPos = iPos + mantis_size
            day += 1
        f_date += records_amount
    return data


def read_month_arch(registr, from_date, months_amount, month ):
    constants.active = True
    print "REGISTR = ",registr
    data = [0] *  months_amount
    factor = f_date = records_amount = mantis_size = 0    
    #if not constants.active:
	#return empty_day_arch(registr,from_date, months_amount, month)    
    #if not registr == 1003:	
    #	data = empty_day_arch(registr,from_date, months_amount, month)    
    #	print repr(data)
    constants.Cmd.from_array([0x3f,0x65]) 				
    constants.Cmd = I2Bytes(registr, constants.Cmd, 2)			
    f_date = from_date
    month = 0
    while month < months_amount:
	constants.Cmd = I2Bytes(f_date, constants.Cmd, 4)		
	constants.reading_error = SendCommand(constants.Cmd, 6)
	if constants.reading_error != 0:
		dbmsg(5,"some errors")
    		return [0] * months_amount
    	try:
    	    mantis_size = constants.response[5]               			# Размер мантиссы
	    factor = Byte2Factor(constants.response[6]) 			 	# Фактор
	except IndexError:
	    return [0] * months_amount	    
        records_amount = (constants.response_data_len - 7) / mantis_size   	# Количество отц·чётов полученное
        if records_amount == 0:
    	    return [0] * months_amount
        iPos = 7
        if records_amount > months_amount:
    	    records_amount = months_amount
        for j in range(records_amount):
    	    print j    	    
            data[month] = Byte2Mantiss(constants.response, mantis_size, iPos) * factor
            #print "data[month] =",repr(data[month])
            month += 1
    	    iPos += mantis_size
        f_date += records_amount    
    data.reverse()
    return data

def process_hour(date_from,raw_data):
    pass
	
def process_day(date_from,raw_data):
    pass
	

# 192.168.3.100

