#!/usr/bin/env python2 
# -*- coding: utf8 -*-


import wx
import wx.gizmos
import wx.grid
import wx.lib.buttons
import wx.lib.newevent

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

#__________________________-
import constants
import main
from utils import *

from sys import exit
from datetime import datetime
from serial.serialutil import SerialException
from time import sleep



import threading
import thread
def create(parent):
    return main3(parent)

[wxID_MAIN3, wxID_MAIN3CONTAINER1, wxID_MAIN3CURRENT, 
 wxID_MAIN3DATEPICKERCTRL1, wxID_MAIN3DATEPICKERCTRL2, wxID_MAIN3DAY, 
 wxID_MAIN3FROM_PERIOD, wxID_MAIN3HOUR, wxID_MAIN3LEDNUMBERCTRL1, 
 wxID_MAIN3MONTH, wxID_MAIN3PORT, wxID_MAIN3PROCENT, wxID_MAIN3RCV_DATA, 
 wxID_MAIN3READ, wxID_MAIN3READ_PROCENT, wxID_MAIN3REGISTERS_LIST_LABEL, 
 wxID_MAIN3REGLIST, wxID_MAIN3SAVE, wxID_MAIN3STATUSBAR1, wxID_MAIN3TO_PERIOD, 
] = [wx.NewId() for _init_ctrls in range(20)]

(UpdateProcentEvent, EVT_UPDATE_PROCENT) = wx.lib.newevent.NewEvent()

class ProcentThread:
    """ CalcBarThread( self-win, 4, 225)       """
    def __init__(self, win, val):
        self.win = win
        self.val = val        
        self.LED = wx.gizmos.LEDNumberCtrl(parent=self.win, pos=wx.Point(128, 304), size=wx.Size(65, 40),
              style=wx.gizmos.LED_ALIGN_LEFT)      
        
    def Start(self,val = 0):
        self.val = val
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False


    def IsRunning(self):
        return self.running

    def Run(self):
        procent = self.val
        len_constants_table = 0
        len_reglist = 0
        while self.keepGoing and self.val < 100:
            sleep(1)
            if constants.table and self.win.reg_list:
                len_reglist = len(self.win.reg_list)
                len_constants_table = float(len(constants.table))
                if len_constants_table > len_reglist:
                    len_constants_table
                if len_constants_table:
                    #print "len_table=%d        len_reg=%d "%(len_constants_table , len_reglist)
                    self.val = (len_constants_table / len_reglist) * 100
                    if self.val > 100.0:
                        self.val = 100.0
                    self.LED.SetValue(str(int(self.val)))
                    self.LED.Refresh(False)
                    #print self.val
                    #busy = wx.BusyInfo(str(self.val))                    
            evt = UpdateProcentEvent(value = str(self.val))
            wx.PostEvent(self.win, evt)        
        self.running = False

