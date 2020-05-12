#!/usr/bin/env python


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


from datetime import datetime,date,time
from biteoperations import ChLInt,ShortResidue
from utils import dbmsg

def mult2python_date(mult_date,return_datetime = False):    
    """ alya YYMMDD2Date"""    
    if not mult_date:
	return False
    mult_date = int(mult_date)
    dt = date
    if return_datetime:
	dt = datetime
		
    year_month 	= mult_date / 100
    day		= mult_date % 100
    if day != 0:
	# ÐÏÌÎÙÅ ÄÁÔÙ
	return dt(2000 + year_month / 100, year_month % 100, day)
    elif (year_month % 100) != 0:
	#ÍÅÓÑÃÙ É ÇÏÄÙ
	return dt(2000 + year_month / 100,  year_month % 100, 1)	
    else:
	#ÔÏÌØËÏ ÇÏÄÙ
	return dt(2000 + year_month / 100,  1, 1)
	
    

def mult2python_time(mult_time):
    if not mult_time:
	return False	
    #mult_time = int(mult_time)
    hour_minutes = mult_time / 100
    return time(hour_minutes/100, hour_minutes % 100, mult_time % 100)
    

def Date2YYMMDD( arch_type, datetime_mean ):
    dt = datetime_mean
    if arch_type in ('hour','day'):
	return ((dt.year - 2000) *100 + dt.month) * 100 + dt.day
    elif arch_type == 'month':
	return ((dt.year - 2000) *100 + dt.month) * 100
    elif arch_type == 'year':
	return (dt.year - 2000) * 10000
    else:
	return False



def years_left(first_date,second_date):
    if (first_date < second_date):
	dbmsg(6," months_left fail -< first_date < second_date")
	return False
    return (first_date.year - second_date.year)

def months_left(first_date,second_date):
    print locals()
    if (first_date < second_date):
	dbmsg(6," months_left fail -> first_date < second_date")
	return False
    return ((first_date.year * 12) + first_date.month) - ((second_date.year * 12) + second_date.month)

def days_left(first_date,second_date):
    #print "days_left ",locals()
    if (first_date < second_date):
	dbmsg(6," days_left fail -> first_date(%s) < second_date(%s)"%(str(first_date),str(second_date)))
	#return False
	return 0
    return (first_date - second_date).days

def hours_left(first_date,second_date):
    if (first_date < second_date):
	dbmsg(6," hours_left fail -> first_date < second_date")
	return False
    return (first_date - second_date).days * 24


def DateDiff(first_date,second_date):
    if first_date % 10000 == 0:
	return years_left(mult2python_date(first_date),mult2python_date(second_date))
    elif first_date %100 == 0:
	return months_left(mult2python_date(first_date),mult2python_date(second_date))        
    return days_left(mult2python_date(first_date),mult2python_date(second_date))
    

if __name__ == '__main__':
    pass


    