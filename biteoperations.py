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


from struct import pack,unpack
import constants
from utils import dbmsg

"""__all__ = [ \
    'I2B_Hi',   'doublebites_to_hi_bite',    'I2Bytes',    'Byte2Factor',    'Byte2Mantiss',
    'ShRByte',    'ShLByte',    'ChLInt',    'ShLInt',    'ShortResidue',    'L2I_Hi',
    'ChLLng',    'Bytes2L', 'Stuffing',      'Destuffing','proccess_array']
"""

def I2B_Hi(i):
    # xxyy --> xx
    #i = i & 0xff00 
    #i = i / 256
    #return i & 0xff
    return i >> 8
    
    
def doublebites_to_hi_bite(dword_integer):
    return dword_integer >> 8


def I2Bytes(reg,bites,offset):
    #print repr(locals())
    #bites[offset]     = ChLInt(reg)
    #bites[offset + 1] = ChLInt(reg)
    #return bites
    if len(bites) <= offset:	
	bites += [0] * (2 + offset - len(bites))
    registr = unpack('BB',pack('H',reg))
    #print locals()
    bites[offset]   = registr[1]
    bites[offset+1] = registr[0]
    #print "eee - ",locals()
    return bites
    

def Byte2Factor(bite):
    D = 1
    cnt = bite & 0x3f    
    while cnt > 0:
	D *= 10
	cnt -= 1
    if (bite & 0x40) != 0:
	 D = 1.0/D
    if (bite & 0x80) != 0:
	 D = -D
    #print locals()
    return D



def Byte2Mantiss(array, mantise_size, offset):
    #print offset
    res = float(0)
    cnt = 0
    #print "LEN array = ",len(array)," offset = ",offset
    while cnt < mantise_size:
	res *= 256   			# << 8
	try:	
	    res += array[offset + cnt]
	except:
	    print "LEN array = ",len(array)," -- offset+cnt = ",offset + cnt
	cnt += 1
    return res

def ShRByte(b):
    return (b>>1)%256
    #return bool( b&1 != 0 )

def ShLByte(bite):    
    #first_byte_anable - flag about... if shift enable then will be 2 bites instead of 1 bite
    #shift - left shift
    shift = bite
    first_byte_enable  = (bite & 0x80) != 0   
    shift &= 0x7f
    shift *= 2
    #print "ShLByte(%s) = %s"%(repr(bite),repr(shift))
    return shift, first_byte_enable 


def ChLInt(integer):    
    # xxyy ---> xx00 ; return xx
    # XXYY -> YY00. short int shift left 
    # XX. return left bite, right bite will be inserted by zero
    # src = source mean manipulation 
    # dst = function result    
    hi_bite = integer >> 8
    # Present 8 byte?
    eight_enable = (integer & 0x80) != 0 
    # 8 byte clear
    integer = integer & 0x7f
    integer = integer << 8
    if eight_enable:
	integer = integer | 0x8000
    integer = unpack('hxx',pack('i',integer))[0]
    return integer, hi_bite

def ShLInt(integer):    
    tmp = integer
    #  shift int on 1 byte to left , return True if high_byte_shift_enable
    enable_14_bite = 0
    high_byte_shift_enable = (integer & 0x8000) != 0   # flag about that high bite was changed
    enable_14_bite = integer & 0x4000 	# remember 14 byte
    integer = integer & 0x3fff 		# clear 14,16 byte
    integer = integer * 2 
    if enable_14_bite != 0:
	integer = integer | 0x8000
    #print "ShLInt(%d) = %d,%s"%(tmp,integer,str(high_byte_shift_enable))
    return integer, high_byte_shift_enable


def ShortResidue(bite,mask_of_devisor):    
    # first_byte_of_delimogo = 0x63
    # mask_of_devisor = 0x1021
    endresult = 0
    for x in range(8):
	endresult_shift, endresult_shift_enable = ShLInt(endresult)	# << 1	
	endresult = endresult_shift
	bite_shift, bite_1b_enable = ShLByte(bite)			# << 1
	bite = bite_shift
	if bite_1b_enable != endresult_shift_enable:
	    endresult = endresult ^ mask_of_devisor
	    #print "endres_shift != bite_1b_enable"	    
	#print repr(locals()) + "\n"*3
    result = unpack('hxx',pack('i',endresult))[0]
    return result



