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


from sys import argv
from struct import pack, unpack
#from mx import DateTime
from datetime import datetime

def dbmsg(*arg):
    if arg[0] > 5:
	print " ".join([str(x) for x in arg[1:]])
    return

def pk2str(rs):
    to_dbmsg = ""
    for xxx in rs:
	try:
	    to_dbmsg += hex(unpack('B',xxx)[0]) + ","
	except:
	    dbmsg(8,'error unpack in pk2str bad byte = %s'%str(xxx) )
	    continue
    return to_dbmsg


def lst2hx(rs):
    if isinstance(rs,str):
	return  "[" + ",".join(["0x%x"%ord(x) for x in rs]) + "]"
    return "[" + ",".join(["0x%x"%x for x in rs]) + "]"

"""def DateTime2datetime(time):
    return datetime.fromtimestamp(float(time))"""

