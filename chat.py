# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrame1
###########################################################################
from HCJ_DB_Helper import HCJ_database

class ChatFrame1(wx.Frame):

    def __init__(self, parent):
        self.db = HCJ_database()
        self.myinit()
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(567, 468), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.chatpanel = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, 200),
                                     wx.TE_MULTILINE)
        bSizer1.Add(self.chatpanel, 0, wx.ALL, 5)

        self.cb_1 = wx.CheckBox(self, wx.ID_ANY, u"用户", wx.DefaultPosition, wx.DefaultSize, 0)
        self.cb_1.SetValue(True)
        bSizer1.Add(self.cb_1, 0, wx.ALL, 5)

        self.cb_2 = wx.CheckBox(self, wx.ID_ANY, u"医生", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.cb_2, 0, wx.ALL, 5)

        gSizer1 = wx.GridSizer(2, 1, 50, 0)

        self.answerpanel = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, 100),
                                       wx.TE_MULTILINE)
        gSizer1.Add(self.answerpanel, 0, wx.ALL, 5)

        gSizer2 = wx.GridSizer(1, 2, 10, 0)

        self.bt_sumbit = wx.Button(self, wx.ID_ANY, u"发送", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer2.Add(self.bt_sumbit, 0, wx.ALL, 5)

        self.bt_clear = wx.Button(self, wx.ID_ANY, u"清空", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer2.Add(self.bt_clear, 0, wx.ALL, 5)

        gSizer1.Add(gSizer2, 1, wx.EXPAND, 5)

        bSizer1.Add(gSizer1, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # timer
        self.timer = wx.PyTimer(self.myTimerEvent)
        self.timer.Start(1000)
        # Connect Events
        self.cb_1.Bind(wx.EVT_CHECKBOX, self.cb1_click)
        self.cb_2.Bind(wx.EVT_CHECKBOX, self.cb2_click)
        self.bt_sumbit.Bind(wx.EVT_BUTTON, self.sumbit)
        self.bt_clear.Bind(wx.EVT_BUTTON, self.clear)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def __del__(self):
        self.timer.Stop()

    def OnClose(self, event):

        self.timer.Stop()
        event.Skip()

    # Virtual event handlers, overide them in your derived class
    def myinit(self):
        self.user="user"
        self.server="server"
    def setuser(self,str):
        self.user=str

    def setserver(self,str):
        self.server=str

    def cb1_click(self, event):
        self.user="user"
        self.cb_1.SetValue(True)
        self.cb_2.SetValue(False)
        event.Skip()

    def cb2_click(self, event):
        self.server="server"
        self.cb_2.SetValue(True)
        self.cb_1.SetValue(False)
        event.Skip()
    def myTimerEvent(self):
        sql = "SELECT id,info,user FROM chatlog where state=0 order by id "
        t=self.db.do_sql(sql)
        self.updateChatPanel(t)
    def updateChatPanel(self,tuple):
        '''
        更新聊天
        (3, 'adfadsf', 'user')
        :param tuple:
        :return:
        '''
        str=""
        for tp in tuple:
            str1="%s : %s \n"%(tp[2],tp[1])
            str=str+str1
        self.chatpanel.SetValue(str)
    def sumbit(self, event):
        if self.answerpanel.GetValue()!="":
            self.db_chat_update(self.answerpanel.GetValue(),self.user)
        self.answerpanel.SetValue("")
        event.Skip()

    def clear(self, event):
        sql = "update  chatlog  set state=1 where 1"
        self.db.upda_sql(sql)
        event.Skip()

    def db_chat_update(self,info,user1):
        sql="INSERT INTO chatlog  (`info`,`user`) VALUES ('%s','%s')"%(info,user1)
        self.db.upda_sql(sql)