def L2I_Hi(lng):
    return (lng >> 16) << 16    
    
def ChLLng(lng):
    """ XXYYYYYY -> YYYYYY00. function for 'double' shift to left 1 bite .
	 XX. Return left(high).right(low) fill by zero."""
    hibite = lng >> 24
    bite32enable = (lng & 0x800000) != 0
    lng = lng & 0x7fffff  # 1 byte clean
    lng = lng * 256
    if bite32enable:
	lng = lng | 0x80000000
    return lng, hibite


def Bytes2L(b, n, iPos):
    i = 0 
    l = 0
    while i < n:	
	l = ChLLng(l)[0]	
	l = l | b[i + iPos]	
	i += 1
	#print repr(locals())
	l = unpack('l',pack('L',l))[0]
    
    return l

    
    
def Stuffing(bite):
    """  ц╟ц▓ц▐ц≈ц┘ц▓ц▒ц┘ц■, ц■ц▓ц┘ц┌ц∙ц┘ц■ ц▄ц┴ ц┌ц│ц┼ц■ ц ц│ц█ц┘ц▌ц≥. ц╔ц⌠ц▄ц┴ ц└ц│, ц■ц▐ ц ц│ц█ц┘ц▌ц▒ц┘ц■ ц┘ц┤ц▐ ц┴ ц≈ц▐ц ц≈ц▓ц│ц²ц│ц┘ц■ True """    
    stuffing_done = False
    stuff_dict = {constants.SB_HdQ:constants.St_HdQ,
		  constants.SB_HdR:constants.St_HdR,
		  constants.SB_End:constants.St_End,
		  constants.SB_Stf:constants.St_Stf,
		  constants.SB_Ack:constants.St_Ack}
    if stuff_dict.has_key(bite):
        stuffing_done = True
        stuffing_bite = stuff_dict[bite] # ц╔ц⌠ц▄ц┴ ц┘ц⌠ц■ц≤ ц ц│ц█ц┘ц▌ц│ ц■ц▐ ц ц│ц█ц┘ц▌ц▒ц┘ц█
    else:
	stuffing_bite = bite 
    return stuffing_bite,stuffing_done

def Destuffing(bite):
    """  ц╟ц▓ц▐ц≈ц┘ц▓ц▒ц┘ц■, ц■ц▓ц┘ц┌ц∙ц┘ц■ ц▄ц┴ ц┌ц│ц┼ц■ ц ц│ц█ц┘ц▌ц≥. ц╔ц⌠ц▄ц┴ ц└ц│, ц■ц▐ ц ц│ц█ц┘ц▌ц▒ц┘ц■ ц┘ц┤ц▐ ц┴ ц≈ц▐ц ц≈ц▓ц│ц²ц│ц┘ц■ True """    
    destuffing_done = False
    destuff_dict = {constants.St_HdQ:constants.SB_HdQ,
		    constants.St_HdR:constants.SB_HdR,
		    constants.St_End:constants.SB_End,
		    constants.St_Stf:constants.SB_Stf,
		    constants.St_Ack:constants.SB_Ack}
    if destuff_dict.has_key(bite):
        destuffing_done = True
        destuffing_bite = destuff_dict[bite] # ц╔ц⌠ц▄ц┴ ц┘ц⌠ц■ц≤ ц ц│ц█ц┘ц▌ц│ ц■ц▐ ц ц│ц█ц┘ц▌ц▒ц┘ц█
    else:
	destuffing_bite = bite 		 
    return destuffing_bite,destuffing_done


