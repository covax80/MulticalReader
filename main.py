#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


# system import --------------------------------------------------------------------------------------------------------------------------------------------------
import sys
from sys import argv
from serial import Serial
from multicaldate import Date2YYMMDD, mult2python_date, mult2python_time, months_left, days_left, hours_left
from datetime import datetime,timedelta,date as ddate 
#from dateutil.relativedelta import relativedelta
from struct import pack, unpack
from time import sleep
#import re

# private import -----------------------------------------------------------------------------------------------------------------------------------------------------------
import constants
from driverlib import clear_constats_before_reading
from utils import dbmsg, lst2hx
from commands import read_heatmeter_number,read_datetime, read_hour_arch, read_day_arch, read_month_arch, read_current
import wx
# ------------------------------------------------------------------------------------------------------------------------------------------------


udbmsg = dbmsg

#+++++++++++++++++++++++++ OPERATIONS ++++++++++++++++++++++++

def read_datetime():
    date,time = read_datetime()   
    constants.date_time = datetime(date.year,date.month,date.day,time.hour,time.minute,time.second)
    info = 'Heatcounter time = %s ' % constants.date_time.strftime('%d.%m.%Y %H:%M') 
    return info
    
def read_number():
    constants.heatmeter_number = read_heatmeter_number()
    info = 'Heatcounter counter = %d ' % constants.heatmeter_number 
    return info


	
    #print "\n\n\n".join(repr(row) for row in constants.table.values()) + "\n" + "*"*80 + "\n"

def month_archive(reg_list, fromdate, todate):
    
    from_date = todate 
    to_date   = fromdate
    
    month_now = datetime(*ddate.today().timetuple()[:3])
    f_date = months_left( month_now, from_date ) 
    archive_records = months_left(from_date, to_date) + 1
    print "f_date %d,	 records = %d"%(f_date, archive_records)
    for reg in reg_list:
	constants.table[reg] = [reg]	
	constants.data = read_month_arch(reg, f_date,archive_records, 0)
	print repr(constants.data)
	if not constants.data:
	    dbmsg(7,">>  -------- NO MONTH DATA --------- \n ")
	    sys.exit(1)
	if reg == 1003:
	    dt = 0
	    tmp_list = []
	    for mean in constants.data:
		dt = mult2python_date(mean)
		if not dt:
		    tmp_list.append(mean)
		else:
		    tmp_list.append(dt.strftime('%d.%m.%Y'))
	    constants.table[reg] += tmp_list
	    #constants.table[reg] += [ mult2python_date(dt).strftime('%d.%m.%Y') for dt in constants.data]
	else:
	    constants.table[reg] += ["%.2f"% x for x in constants.data]
	constants.data = []
    return constants.table
    
def day_archive(reg_list, fromdate, todate):

    from_date = todate 				# 12 november
    to_date = fromdate 				# 01 august
    
    #from_date +=  relativedelta(days=1)
    #to_date   +=  relativedelta(days=2)
    now_day = datetime(*ddate.today().timetuple()[:3]) 
    start_date = days_left(now_day,from_date)
    #print "now_day = %s,	from_date = %s"%(repr(now_day),repr(from_date))
    #print "from_day = %s,	to_date = %s"%(repr(from_date),repr(to_date))
    archive_records = days_left(from_date,to_date) + 1 
    #print "startdate %d, records =%d"%(start_date, archive_records)
    len_reglist = len_reglist2 = len(reg_list)
    for reg in reg_list:               
        len_reglist2 -= 1
	constants.table[reg] = []
	constants.data  = read_day_arch(reg, start_date, archive_records, 0)
	if not constants.data:
	    dbmsg(7,">>  -------- NO DAY DATA --------- \n ")
	    sys.exit(1)
	if reg == 1003:	    
	    try:
		constants.table[reg] += [ mult2python_date(dt).strftime('%d.%m.%Y') for dt in constants.data]
	    except:
		constants.table[reg] += ["%d"% x for x in constants.data]
	    #[ mult2python_date(dt).strftime('%d.%m.%Y') for dt in constants.data]
	else:
	    constants.table[reg] += ["%.2f"% x for x in constants.data]
	constants.data = []
	constants.table[reg] += [reg]
	constants.table[reg].reverse()
    return constants.table


