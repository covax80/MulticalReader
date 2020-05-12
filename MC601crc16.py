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


from biteoperations import ChLInt,ShortResidue
import constants
from utils import dbmsg

def CRC_CCITT16(Bites, n, iPos):    
    """bites = [0x1,0x2,....]
       n - Ë ËÁËÏÍÕ ÂÁÊÔÕ ÐÒÉÓÌÀÎÑ×ÉÔØ crc
       iPos - ÎÁÞÁÌØÎÁÑ ÐÏÚÉÃÉÑ × ÍÁÓÓÉ×Å Bites"""	    
    mask 		= 0x1021
    hi_bite_of_array 	= 0x0
    residue 		= 0x0      
    if n > 0:	
	for x in range(n):
	    shift_1byte_left, hi_bite = ChLInt(residue)		# 0x1234 ---> 0x2468, 12
	    residue = shift_1byte_left
	    hi_bite_of_array = hi_bite ^ Bites[iPos + x]
	    short_residue = ShortResidue(hi_bite_of_array, mask)
	    residue  = residue ^ short_residue	    
	    #print repr(locals())+ "\n\n"
	    #print "\n".join([repr(y) + " = " + repr(loc[y]) for y in loc]) + "\n"*3
    return residue


def check_CRC():
    if constants.reading_error == 0:	
	crc_res = CRC_CCITT16(constants.response,constants.response_data_len,0)
	#print " response =%d  response_data_len =%d  CRC = %d" %(len(response), response_data_len,crc_res)
        if crc_res == 0:
            constants.response_data_len -= 2
            constants.response = constants.response[:-2]
        else:
    	    dbmsg(6,"CRC - FALSE")
            constants.reading_error = constants.EP_CRC

if __name__ == '__main__':    
    #bites = [63, 2, 0, 94, 187, 181, 222, 74, 0, 0, 101, 0, 225, 48, 0, 0]
    
    n = 2
    print CRC_CCITT16(bites, n, 0)