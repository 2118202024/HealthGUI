'''
-*- coding: utf-8 -*-
@Author  : HCJ
@Time    : 2020-01-11 15:58
@Software: PyCharm
@File    : chatmain.py
'''
from chat import *


class MyApp(wx.App):
    def OnInit(self):
        mainwin = ChatFrame1(None)
        mainwin.CenterOnParent(wx.BOTH)
        mainwin.Show()
        mainwin.Center(wx.BOTH)
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()