def hour_archive(reg_list,from_date,to_date):
    from_date += timedelta(days=+1)
    to_date   += timedelta(days=+2)
    #day += timedelta(days=+1)
    day = from_date
    for reg in reg_list:
	constants.table[reg] = [reg]
	for day_inc in range(days_left(to_date,from_date)):
	    day = from_date + timedelta(days = day_inc)
	    print "day = %s"%(day)
	    constants.data = read_hour_arch(reg ,day )  		# hour
	    print 'LEN=',len(constants.data)," ",repr(constants.data),"\n"
	    if not constants.data:
		dbmsg(7,">>  -------- NO HOUR DATA --------- \n ")
		sys.exit(1)
	    if reg == 1002:
		constants.table[reg] += [str(int(dt)) for dt in list(constants.data)]
	    elif reg == 1003:
		constants.table[reg] += [ dt.strftime('%d.%m.%Y') for dt in constants.data]
	    else:
		constants.table[reg] += ["%.2f"% x for x in constants.data]
	    constants.data = []	    
    return 


def current_data(reg_list):
    tmp=None    
    for reg in reg_list:
        constants.table[reg] = [reg]
        constants.data = read_current(reg)
        if not constants.data:
            udbmsg(7,">>  -------- NO HOUR DATA --------- \n ")
            return False
        if reg == 1003:
            if constants.data == 0:
                constants.table[reg].append(datetime(*ddate.today().timetuple()[:3]).strftime('%d.%m.%Y'))
            else:
                #print mult2python_date(constants.data).timetuple()[:3]
                constants.table[reg].append(datetime(*mult2python_date(constants.data).timetuple()[:3]).strftime('%d.%m.%Y'))
        elif reg == 1002:
            if constants.data == 0:
                constants.table[reg].append("00:00")
            else:
                tmp = mult2python_time(int(constants.data))
                print tmp
                constants.table[reg].append("%d:%d"%(tmp.hour,tmp.minute))
        else:
            constants.table[reg] += ["%.2f"%constants.data]


def read_archive(reg_list, from_date, to_date, arch_type):
    #print locals()
    constants.table = {}
    arch_type = arch_type.lower()
    if arch_type == 'current':	
	current_data(reg_list)
    elif arch_type == 'hour':	
	hour_archive(reg_list, from_date, to_date)
    elif arch_type == 'day':
	day_archive(reg_list, from_date, to_date)
    elif arch_type == 'month':
	#from_date += relativedelta(day = 1)
	#to_date += relativedelta(day = 1,months = +1)	
	month_archive(reg_list, from_date, to_date)



if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2:
	print "\n\nUSAGE	: prog.py com_port archive fromdate todate reg1,reg2,reg3,reg4 output_file"
	print "\nExample	: prog.py /dev/ttyr03 day  1-10-2008 10-10-2008 73,78,78,92 report1.txt"
	print "\n\nArchive types	: hour, day, month"
	print "\n\nNotice:	: in hour archive \"todate\" always = today\n\n\n"
	sys.exit(1)	
    #try:
    #print "LEN",len(argv),"  ",repr(argv)
    
if 1:
     constants.moxaport = argv[1]
     
     arch_type  = argv[2]
    
     start_date = argv[3];start_date = [int(x) for x in start_date.split('-')]; \
		start_date.reverse();start_date = datetime(*start_date)
     end_date   = argv[4]
     print(end_date)
     end_date = [int(x) for x in end_date.split('-')]
     print(end_date)
     end_date.reverse()
     end_date = datetime(*end_date)
     reg_list   = argv[5];reg_list = [int(x) for x in reg_list.split(',')]
    
     output = argv[6]
          
     """except:
	dbmsg(7,"Arguments FAIL")
	sys.exit()"""
    #open('tmp.tzt','a').write('info = %s'%str(info))    """
    #open('tmp.tzt','a').write('-=( registr = %d )=-\n'%reg)	
    #registr_list = [1002,1003,99,72,73,86,87,61,62]
    #registr_list = [86,87]
    #registr_list = [1003,99,72,73,86,87,61,62] # hour, day
    #registr_list = [1003,99,60,61,62,68,69,97,110]
    #registr_list = [1003,99,72,73,86,87,61,62] # hour, day
    
    #constants.moxaport = '/dev/ttyr03'
    
     print "ARCHIVE_TYPE = %s  from %s to %s" %(arch_type,start_date.strftime('%d.%m.%Y %H:%M'),end_date.strftime('%d.%m.%Y %H:%M'))    
     read_archive(reg_list,start_date,end_date,arch_type) #,constants)
     if not constants.table:
          dbmsg(7,"NO DATA")
          sys.exit(1)
     print repr([constants.table[x] for x in reg_list ] )
     constants.table = map(None,*[constants.table[x] for x in reg_list ] )
     info = ""
     for row  in constants.table:
          info += "\t".join(str(value) for value in row) + "\n"
     print info
     f = open(output,'w')
     f.write('\t%s'%str(info))
    #f.flush()
     f.close()
    
# 192.168.3.100