class ReadThread:
    """ CalcBarThread( self-win, 4, 225)       """
    def __init__(self, win):
        self.win = win
        self.running = False
        
    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):        
	self.win.statusBar1.SetStatusText(number=0, text=u'')
	self.win.read.Show(False)
	try:
	    self.win.reg_list   = [int(x) for x in self.win.reglist.GetValue().split(';')]	
	except:
	    self.win.reg_list = None	    
	    self.win.reglist.SetValue('')
	# check nessesaries variables	
	if constants.moxaport == None:
	    #wx.MessageBox(str(constants.moxaport))
	    self.win.statusBar1.SetStatusText(number=0, text=u'не указан COM порт'); return
	elif not self.win.reg_list:
	    self.win.statusBar1.SetStatusText(number=0, text=u'не указан список регистров'); return	
	#wx.MessageBox('reading')		
	if self.win.current.GetValue():
	    self.win.arch_type = 'current'
	elif self.win.hour.GetValue():
	    self.win.arch_type = 'hour'
	elif self.win.day.GetValue():
	     self.win.arch_type = 'day'
	elif self.win.month.GetValue():
	     self.win.arch_type = 'month'	    
	constants.table = {}
	start_date = datetime.fromtimestamp(self.win.datePickerCtrl1.GetValue().GetTicks())	
	end_date   = datetime.fromtimestamp(self.win.datePickerCtrl2.GetValue().GetTicks())
	self.win.statusBar1.SetStatusText(number=0, text=u"Чтение \'%s\' архива с %s по %s" %(self.win.arch_type,start_date.strftime('%d.%m.%Y %H:%M'),end_date.strftime('%d.%m.%Y %H:%M')))	
        self.win.thread.Start()
	try:
	    main.read_archive(self.win.reg_list,start_date,end_date,self.win.arch_type)
	except SerialException:
	    self.win.statusBar1.SetStatusText(number=0, text=u'указанный COM порт не отвечает')
	    sleep(8)
	    exit(1)
	"""except:
	    self.win.statusBar1.SetStatusText(number=0, text=u'unkown error')
	    sleep(8)
	    exit(1)"""
	self.win.thread.Stop()
	while self.win.thread.IsRunning():
              print "thread alive"
              sleep(0.1)
	if not constants.table:
    	    dbmsg(7,"NO DATA")
    	    self.win.statusBar1.SetStatusText(number=0, text=u"Нет данных")
    	    #exit(1)
        
	print repr([constants.table[x] for x in self.win.reg_list ])
        constants.table = map(None,*[constants.table[x] for x in self.win.reg_list ] )
        
        if len(constants.table) < 2:
    	    dbmsg(7,"NO DATA")
    	    self.win.statusBar1.SetStatusText(number=0, text=u"Получены не полные данные - необходимо повторить приём")
    
	self.win.data = ""
        #print ">> ",repr(constants.table)
	if isinstance(constants.table[0],int):
                #print ">> ",repr(constants.table)
                #constants.table = tuple(constants.table[0]),(constants.table[1:]))
                constants.table = [[row] for row in constants.table]
                print ">> ",repr(constants.table)
	for row in constants.table:            
            self.win.data += ",".join([str(value) for value in row]) + "\n"        
                    
	
	self.win.recreateGrid(len(constants.table), len(constants.table[0]))
    
        col_cnt = 0
        print constants.table

	for reg_name in constants.table[0]:
	    #print reg_name
    	    self.win.rcv_data.SetColLabelValue(col_cnt, str(reg_name))
    	    col_cnt += 1
    	    
        row = 0
	for row_data in constants.table[1:]:
	    column = 0
    	    for column_data in row_data:
    		self.win.rcv_data.SetCellValue(row, column, column_data)    
		column +=1	    
	    row += 1
	#self.win.rcv_data.AutoSizeColumns()
	self.win.rcv_data.ForceRefresh()
        self.running = False
        

