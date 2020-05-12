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


from datetime import datetime

#CONSTANTS ERRORS

reading_error = 0
EP_None = 0        # �ӣ ��
EP_Line = 1        # ������ �� ����� �����
EP_TimeOut = 2     # ��� ������ (�������)
EP_Raving = 3      # ������������� �����
EP_Violation = 4   # ��������� ���������
EP_Stuff = 5       # ������������ ������
EP_CRC = 6         # ������ CRC
EP_TooMany = 7     # ������� ����� ������ 

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
reading_status = 0   #  ��������� �������� ��ɣ�� (default = 0 = IP_Void)
IP_Void = 0   #  ��É£� ��������
IP_Wait = 1   #  öÄ£Í  ��Á
IP_Echo = 2   #  ��É£� ���
IP_Paus = 3   #  öÄ£Í  ������
IP_Resp = 4   #  ��É£� ������
IP_Stuf = 5   #  öÄ£Í  ������              

reading_status_log = { \
    IP_Void : 'IP_Void',
    IP_Wait : 'IP_Wait',
    IP_Echo : 'IP_Echo',
    IP_Paus : 'IP_Paus',
    IP_Resp : 'IP_Resp',
    IP_Stuf : 'IP_Stuf' }


# Bites for request
SB_HdQ = 0x80;St_HdQ = 0x7F  # �����-���� �������
SB_HdR = 0x40;St_HdR = 0xBF  # �����-���� ������
SB_End = 0x0D;St_End = 0xF2  # ����-����
SB_Stf = 0x1B;St_Stf = 0xE4  # ���� �������� ������
SB_Ack = 0x06;St_Ack = 0xF9  # ������������


#class
class BiteSequences(list):
    """îÅÍÎÏÖËÏ ÍÏÄÅÒÎÅÚÉÒÏ×ÁÎÎÙÊ ÓÐÉÓÏË"""
    def __init__(self,array=None):
	if array:
	    if isinstance(array,list):		
		#self += array
		self.from_array(array)
	    elif isinstance(array,str):		
		self.from_str(array)
    def as_array(self):
	"""×Ù×ÅÓÔÉ ÍÁÓÓÉ× ÂÁÊÔ ËÁË ÓÐÉÓÏË"""
	return self
    def as_str(self):
	"""×Ù×ÅÓÔÉ ÍÁÓÓÉ× ÂÁÊÔ ËÁË ÓÔÒÏËÕ"""
	return "".join([chr(x) for x in self])
    def from_str(self,string=""):
	"""ÐÏÌÕÞÅÎÎÕÀ ÐÏÓÌÅÄÏ×ÁÔÅÌØÎÏÓÔØ ÂÁÊÔ ÐÅÒÅ×ÅÓÔÉ × ÓÐÉÓÏË"""
	
	"""if string.__len__()<15:
	    string += "\x00"*(15 - string.__len__())"""
	self.clear_array()
	self += list([ord(x) for x in string])
    def from_array(self,array=[]):
	"""if array.__len__()<15:
	    array += [0]*(15 - array.__len__())"""
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
Rqs 	 	  = BiteSequences() # úÁÐÒÏÓ ÞÅÇÏ-ÌÉÂÏ
Cmd 	 	  = BiteSequences() # ëÏÍÍÁÎÄÁ ÏÔ ÚÁÐÒÏÓÁ
request  	  = BiteSequences() # ÐÏÌÎÏÓÔØÀ ÓÆÏÒÍÉÒÏ×ÁÎÎÙÊ ÚÁÐÒÏÓ = ÓÐÅÃ.ÂÉÔÙ + Cmd
request_data_len  = 0 		    # ÄÌÉÎÁ ÚÁÐÒÏÓ × ÂÁÊÔÁÈ
response 	  = BiteSequences() # ÏÎ ÖÅ MC601Response
response_data_len = 0 		    # ÄÌÉÎÁ ÏÔ×ÅÔÁ × ÂÁÊÔÁÈ
register = 0
data = []		    	    # ÕÖÅ ÏÂÒÁÂÏÔÁÎÎÙÊ ÄÁÎÎÙÅ, ÇÏÔÏ×ÙÅ ÄÌÑ ÚÁÐÉÓÉ
table = {}			    # ÄÁÎÎÙÅ × ÓÌÏ×ÁÒÅ Ó ÒÅÇÉÓÒÏÍ × ËÁÞÅÔ×Å ËÌÀÞÁ

#---------- timing -------------	# ÔÁÊÍÅÒ ÐÒÉ£ÍÁ
end_time = datetime.now()
wait = False
#--------- Status -------------- 	# ÓÔÁÔÕÓ ÐÒÉ£ÍÁ
active = False
connection_error = [ "ðÏÒÔ ÏÔËÒÙÔ", "îÅ×ÅÒÎÙÊ ÎÏÍÅÒ ÐÏÒÔÁ","ïÛÉÂËÁ ÍÏÄÕÌÑ MSComm32",
		     "ðÏÒÔ ÏÔËÒÙÔØ ÎÅ ÕÄÁÌÏÓØ","îÅ ÕÄÁÌÏÓØ ÏÂÎÁÒÕÖÉÔØ óÞ£ÔÞÉË"] 

#---------headmeter-------		# ÄÁÎÎÙÅ ÔÅÐÌÏÓÞ£ÔÞÉËÁ
date_time = datetime.now()
heatmeter_number = 0

