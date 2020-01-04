# -*- encoding: utf-8 -*-
"""
@File    : MyFrame.py
@Time    : 2020/1/4 15:13
@Author  : zx
@Email   : zhaoxiao@tju.edu.cn
@Software: PyCharm 
"""
import time

import wx
# from StatusBar import MyStatusBar
class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE, log=None):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)


        self.statusbar = self.CreateStatusBar(3)
        self.statusbar.SetStatusWidths([-3, -2,-1])
        self.statusbar.SetStatusText("系统正在运行", 0)
        self.statusbar.SetStatusText("Welcome to wxPython!", 1)
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(100)

    def Notify(self):
        try:
            st = time.strftime("%Y{y}%m{m}%d{d}%H{h}%M{m1}%S{s}").format(y='/', m='/', d='  ', h=":", m1=":", s="")
            self.SetStatusText(st, 2)
        except:
            self.timer.Stop()


class MyApp(wx.App):
    def OnInit(self):
        mainwin = MyFrame(None, wx.ID_ANY, " 健康食谱查询系统                       2020年1月   Version 0.100104A", size=(800,600),style=wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        mainwin.CenterOnParent(wx.BOTH)
        mainwin.Show()
        mainwin.Center(wx.BOTH)
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
