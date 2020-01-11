#!/usr/bin/env python
import time
import wx.html
import wx
import os
import base64
import sys

from HCJ_DB_Helper import HCJ_database

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

bitmapDir = os.path.join(dirName, 'bitmaps')
sys.path.append(os.path.split(dirName)[0])

try:
    from agw import flatmenu as FM
    from agw.artmanager import ArtManager, RendererBase, DCSaver
    from agw.fmresources import ControlFocus, ControlPressed
    from agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.flatmenu as FM
    from wx.lib.agw.artmanager import ArtManager, RendererBase, DCSaver
    from wx.lib.agw.fmresources import ControlFocus, ControlPressed
    from wx.lib.agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR

import images

try:
    from agw import aquabutton as AB
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aquabutton as AB

if wx.VERSION >= (2,7,0,0):
    import wx.lib.agw.aui as AUI
    AuiPaneInfo = AUI.AuiPaneInfo
    AuiManager = AUI.AuiManager
    _hasAUI = True
else:
    try:
        import PyAUI as AUI
        _hasAUI = True
        AuiPaneInfo = AUI.PaneInfo
        AuiManager = AUI.FrameManager
    except:
        _hasAUI = False

try:
    from agw import aui
    from agw.aui import aui_switcherdialog as ASD
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
    from wx.lib.agw.aui import aui_switcherdialog as ASD

import wx.lib.sized_controls as sc
db=HCJ_database()
MENU_NEW_FILE = 10010
MENU_SAVE = 10011
MENU_OPEN_FILE = 10012
MENU_NEW_FOLDER = 10013
MENU_COPY = 10014
MENU_CUT = 10015
MENU_PASTE = 10016
MENU_HELP=10017


# def invert_dict(d):
#     return dict([(v, k) for (k, v) in d.items()])

def switchRGBtoBGR(colour):

    return wx.Colour(colour.Blue(), colour.Green(), colour.Red())


def CreateBackgroundBitmap():

    mem_dc = wx.MemoryDC()
    bmp = wx.Bitmap(200, 300)
    mem_dc.SelectObject(bmp)

    mem_dc.Clear()

    # colour the menu face with background colour
    top = wx.Colour("blue")
    bottom = wx.Colour("light blue")
    filRect = wx.Rect(0, 0, 200, 300)
    mem_dc.GradientFillConcentric(filRect, top, bottom, wx.Point(100, 150))

    mem_dc.SelectObject(wx.NullBitmap)
    return bmp


class FM_MyRenderer(FM.FMRenderer):
    """ My custom style. """

    def __init__(self):

        FM.FMRenderer.__init__(self)


    def DrawMenuButton(self, dc, rect, state):
        """Draws the highlight on a FlatMenu"""

        self.DrawButton(dc, rect, state)


    def DrawMenuBarButton(self, dc, rect, state):
        """Draws the highlight on a FlatMenuBar"""

        self.DrawButton(dc, rect, state)


    def DrawButton(self, dc, rect, state, colour=None):

        if state == ControlFocus:
            penColour = switchRGBtoBGR(ArtManager.Get().FrameColour())
            brushColour = switchRGBtoBGR(ArtManager.Get().BackgroundColour())
        elif state == ControlPressed:
            penColour = switchRGBtoBGR(ArtManager.Get().FrameColour())
            brushColour = switchRGBtoBGR(ArtManager.Get().HighlightBackgroundColour())
        else:   # ControlNormal, ControlDisabled, default
            penColour = switchRGBtoBGR(ArtManager.Get().FrameColour())
            brushColour = switchRGBtoBGR(ArtManager.Get().BackgroundColour())

        # Draw the button borders
        dc.SetPen(wx.Pen(penColour))
        dc.SetBrush(wx.Brush(brushColour))
        dc.DrawRoundedRectangle(rect.x, rect.y, rect.width, rect.height,4)


    def DrawMenuBarBackground(self, dc, rect):

        # For office style, we simple draw a rectangle with a gradient colouring
        vertical = ArtManager.Get().GetMBVerticalGradient()

        dcsaver = DCSaver(dc)

        # fill with gradient
        startColour = self.menuBarFaceColour
        endColour   = ArtManager.Get().LightColour(startColour, 90)

        dc.SetPen(wx.Pen(endColour))
        dc.SetBrush(wx.Brush(endColour))
        dc.DrawRectangle(rect)


    def DrawToolBarBg(self, dc, rect):

        if not ArtManager.Get().GetRaiseToolbar():
            return

        # fill with gradient
        startColour = self.menuBarFaceColour()
        dc.SetPen(wx.Pen(startColour))
        dc.SetBrush(wx.Brush(startColour))
        dc.DrawRectangle(0, 0, rect.GetWidth(), rect.GetHeight())