def save_bite(bite):
    # Записывает очередной байт в приёмный буфер. Нужна для предыдущей процедуры    
    if (constants.response_data_len >= constants.MaxRsp):
        constants.reading_status = constants.IP_Void
        constants.reading_error = constants.EP_TooMany
    else:
        constants.response.append(bite)        
        constants.response_data_len += 1
    return

def proccess_bite(bite):
    # Автомат приёма. Отсекает эхо, убирает стартовый и стоповый байтвы и т.д.
    dbmsg(3,"reading_error = %s reading_status = %s"%( constants.reading_error_log[constants.reading_error],
	    constants.reading_status_log[constants.reading_status]))
    if (constants.reading_status == constants.IP_Void):
	    #print "1"
	    # Прц┴бём не ожидается. Любой вход -- ошибка
	    if constants.reading_error != 0:	
		constants.reading_error  = constants.EP_Raving
    elif (constants.reading_status == constants.IP_Wait):
    	    #print "2"
	    # Жц└бём эха или собственно ответа.
	    if (bite == constants.SB_HdQ):
		# Начало эха с опто-головки
        	constants.reading_status = constants.IP_Echo   # ц┘ц⌠ц▄ц┴ ц⌠ц■ц│ц▓ц■ц▐ц≈ц≥ц┼ ц┌ц┴ц■ 0x80 - ц■ц▐ ц√ц└бёц█ ц°ц┬ц│
    	    elif (bite == constants.SB_HdR):
		constants.reading_status = constants.IP_Resp   # ц┘ц⌠ц▄ц┴ 0x40 -  Начало ответа	    
		#print "detect 0x40 " 
            else:
		constants.reading_status = constants.IP_Void
        	constants.reading_error = constants.EP_Violation         
    elif (constants.reading_status == constants.IP_Echo):
    	    #print "3"
	    # Принимаем эхо. По стоп-байту прекращаем
	    if (bite == constants.SB_End):
        	constants.reading_status = constants.IP_Paus
	    else:		
        	# В принципе, можно сравнивать с запросом
        	# Но мы пока ничего не делаем
		pass
    elif (constants.reading_status == constants.IP_Paus):
    	    #print "4"
    	    # Ждём ответа. Допустим только стартовый байт
    	    if (bite == constants.SB_HdR):
        	constants.reading_status = constants.IP_Resp
            elif (bite == constants.SB_Ack):
	        constants.reading_status = constants.IP_Void
        	save_bite(bite)
	    else:            
		constants.reading_status = constants.IP_Void
		constants.reading_error = constants.EP_Violation
		save_bite(bite)
    elif (constants.reading_status == constants.IP_Resp):
    	    #print "5"
	    # Принимаем ответ
    	    if (bite == constants.SB_End):
        	constants.reading_status = constants.IP_Void	# if bite == 0x0d
            elif (bite == constants.SB_Stf):
        	constants.reading_status = constants.IP_Stuf
            else:
		save_bite(bite)
    elif (constants.reading_status == constants.IP_Stuf):
    	    #print "6"
	    # Жц└бём байт замены
	    bite,destuffing_done = Destuffing(bite)
    	    if destuffing_done:
        	constants.reading_status = constants.IP_Resp
            else:
        	constants.reading_status = constants.IP_Void
        	constants.reading_error= constants.EP_Stuff
    	    save_bite(bite)
      
def proccess_array(array):
    constants.reading_status = constants.IP_Wait
    dbmsg(3,"proccess_array reading_error = %d \n\n"% constants.reading_error  )
    cnt = 0
    for x in array:
	cnt += 1
	#save_bite(x)
	proccess_bite(ord(x))
	#print "cnt=",cnt
	if constants.reading_error != 0:
	    print "ERROR = " + constants.reading_error_log[constants.reading_error]
	    sys.exit(1)
    return


    
    

if __name__ == '__main__':
    """while 1:
	try:
	    c = raw_input("=> ")
    	    print ShortResidue(int(c),0x1021)
    	except:
    	    break"""
    #print Bytes2L([0x1,0x2,0x3,0x4],4,0)
    print Byte2Factor(0x42)
    
    