class main3(wx.Frame):    
        
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_MAIN3, name=u'main3', parent=prnt,
              pos=wx.Point(319, 290), size=wx.Size(800, 500),
              style=wx.DEFAULT_FRAME_STYLE, title=u'Data reciever')
        self.SetClientSize(wx.Size(800, 500))

        self.statusBar1 = wx.StatusBar(id=wxID_MAIN3STATUSBAR1,
              name='statusBar1', parent=self, style=0)

        self.datePickerCtrl1 = wx.DatePickerCtrl(id=wxID_MAIN3DATEPICKERCTRL1,
              name='datePickerCtrl1', parent=self, pos=wx.Point(56, 352),
              size=wx.Size(160, 32), style=wx.DP_SHOWCENTURY)

        self.datePickerCtrl2 = wx.DatePickerCtrl(id=wxID_MAIN3DATEPICKERCTRL2,
              name='datePickerCtrl2', parent=self, pos=wx.Point(264, 352),
              size=wx.Size(152, 32), style=wx.DP_SHOWCENTURY)

        self.read = wx.Button(id=wxID_MAIN3READ,
              label=u'\u0441\u0447\u0438\u0442\u0430\u0442\u044c',name=u'read',
              parent=self, pos=wx.Point(544, 352), size=wx.Size(240, 120),
              style=0)
        self.read.Bind(wx.EVT_LEFT_UP, self.OnReadLeftUp, id=wxID_MAIN3READ)
                
        self.from_period = wx.StaticText(id=wxID_MAIN3FROM_PERIOD, label=u'c',
              name=u'from_period', parent=self, pos=wx.Point(24, 360),
              size=wx.Size(24, 24), style=0)

        self.to_period = wx.StaticText(id=wxID_MAIN3TO_PERIOD,
              label=u'\u043f\u043e', name=u'to_period', parent=self,
              pos=wx.Point(232, 360), size=wx.Size(24, 24), style=0)

        self.reglist = wx.TextCtrl(id=wxID_MAIN3REGLIST, name=u'reglist',
              parent=self, pos=wx.Point(56, 392), size=wx.Size(480, 30),
              style=0, value=u'1003;1002;99;72;73;86;87;61;62;60')

        self.registers_list_label = wx.StaticText(id=wxID_MAIN3REGISTERS_LIST_LABEL,
              label=u'reg.', name=u'reglist_label', parent=self,
              pos=wx.Point(16, 400), size=wx.Size(32, 20), style=0)

        self.current = wx.RadioButton(id=wxID_MAIN3CURRENT,
              label=u'\u0442\u0435\u043a\u0443\u0449\u0438\u0435',
              name=u'current', parent=self, pos=wx.Point(16, 432),
              size=wx.Size(128, 32), style=0)
        self.current.SetValue(False)
        self.current.Bind(wx.EVT_RADIOBUTTON,self.OnCurrentButton)
        
        self.hour = wx.RadioButton(id=wxID_MAIN3HOUR,
              label=u'\u0447\u0430\u0441\u043e\u0432\u044b\u0435', name=u'hour',
              parent=self, pos=wx.Point(144, 432), size=wx.Size(120, 32),
              style=0)
        self.hour.SetValue(False)
        self.hour.Bind(wx.EVT_RADIOBUTTON,self.OnHourButton)

        self.day = wx.RadioButton(id=wxID_MAIN3DAY,
              label=u'\u0441\u0443\u0442\u043e\u0447\u043d\u044b\u0435',
              name=u'day', parent=self, pos=wx.Point(280, 432),
              size=wx.Size(136, 32), style=0)
        self.day.SetValue(True)
        self.day.Bind(wx.EVT_RADIOBUTTON,self.OnDayButton)
        
        self.month = wx.RadioButton(id=wxID_MAIN3MONTH,
              label=u'\u043c\u0435\u0441\u044f\u0447\u043d\u044b\u0435',
              name=u'month', parent=self, pos=wx.Point(432, 432),
              size=wx.Size(112, 32), style=0)
        self.month.SetValue(False)
        self.month.Bind(wx.EVT_RADIOBUTTON,self.OnMonthButton)

        self.port = wx.ComboBox(choices=[ "COM %d"%x for x in range(1,10) ], id=wxID_MAIN3PORT, name=u'port',
              parent=self, pos=wx.Point(424, 352), size=wx.Size(112, 30),
              style=0, value=u'COM 1')
        self.port.SetLabel(u'')
        self.port.Bind(wx.EVT_COMBOBOX, self.OnPortSet)
        self.port.Bind(wx.EVT_KEY_UP, self.OnPortSet)
        self.read = wx.Button(id=wxID_MAIN3READ,
              label=u'\u0441\u0447\u0438\u0442\u0430\u0442\u044c', name=u'read',
              parent=self, pos=wx.Point(544, 352), size=wx.Size(240, 120),style=0)
        self.read.Bind(wx.EVT_LEFT_UP, self.OnReadLeftUp)


        self.save = wx.lib.buttons.GenButton(id=wxID_MAIN3SAVE,
              label=u'\u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0434\u0430\u043d\u043d\u044b\u0435',
              name=u'save', parent=self, pos=wx.Point(544, 304),
              size=wx.Size(240, 40), style=0)        
        self.save.Bind(wx.EVT_LEFT_UP, self.OnSaveLeftUp, id=wxID_MAIN3SAVE)

        self.read_procent = wx.StaticText(id=wxID_MAIN3READ_PROCENT,
              label=u'\u0441\u0447\u0438\u0442\u0430\u043d\u043e' + ' %',
              name=u'read_procent', parent=self, pos=wx.Point(24, 320),
              size=wx.Size(88, 24), style=0)
           
        #self.Bind(EVT_UPDATE_PROCENT, self.OnPocentUpdate)

        self.thread = ProcentThread(self,0)
        self.read_thread = ReadThread(self)
        
        #self.recreateGrid(18,18)

        """self.rcv_data = wx.ListView(id=wxID_MAIN3RCV_DATA, name=u'rcv_data',
              parent=self, pos=wx.Point(8, 32), size=wx.Size(776, 256),
              style=wx.LC_ICON)"""
       
        self.rcv_data = wx.grid.Grid(id=wxID_MAIN3RCV_DATA, name=u'rcv_data',
              parent=self, pos=wx.Point(8, 32), size=wx.Size(776, 256),
              style=wx.SUNKEN_BORDER)
	self.rcv_data.EnableGridLines(True)        
	self.rcv_data.Bind(wx.EVT_LEFT_UP,self.GridRefresh)
        self.rcv_data.CreateGrid(2,4)
	
        """self.container1 = wx.SashWindow(id=wxID_MAIN3CONTAINER1,
              name=u'container1', parent=self, pos=wx.Point(0, 464),
              size=wx.Size(808, 108), style=wx.CLIP_CHILDREN | wx.SW_3D)"""

    """    def OnPocentUpdate(self,event):
        self.LED.SetValue(event.value)
        self.LED.Refresh(False)"""

    def OnSaveLeftUp(self, event):
	if not self.data:
		self.statusBar1.SetStatusText(number=0, text=u'Нет данных для сохранения')
		event.Skip()
		return
        dlg = wx.FileDialog(parent = self, message = "Save", defaultDir = ".",
		            defaultFile = "report.cvs",wildcard =  "*.csv", style = wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:    	    
	    self.filename = dlg.GetFilename()	    
	    open(self.filename,'w').write(self.data)
	    #exit(1)
        dlg.Destroy()
        event.Skip()
        

    def OnPortSet(self,event):
	#constants.port.close()        
	constants.moxaport = str(self.port.GetValue()).lower()
	if constants.moxaport.startswith('com'):
	    try:
		print "start with COM"
		constants.moxaport = int(constants.moxaport.lstrip('com ')) - 1		
	    except:
		self.statusBar1.SetStatusText(number=0, text=u'COM порт указан не верно')
		constants.moxaport = None
		
	elif constants.moxaport.startswith('ttyr'):
	    constants.moxaport = '/dev/' + constants.moxaport 
	elif constants.moxaport.startswith('/dev/ttyr'):
	    pass
	else:
	    self.statusBar1.SetStatusText(number=0, text=u'COM порт указан не верно')
	    constants.moxaport = None
	#wx.MessageBox('here')
	if constants.moxaport:
	    self.statusBar1.SetStatusText(number=0, text=u'установлен COM порт')
	event.Skip()
	return
	

    def OnFromPeriod(self,event):
	pass

    def OnCurrentButton(self,event):
        self.reglist.SetValue("1003;1002;1001;1004;72;73;86;87;61;62;60")
        self.statusBar1.SetStatusText(number=0, text=u'Чтение даты, времени, номера прибора,времени исправной работы,М1,М2,T1,T2,Q1,Q2,dQ')
        event.Skip()

    def OnHourButton(self,event):
        self.reglist.SetValue("1003;1002;99;72;73;86;87;61;62;60")
        self.statusBar1.SetStatusText(number=0, text=u'Чтение даты, времени, кода ошибки,М1,М2,T1,T2,Q1,Q2,dQ')
        event.Skip()

    def OnDayButton(self,event):
        self.reglist.SetValue("1003;99;72;73;86;87;61;62;60")
        self.statusBar1.SetStatusText(number=0, text=u'Чтение даты,кода ошибки,М1,М2,T1,T2,Q1,Q2,dQ')
        event.Skip()

    def OnMonthButton(self,event):
        self.reglist.SetValue("1003;99;60;61;62;68;69;97;110")
        self.statusBar1.SetStatusText(number=0, text=u'Чтение даты,кода ошибки,E1,E4,E5,V1,V2,V1*T1,V1*T2')
        event.Skip()

	
    def OnReadLeftUp(self,event):
        if self.read_thread.running:
            wx.MessageBox('3AHRTO')
            event.Skip()
            return
        self.read_thread.Start()
        #self.read_thread.Run()
        event.Skip()
    	
    def recreateGrid(self, row, col):        
        self.rcv_data.DeleteRows(0,self.rcv_data.GetNumberRows())
        self.rcv_data.DeleteCols(0,self.rcv_data.GetNumberCols())
        self.rcv_data.ClearGrid()
        self.rcv_data.InsertRows(0,row)
        self.rcv_data.InsertCols(0,col)

    def GridRefresh(self,event):
        self.rcv_data.ForceRefresh()
        event.Skip()

    def OnTimer(self,event):
        procent = 0
        if constants.table and self.reg_list:
           len_reglist = len(self.reg_list)                                
           len_constants_table = len(constants.table)
           if len_constants_table:
              procent = (len_constants_table / len_reglist) * 100
        self.LED.SetValue(str(procent),True)
        print "PROCENT = %d" % procent
        
	
    def __init__(self, parent):        
        self.filename = "report.cvs"
        global constants
        constants.moxaport = 0
	self.arch_type  = None
	self.start_date = None
	self.end_date   = None	
	self.reg_list	= None
	self.data = None
        self._init_ctrls(parent) 
        
        
        
        
        
        