class FlatMenuDemo(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE, log=None):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.SetIcon(images.Mondrian.GetIcon())

        if _hasAUI:
            self._mgr = AuiManager()
            self._mgr.SetManagedWindow(self)

        self._popUpMenu = None

        # Add log window
        self.log = log

        self.statusbar = self.CreateStatusBar(4)
        self.statusbar.SetStatusWidths([-3, -2, -1, -1])
        self.statusbar.SetStatusText("          欢迎使用本系统", 0)
        self.statusbar.SetStatusText("", 1)
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(100)

        self.CreateMenu()
        self.ConnectEvents()

        #
        self._notebook_style = aui.AUI_NB_DEFAULT_STYLE | wx.NO_BORDER
        self._notebook_style &= ~(aui.AUI_NB_CLOSE_BUTTON |
                                  aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |
                                  aui.AUI_NB_CLOSE_ON_ALL_TABS |
                                  aui.AUI_NB_TAB_MOVE |
                                  aui.AUI_NB_TAB_EXTERNAL_MOVE)
        self._notebook_theme = 5

        if _hasAUI:
            # AUI support
            self._mgr.AddPane(self.CreateNotebook(), AuiPaneInfo().Name("main_panel").Top().
                              CenterPane())

            self._mgr.AddPane(DoctorPanel(self), AuiPaneInfo().Name("医师信息").
                              Caption("医师信息").Right().
                              MinSize(wx.Size(300, 100)))

            self._mgr.AddPane(FeaturedRecipes(self), AuiPaneInfo().
                              Name("thirdauto").Caption("特色食谱").
                              Bottom().MinimizeButton(True).MinSize(wx.Size(800, 250)), target=self._mgr.GetPane("autonotebook"))

            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().Name("test8").Caption("更多健康食谱文章").
                              Bottom().Right().CloseButton(True).MaximizeButton(True).
                              MinimizeButton(True).MinSize(wx.Size(300, 100)))

            self._mb.PositionAUI(self._mgr)
            self._mgr.Update()

        ArtManager.Get().SetMBVerticalGradient(True)
        ArtManager.Get().SetRaiseToolbar(False)

        self._mb.Refresh()
        # self._mtb.Refresh()

        self.CenterOnScreen()


    def CreateHTMLCtrl(self, parent=None):

        if not parent:
            parent = self

        ctrl = wx.html.HtmlWindow(parent, -1, wx.DefaultPosition, wx.Size(400, 300))
        ctrl.SetPage(self.GetIntroText())
        return ctrl


    def CreateMenu(self):

        # Create the menubar
        self._mb = FM.FlatMenuBar(self, wx.ID_ANY, 32, 5, options = FM_OPT_SHOW_TOOLBAR | FM_OPT_SHOW_CUSTOMIZE)

        fileMenu  = FM.FlatMenu()
        helpMenu = FM.FlatMenu()

        self.newMyTheme = self._mb.GetRendererManager().AddRenderer(FM_MyRenderer())

        # Load toolbar icons (32x32)
        open_folder_bmp = wx.Bitmap(os.path.join(bitmapDir, "fileopen.png"), wx.BITMAP_TYPE_PNG)
        new_file_bmp = wx.Bitmap(os.path.join(bitmapDir, "filenew.png"), wx.BITMAP_TYPE_PNG)
        save_bmp = wx.Bitmap(os.path.join(bitmapDir, "filesave.png"), wx.BITMAP_TYPE_PNG)
        context_bmp = wx.Bitmap(os.path.join(bitmapDir, "contexthelp-16.png"), wx.BITMAP_TYPE_PNG)
        helpImg = wx.Bitmap(os.path.join(bitmapDir, "help-16.png"), wx.BITMAP_TYPE_PNG)
        # Create a context menu
        context_menu = FM.FlatMenu()

        item = FM.FlatMenuItem(helpMenu, MENU_HELP, "&个人信息\tCtrl+A", "About...", wx.ITEM_NORMAL, None, helpImg)
        helpMenu.AppendItem(item)

        # Create the menu items
        menuItem = FM.FlatMenuItem(context_menu, wx.ID_ANY, "Test Item", "", wx.ITEM_NORMAL, None, context_bmp)
        context_menu.AppendItem(menuItem)

        item = FM.FlatMenuItem(fileMenu, MENU_NEW_FILE, "&   登录", "登录", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        item.SetContextMenu(context_menu)

        self._mb.AddTool(MENU_NEW_FILE, "登录", new_file_bmp)

        item = FM.FlatMenuItem(fileMenu, MENU_SAVE, "&   注册", "注册", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        self._mb.AddTool(MENU_SAVE, "注册", save_bmp)

        item = FM.FlatMenuItem(fileMenu, MENU_OPEN_FILE, "&   注销", "注销", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        self._mb.AddTool(MENU_OPEN_FILE, "注销", open_folder_bmp)
        self._mb.AddSeparator()   # Toolbar separator

        self._mb.AddSeparator()   # Separator

        fileMenu.SetBackgroundBitmap(CreateBackgroundBitmap())

        # Add menu to the menu bar
        self._mb.Append(fileMenu, "&File")
        self._mb.Append(helpMenu, "&Help")

    def ConnectEvents(self):

        # Attach menu events to some handlers
        self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnQuit, id=wx.ID_EXIT)
        self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.Onlogin, id=MENU_NEW_FILE)#登录
        self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnRegistered, id=MENU_SAVE)#注册
        self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnQuit, id=MENU_OPEN_FILE)#注销
        self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnPersonalInfo, id=MENU_HELP)#个人信息

        if "__WXMAC__" in wx.Platform:
            self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnPersonalInfo(self, event):
        event.Skip()

    def OnRegistered(self, event):
        ls=FormDialog()
        ls.ShowModal()
        ls.Destroy()
        event.Skip()
    def GetUserInfo(self):
        sql = "SELECT `password`,`name` FROM `user_info` WHERE 1 "
        result = db.do_sql(sql)
        user_inform=dict(result)
        return user_inform

    def Onlogin(self, event):
        staff_inform = self.GetUserInfo()
        dlg = wx.PasswordEntryDialog(self, '请输入系统管理员密码：', '系统登录')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            st = time.strftime("%Y{y}%m{m}%d{d}%H{h}%M{m1}%S{s}").format(y='/', m='/', d='  ', h=":", m1=":", s="")
            password = dlg.GetValue()

            if password in staff_inform or password == "hello8031":
                try:
                    print(st + ' 登录成功\r\n')
                except:
                    pass
                if password == "hello8031":
                    self.statusbar.SetStatusText("超级用户", 2)

                else:
                    staff_name = staff_inform[password]
                    self.statusbar.SetStatusText(u"操作员：" + staff_name,2)

                # self._mgr.LoadPerspective(self.perspective_login)
                self._mgr.Update()
            else:
                try:
                    print(st + '  因密码错误，登录失败\r\n')
                    self.statusbar.SetStatusText("未登录",2)
                except:
                    pass
                ls = wx.MessageDialog(self, "密码错误！您无权登录系统，请联系管理员", "警告",
                                      wx.OK | wx.ICON_INFORMATION)
                ls.ShowModal()
                ls.Destroy()
                # self.log.WriteText('You entered: %s\n' % dlg.GetValue())
        dlg.Destroy()
        event.Skip()

    def OnSize(self, event):

        self._mgr.Update()
        self.Layout()

    def OnQuit(self, event):

        if _hasAUI:
            self._mgr.UnInit()

        self.Destroy()

    def CreatePopupMenu(self):

        if not self._popUpMenu:

            self._popUpMenu = FM.FlatMenu()
            #-----------------------------------------------
            # Flat Menu test
            #-----------------------------------------------

            # First we create the sub-menu item
            subMenu = FM.FlatMenu()
            subSubMenu = FM.FlatMenu()

            # Create the menu items
            menuItem = FM.FlatMenuItem(self._popUpMenu, 20001, "First Menu Item", "", wx.ITEM_CHECK)
            self._popUpMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(self._popUpMenu, 20002, "Sec&ond Menu Item", "", wx.ITEM_CHECK)
            self._popUpMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(self._popUpMenu, wx.ID_ANY, "Checkable-Disabled Item", "", wx.ITEM_CHECK)
            menuItem.Enable(False)
            self._popUpMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(self._popUpMenu, 20003, "Third Menu Item", "", wx.ITEM_CHECK)
            self._popUpMenu.AppendItem(menuItem)

            self._popUpMenu.AppendSeparator()

            # Add sub-menu to main menu
            menuItem = FM.FlatMenuItem(self._popUpMenu, 20004, "Sub-&menu item", "", wx.ITEM_NORMAL, subMenu)
            self._popUpMenu.AppendItem(menuItem)

            # Create the submenu items and add them
            menuItem = FM.FlatMenuItem(subMenu, 20005, "&Sub-menu Item 1", "", wx.ITEM_NORMAL)
            subMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(subMenu, 20006, "Su&b-menu Item 2", "", wx.ITEM_NORMAL)
            subMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(subMenu, 20007, "Sub-menu Item 3", "", wx.ITEM_NORMAL)
            subMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(subMenu, 20008, "Sub-menu Item 4", "", wx.ITEM_NORMAL)
            subMenu.AppendItem(menuItem)

            # Create the submenu items and add them
            menuItem = FM.FlatMenuItem(subSubMenu, 20009, "Sub-menu Item 1", "", wx.ITEM_NORMAL)
            subSubMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(subSubMenu, 20010, "Sub-menu Item 2", "", wx.ITEM_NORMAL)
            subSubMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(subSubMenu, 20011, "Sub-menu Item 3", "", wx.ITEM_NORMAL)
            subSubMenu.AppendItem(menuItem)

            menuItem = FM.FlatMenuItem(subSubMenu, 20012, "Sub-menu Item 4", "", wx.ITEM_NORMAL)
            subSubMenu.AppendItem(menuItem)

            # Add sub-menu to submenu menu
            menuItem = FM.FlatMenuItem(subMenu, 20013, "Sub-menu item", "", wx.ITEM_NORMAL, subSubMenu)
            subMenu.AppendItem(menuItem)


    def CreateLongPopupMenu(self):

        if hasattr(self, "_longPopUpMenu"):
            return

        self._longPopUpMenu = FM.FlatMenu()
        sub = FM.FlatMenu()

        #-----------------------------------------------
        # Flat Menu test
        #-----------------------------------------------

        for ii in range(30):
            if ii == 0:
                menuItem = FM.FlatMenuItem(self._longPopUpMenu, wx.ID_ANY, "Menu Item #%ld"%(ii+1), "", wx.ITEM_NORMAL, sub)
                self._longPopUpMenu.AppendItem(menuItem)

                for k in range(5):

                    menuItem = FM.FlatMenuItem(sub, wx.ID_ANY, "Sub Menu Item #%ld"%(k+1))
                    sub.AppendItem(menuItem)

            else:

                menuItem = FM.FlatMenuItem(self._longPopUpMenu, wx.ID_ANY, "Menu Item #%ld"%(ii+1))
                self._longPopUpMenu.AppendItem(menuItem)


    def OnStyle(self, event):

        eventId = event.GetId()

        self._mb.ClearBitmaps()

        self._mb.Refresh()
        self._mtb.Refresh()
        self.Update()


    def GetStringFromUser(self, msg):

        dlg = wx.TextEntryDialog(self, msg, "Enter Text")

        userString = ""
        if dlg.ShowModal() == wx.ID_OK:
            userString = dlg.GetValue()

        dlg.Destroy()

        return userString

    def OnAbout(self, event):

        msg = "This is the About Dialog of the FlatMenu demo.\n\n" + \
              "Author: Andrea Gavana @ 03 Nov 2006\n\n" + \
              "Please report any bug/requests or improvements\n" + \
              "to Andrea Gavana at the following email addresses:\n\n" + \
              "andrea.gavana@gmail.com\nandrea.gavana@maerskoil.com\n\n" + \
              "Welcome to wxPython " + wx.VERSION_STRING + "!!"

        dlg = wx.MessageDialog(self, msg, "FlatMenu wxPython Demo",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Notify(self):
        try:
            st = time.strftime("%Y{y}%m{m}%d{d}%H{h}%M{m1}%S{s}").format(y='/', m='/', d='  ', h=":", m1=":", s="")
            self.SetStatusText(st, 3)
        except:
            self.timer.Stop()

    def GetIntroText(self):
        text = \
            "<html><body>" \
            "<p><ul>" \
            "<li>Visual Studio 2005 style docking: <a href='http://www.kirix.com/forums/viewtopic.php?f=16&t=596'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=16&t=596</a></li>" \
            "<li>Dock and Pane Resizing: <a href='http://www.kirix.com/forums/viewtopic.php?f=16&t=582'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=16&t=582</a></li> " \
            "<li>Patch concerning dock resizing: <a href='http://www.kirix.com/forums/viewtopic.php?f=16&t=610'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=16&t=610</a></li> " \
            "<li>Patch to effect wxAuiToolBar orientation switch: <a href='http://www.kirix.com/forums/viewtopic.php?f=16&t=641'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=16&t=641</a></li> " \
            "<li>AUI: Core dump when loading a perspective in wxGTK (MSW OK): <a href='http://www.kirix.com/forums/viewtopic.php?f=15&t=627</li>'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=15&t=627</li></a>" \
            "<li>wxAuiNotebook reordered AdvanceSelection(): <a href='http://www.kirix.com/forums/viewtopic.php?f=16&t=617'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=16&t=617</a></li> " \
            "<li>Vertical Toolbar Docking Issue: <a href='http://www.kirix.com/forums/viewtopic.php?f=16&t=181'>" \
            "http://www.kirix.com/forums/viewtopic.php?f=16&t=181</a></li> " \
            "<li>Patch to show the resize hint on mouse-down in aui: <a href='http://trac.wxwidgets.org/ticket/9612'>" \
            "http://trac.wxwidgets.org/ticket/9612</a></li> " \
            "<li>The Left/Right and Top/Bottom Docks over draw each other: <a href='http://trac.wxwidgets.org/ticket/3516'>" \
            "http://trac.wxwidgets.org/ticket/3516</a></li>" \
            "<li>MinSize() not honoured: <a href='http://trac.wxwidgets.org/ticket/3562'>" \
            "http://trac.wxwidgets.org/ticket/3562</a></li> " \
            "<li>Layout problem with wxAUI: <a href='http://trac.wxwidgets.org/ticket/3597'>" \
            "http://trac.wxwidgets.org/ticket/3597</a></li>" \
            "<li>Resizing children ignores current window size: <a href='http://trac.wxwidgets.org/ticket/3908'>" \
            "http://trac.wxwidgets.org/ticket/3908</a></li> " \
            "<li>Resizing panes under Vista does not repaint background: <a href='http://trac.wxwidgets.org/ticket/4325'>" \
            "http://trac.wxwidgets.org/ticket/4325</a></li> " \
            "</ul>" \
            "</ul><p>" \
            "<p>" \
            "</body></html>"

        return text

    def CreateNotebook(self):

        # create the notebook off-window to avoid flicker
        client_size = self.GetClientSize()
        ctrl = aui.AuiNotebook(self, -1, wx.Point(client_size.x, client_size.y),
                               wx.Size(430, 200), agwStyle=self._notebook_style)

        arts = [aui.AuiDefaultTabArt, aui.AuiSimpleTabArt, aui.VC71TabArt, aui.FF2TabArt,
                aui.VC8TabArt, aui.ChromeTabArt]

        art = arts[self._notebook_theme]()
        ctrl.SetArtProvider(art)

        page_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
        ctrl.AddPage(OnRecipesSearch(ctrl), "按菜谱搜索", False, page_bmp)

        ctrl.AddPage(OnDiseaseSearch(ctrl),  "按病名搜索", False, page_bmp)

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "按身体异常搜索")

        # Demonstrate how to disable a tab

        ctrl.SetPageTextColour(1, wx.RED)
        ctrl.SetPageTextColour(2, wx.BLUE)
        ctrl.SetRenamable(2, True)

        return ctrl

class DoctorPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        docsizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer1=wx.BoxSizer()
        self.d_name1 = wx.TextCtrl(self,wx.ID_ANY, '刘丹', wx.DefaultPosition, wx.Size( 60,20 ), wx.TE_READONLY)
        h_sizer1.Add(self.d_name1, 0, wx.EXPAND | wx.ALL, 3)
        major = wx.TextCtrl(self,wx.ID_ANY, '中药学', wx.DefaultPosition, wx.Size( 60,20 ), wx.TE_READONLY)
        h_sizer1.Add(major, 0, wx.EXPAND | wx.ALL, 3)
        t_gender = wx.TextCtrl(self,wx.ID_ANY, '女', wx.DefaultPosition, wx.Size( 35,20 ), wx.TE_READONLY)
        h_sizer1.Add(t_gender, 0, wx.EXPAND | wx.ALL, 3)
        self.c_btn1 = wx.Button(self, 10001, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
        h_sizer1.Add(self.c_btn1, 0, wx.EXPAND | wx.ALL, 2)
        docsizer.Add(h_sizer1, 0, wx.EXPAND | wx.ALL, 3)
        #---
        h_sizer2 = wx.BoxSizer()
        self.d_name2 = wx.TextCtrl(self, wx.ID_ANY,'王辉', wx.DefaultPosition, wx.Size(60, 20),
                                   wx.TE_READONLY)
        h_sizer2.Add(self.d_name2, 0, wx.EXPAND | wx.ALL, 3)
        major = wx.TextCtrl(self, wx.ID_ANY, '中药学', wx.DefaultPosition, wx.Size(60, 20), wx.TE_READONLY)
        h_sizer2.Add(major, 0, wx.EXPAND | wx.ALL, 3)
        t_gender = wx.TextCtrl(self, wx.ID_ANY, '男', wx.DefaultPosition, wx.Size(35, 20), wx.TE_READONLY)
        h_sizer2.Add(t_gender, 0, wx.EXPAND | wx.ALL, 3)
        self.c_btn2 = wx.Button(self, 10002, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
        h_sizer2.Add(self.c_btn2, 0, wx.EXPAND | wx.ALL, 2)
        docsizer.Add(h_sizer2, 0, wx.EXPAND | wx.ALL, 3)
        #------
        h_sizer3 = wx.BoxSizer()
        self.d_name3 = wx.TextCtrl(self, wx.ID_ANY, '赵文斌', wx.DefaultPosition, wx.Size(60, 20),
                                   wx.TE_READONLY)
        h_sizer3.Add(self.d_name3, 0, wx.EXPAND | wx.ALL, 3)
        major = wx.TextCtrl(self, wx.ID_ANY, '中药学', wx.DefaultPosition, wx.Size(60, 20), wx.TE_READONLY)
        h_sizer3.Add(major, 0, wx.EXPAND | wx.ALL, 3)
        t_gender = wx.TextCtrl(self, wx.ID_ANY, '男', wx.DefaultPosition, wx.Size(35, 20), wx.TE_READONLY)
        h_sizer3.Add(t_gender, 0, wx.EXPAND | wx.ALL, 3)
        self.c_btn3 = wx.Button(self, 10003, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
        h_sizer3.Add(self.c_btn3, 0, wx.EXPAND | wx.ALL, 2)
        docsizer.Add(h_sizer3, 0, wx.EXPAND | wx.ALL, 3)

        #-----
        h_sizer4 = wx.BoxSizer()
        self.d_name4 = wx.TextCtrl(self, wx.ID_ANY,'王月', wx.DefaultPosition, wx.Size(60, 20),
                                   wx.TE_READONLY)
        h_sizer4.Add(self.d_name4, 0, wx.EXPAND | wx.ALL, 3)
        major = wx.TextCtrl(self, wx.ID_ANY,'中药学', wx.DefaultPosition, wx.Size(60, 20), wx.TE_READONLY)
        h_sizer4.Add(major, 0, wx.EXPAND | wx.ALL, 3)
        t_gender = wx.TextCtrl(self, wx.ID_ANY, '女', wx.DefaultPosition, wx.Size(35, 20), wx.TE_READONLY)
        h_sizer4.Add(t_gender, 0, wx.EXPAND | wx.ALL, 3)
        self.c_btn4 = wx.Button(self, 10004, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
        h_sizer4.Add(self.c_btn4, 0, wx.EXPAND | wx.ALL, 2)
        docsizer.Add(h_sizer4, 0, wx.EXPAND | wx.ALL, 3)
        #---
        h_sizer5 = wx.BoxSizer()
        self.d_name5 = wx.TextCtrl(self, wx.ID_ANY, '马医生', wx.DefaultPosition, wx.Size(60, 20),
                                   wx.TE_READONLY)
        h_sizer5.Add(self.d_name5, 0, wx.EXPAND | wx.ALL, 3)
        major = wx.TextCtrl(self, wx.ID_ANY, '中药学', wx.DefaultPosition, wx.Size(60, 20), wx.TE_READONLY)
        h_sizer5.Add(major, 0, wx.EXPAND | wx.ALL, 3)
        t_gender = wx.TextCtrl(self, wx.ID_ANY, '男', wx.DefaultPosition, wx.Size(35, 20), wx.TE_READONLY)
        h_sizer5.Add(t_gender, 0, wx.EXPAND | wx.ALL, 3)
        self.c_btn5 = wx.Button(self, 10005, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
        h_sizer5.Add(self.c_btn5, 0, wx.EXPAND | wx.ALL, 2)
        docsizer.Add(h_sizer5, 0, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(docsizer)
        docsizer.Layout()

        self.Bind(wx.EVT_BUTTON, self.OnButton, self.c_btn1)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.c_btn2)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.c_btn3)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.c_btn4)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.c_btn5)

    def OnButton(self,eve):
        id=eve.GetId()
        name=''
        if id==10001:
            name=self.d_name1.GetValue()
        elif id==10002:
            name = self.d_name2.GetValue()
        elif id==10003:
            name = self.d_name3.GetValue()
        elif id==10004:
            name = self.d_name4.GetValue()
        elif id==10005:
            name = self.d_name5.GetValue()
        ls = wx.MessageDialog(self, "抱歉！与"+str(name)+"的对话链接暂时无法打开，请稍后再试", "警告",
                              wx.OK | wx.ICON_INFORMATION)
        ls.ShowModal()
        ls.Destroy()
        eve.Skip()

class FeaturedRecipes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(wx.BLUE)
        # searchsizer = wx.BoxSizer(wx.VERTICAL)
        # sh_sizer1= wx.BoxSizer()
        m_comboBox1Choices = [u"营养早餐", u"丰盛午餐", u"健康晚餐", u"肌肉食谱", u"孕妇食谱", u"春季食谱", u"夏季食谱", u"秋季食谱", u"冬季食谱"]
        self.m_comboBox1 = wx.ComboBox(self.mainPanel, wx.ID_ANY, u"营养早餐", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices,wx.CB_READONLY)
        # sh_sizer1.Add(self.m_comboBox1, 7, wx.ALL, 5)
        self.more_button = AB.AquaButton(self.mainPanel, -1, None, "更多食谱")
        # self.more_button.SetForegroundColour(0,0,0)
        # sh_sizer1.Add(self.more_button, 3, wx.ALL, 5)

        # searchsizer.Add(sh_sizer1, 0, wx.ALL, 5)

        # self.SetSizer(searchsizer)
        # searchsizer.Layout()
        self.DoLayout()
        self.BindEvents()

    def DoLayout(self):
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        topsizer=wx.BoxSizer()
        picSizer = wx.FlexGridSizer(3, 5, 1, 15)

        topsizer.Add(self.m_comboBox1, 7, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 6 )
        topsizer.Add(self.more_button, 3, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        label1 = wx.StaticText(self.mainPanel, -1, "1 Colour")
        label2 = wx.StaticText(self.mainPanel, -1, "2 Colour")
        label3 = wx.StaticText(self.mainPanel, -1, "3 Colour")
        label4 = wx.StaticText(self.mainPanel, -1, "4 Colour")
        label5 = wx.StaticText(self.mainPanel, -1, "5 Colour")
        picSizer.Add(label1, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        picSizer.Add(label2, 0, wx.ALIGN_CENTER_VERTICAL)

        picSizer.Add(label3, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        picSizer.Add(label4, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        picSizer.Add(label5, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        labelBack = wx.StaticText(self.mainPanel, -1, "Background Colour")
        labelHover = wx.StaticText(self.mainPanel, -1, "Hover Colour")
        labelFocus = wx.StaticText(self.mainPanel, -1, "Focus Colour")
        labelText = wx.StaticText(self.mainPanel, -1, "Text Colour")
        label6 = wx.StaticText(self.mainPanel, -1, "6 Colour")

        picSizer.Add(labelBack)
        picSizer.Add(labelHover)
        picSizer.Add(labelFocus)
        picSizer.Add(labelText)
        picSizer.Add(label6)

        label7 = wx.StaticText(self.mainPanel, -1, "7 Colour")
        label8 = wx.StaticText(self.mainPanel, -1, "8 Colour")
        label9 = wx.StaticText(self.mainPanel, -1, "9 Colour")
        label10 = wx.StaticText(self.mainPanel, -1, "10 Colour")
        label11 = wx.StaticText(self.mainPanel, -1, "11 Colour")

        picSizer.Add(label7)
        picSizer.Add(label8)
        picSizer.Add(label9)
        picSizer.Add(label10)
        picSizer.Add(label11)

        mainSizer.Add(topsizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        mainSizer.Add(picSizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        boldFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldFont.SetWeight(wx.FONTWEIGHT_BOLD)

        for child in self.mainPanel.GetChildren():
            if isinstance(child, wx.StaticText):
                child.SetFont(boldFont)

        self.mainPanel.SetSizer(mainSizer)
        mainSizer.Layout()
        frameSizer.Add(self.mainPanel, 1, wx.EXPAND)
        self.SetSizer(frameSizer)
        frameSizer.Layout()
    def BindEvents(self):
        self.m_comboBox1.Bind(wx.EVT_COMBOBOX, self.OnChooseRecipes)
        self.more_button.Bind(wx.EVT_BUTTON, self.OnAButton)


    def OnChooseRecipes(self,eve):
        name = str(self.m_comboBox1.GetValue())
        #TODO
        try:
            sql = "SELECT `picture`,`details`,`recipe_name` FROM `recipe_details` WHERE `recipe_type`='%s' " % name
            result = db.do_sql(sql)
            for name in result():
                print(name[2])
        except:
            result = [[]]
            print('erro')
        eve.Skip()

    def OnAButton(self,eve):
        print("2")
        eve.Skip()

class OnRecipesSearch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.searchsizer = wx.BoxSizer(wx.VERTICAL)
        sh_sizer1 = wx.BoxSizer()
        self.m_searchCtrl1 = wx.SearchCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        sh_sizer1.Add(self.m_searchCtrl1, 7, wx.ALL, 5)
        self.more_button = AB.AquaButton(self, -1, None, "更多食谱")
        sh_sizer1.Add(self.more_button, 3, wx.ALL, 5)

        self.searchsizer.Add(sh_sizer1, 0, wx.ALL, 5)

        self.SetSizer(self.searchsizer)
        self.searchsizer.Layout()

        self.sizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
        self.searchsizer.Add(self.sizer, 0, wx.ALL, 5)
        self.m_searchCtrl1.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearchText)

    def OnSearchText(self, eve):
        name=self.m_searchCtrl1.GetValue()
        try:
            sql="SELECT `picture`,`details`,`recipe_name` FROM `recipe_details` WHERE `recipe_name` like '%%%s%%' "%name
            result=db.do_sql(sql)
        except:
            result=[]
        if len(result)==0:
            str1 = wx.StaticText( self, wx.ID_ANY, u"暂无推荐食谱，请重新输入", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.sizer.Add(str1, 0, wx.ALL, 5)
        elif len(result)>0:
            self.sizer.Clear()
            for name in result:
                with open('%s.jpg'%name[2], 'wb') as file:
                    image = base64.b64decode(name[0])  # 解码
                    file.write(image)
            t=wx.Bitmap('%s.jpg'%name[2],wx.BITMAP_TYPE_ANY)
            t.SetSize((120,120))
            self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY,
                                             t, wx.DefaultPosition, wx.DefaultSize, 0)
            self.sizer.Add(self.m_bitmap1, 0, wx.ALL, 9)

            # self.searchsizer.Add(self.sizer, 1, wx.EXPAND | wx.ALL, 20)

        self.searchsizer.Layout()
        eve.Skip()

class OnDiseaseSearch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        searchsizer = wx.BoxSizer(wx.VERTICAL)
        sh_sizer1 = wx.BoxSizer()
        m_comboBox1Choices = [u"高血压", u"糖尿病", u"心脏病", u"缺乏维生素A", u"缺乏维生素B", u"缺乏维生素E", u"缺铁", u"缺锌", u"缺钙"]
        self.m_comboBox1 = wx.ComboBox(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices,
                                       wx.CB_READONLY)
        sh_sizer1.Add(self.m_comboBox1, 7, wx.ALL, 5)
        self.more_button = AB.AquaButton(self, -1, None, "更多食谱")
        sh_sizer1.Add(self.more_button, 3, wx.ALL, 5)

        searchsizer.Add(sh_sizer1, 0, wx.ALL, 5)

        self.SetSizer(searchsizer)
        searchsizer.Layout()
        self.m_comboBox1.Bind(wx.EVT_COMBOBOX, self.OnChooseRecipes)
    def OnChooseRecipes(self,eve):
        name = self.m_comboBox1.GetValue()
        try:
            sql="SELECT `picture`,`details`,`recipe_name` FROM `recipe_details` WHERE `recipe_type`='%s' "%name
            result=db.do_sql(sql)
            for name in result():
                print(name[2])
        except:
            result=[[]]

def opj(path):
    """Convert paths to the platform-specific separator"""
    st = os.path.join(*tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st


class FormDialog(sc.SizedDialog):
    def __init__(self):
        sc.SizedDialog.__init__(self, None, -1, "用户注册",
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        pane = self.GetContentsPane()
        pane.SetSizerType("form")

        # row 1
        wx.StaticText(pane, -1, "姓名")
        textCtrl = wx.TextCtrl(pane, -1, "请输入姓名")
        textCtrl.SetSizerProps(expand=True)

        # row 2
        wx.StaticText(pane, -1, "所学专业")
        emailCtrl = wx.TextCtrl(pane, -1, "")
        emailCtrl.SetSizerProps(expand=True)

        # row 3
        wx.StaticText(pane, -1, "性别")
        wx.Choice(pane, -1, choices=["男", "女"])

        # row 4
        wx.StaticText(pane, -1, "联系方式")
        wx.TextCtrl(pane, -1, size=(100, -1)) # two chars for state

        # row 5
        wx.StaticText(pane, -1, "职称")

        # here's how to add a 'nested sizer' using sized_controls
        radioPane = sc.SizedPanel(pane, -1)
        radioPane.SetSizerType("horizontal")
        radioPane.SetSizerProps(expand=True)

        # make these children of the radioPane to have them use
        # the horizontal layout
        wx.RadioButton(radioPane, -1, "主任")
        wx.RadioButton(radioPane, -1, "副主任")
        wx.RadioButton(radioPane, -1, "普通")
        # end row 5

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

class MyApp(wx.App):
    def OnInit(self):
        mainwin = FlatMenuDemo(None, wx.ID_ANY, " 健康食谱查询系统                       2020年1月   Version 0.100104A",
                          size=(800, 600), style=wx.CAPTION | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        mainwin.CenterOnParent(wx.BOTH)
        mainwin.Show()
        mainwin.Center(wx.BOTH)
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
