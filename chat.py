# -*- coding: utf-8 -*-

import wx
import wx.xrc

from HCJ_DB_Helper import HCJ_database

class ChatFrame1(wx.Frame):

    def __init__(self,parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(550, 500), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL):
        self.db = HCJ_database()
        self.myinit()
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.chatpanel = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(540, 300),
                                     wx.TE_MULTILINE)
        bSizer1.Add(self.chatpanel, 0, wx.ALL, 5)
        self.answerpanel = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(540, 90),
                                       wx.TE_MULTILINE)
        bSizer1.Add(self.answerpanel, 0, wx.ALL, 5)
        bSizer2 = wx.BoxSizer()
        self.bt_sumbit = wx.Button(self, wx.ID_ANY, u"发送", wx.DefaultPosition, wx.Size(250, 60), 0)
        bSizer2.Add(self.bt_sumbit, 0, wx.ALL, 3)
        self.bt_clear = wx.Button(self, wx.ID_ANY, u"清空", wx.DefaultPosition, wx.Size(250, 60), 0)
        bSizer2.Add(self.bt_clear, 0, wx.ALL|wx.RIGHT, 3)
        bSizer1.Add(bSizer2, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.Centre(wx.BOTH)

        # timer
        self.timer = wx.PyTimer(self.myTimerEvent)
        self.timer.Start(1000)
        # Connect Events
        self.bt_sumbit.Bind(wx.EVT_BUTTON, self.sumbit)
        self.bt_clear.Bind(wx.EVT_BUTTON, self.clear)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def __del__(self):
        self.timer.Stop()

    def OnClose(self, event):
        from HCJ_DB_Helper import HCJ_database
        db = HCJ_database()
        try:
            sql = "update `chatlog` set `read_state`=10  WHERE `rflag`='%s' "% self.flag
            db.upda_sql(sql)
        except:
            print('erro')
        self.timer.Stop()
        event.Skip()

    # Virtual event handlers, overide them in your derived class
    def myinit(self):
        self.user="user"
        self.server="server"
        self.flag=""
        self.rflag=""

    def setuser(self,str):
        self.user=str

    def setserver(self,str):
        self.server=str

    def setflag(self,user,server):
        self.flag=user+"-"+server
        self.rflag=server+"-"+user

    def myTimerEvent(self):
        sql = "SELECT id,info,user FROM chatlog where state=0 and (flag='%s' or rflag='%s' )order by id "%(self.flag,self.flag)
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
        self.chatpanel.ShowPosition(self.chatpanel.GetLastPosition())  # 移动到最底部

    def sumbit(self, event):
        if self.answerpanel.GetValue()!="":
            self.db_chat_update(self.answerpanel.GetValue(),self.user)
        self.answerpanel.SetValue("")
        event.Skip()

    def clear(self, event):
        sql = "update  chatlog  set state=1 where  (flag='%s' or rflag='%s')"%(self.flag,self.flag)
        self.db.upda_sql(sql)
        event.Skip()

    def db_chat_update(self,info,user1):
        sql="INSERT INTO chatlog (`info`,`user`,`flag`,`rflag`) VALUES ('%s','%s','%s','%s')"%(info,user1,self.flag,self.rflag)
        self.db.upda_sql(sql)