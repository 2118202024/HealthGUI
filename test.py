#!/usr/bin/env python
import time
import wx.html
import wx
import os
import base64
import sys

from HCJ_DB_Helper import HCJ_database
from  RecipesSizer  import *
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

from chat import ChatFrame1

import wx.grid

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

MANAGER_ID=1
USER_ID=5
DOCTOR_ID=10

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
        self.statusbar.SetStatusWidths([-2, -1, -2, -1])
        self.statusbar.SetStatusText("        系统正在运行......", 0)
        self.statusbar.SetStatusText("", 1)
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(100)

        self.CreateMenu()
        self.ConnectEvents()

        # #
        self._notebook_style = aui.AUI_NB_DEFAULT_STYLE | wx.NO_BORDER
        self._notebook_style &= ~(aui.AUI_NB_CLOSE_BUTTON |
                                  aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |
                                  aui.AUI_NB_CLOSE_ON_ALL_TABS |
                                  aui.AUI_NB_TAB_MOVE |
                                  aui.AUI_NB_TAB_EXTERNAL_MOVE)
        self._notebook_theme = 5

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

    def DoNewLayout(self):
        helpMenu = FM.FlatMenu()
        helpImg = wx.Bitmap(os.path.join(bitmapDir, "help-16.png"), wx.BITMAP_TYPE_PNG)
        item = FM.FlatMenuItem(helpMenu, MENU_HELP, "&个人信息\tCtrl+A", "About...", wx.ITEM_NORMAL, None, helpImg)
        helpMenu.AppendItem(item)
        self._mb.Append(helpMenu, "&管理")

        if self.id_num==USER_ID:
            self._mgr.AddPane(self.CreateNotebook(), AuiPaneInfo().Name("main_panel").Top().
                              CenterPane())
            self._mgr.AddPane(DoctorPanel(self, self.operator,self.doctor_info), AuiPaneInfo().Name("医师信息").
                              Caption("医师信息").Right().CloseButton(False).MaximizeButton(False).MinimizeButton(True).
                              MinSize(wx.Size(300, 150)))
            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().Name("test8").Caption("更多健康食谱文章").
                              Bottom().Right().CloseButton(False).MaximizeButton(True).
                              MinimizeButton(True).MinSize(wx.Size(300, 150)))
        elif self.id_num==MANAGER_ID:
            print('管理员')
            self._mgr.AddPane(MangerInfoPanel(self, self.operator, self.doctor_info), AuiPaneInfo().Name("医师信息").
                              Caption("医师信息").Right().CloseButton(False).MaximizeButton(False).MinimizeButton(True).
                              MinSize(wx.Size(300, 150)))
        elif self.id_num == DOCTOR_ID:
            print('医生')
            self._mgr.AddPane(ChatUserInfoPanel(self, self.operator), AuiPaneInfo().Name("main_panel").Top().
                              CenterPane())

            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().Name("user_info").Caption("养生文章").
                              Bottom().Right().CloseButton(False).MaximizeButton(True).
                              MinimizeButton(True).MinSize(wx.Size(400, 200)))
        else:
            print(self.id_num)


        self._mgr.AddPane(FeaturedRecipes(self), AuiPaneInfo().
                          Name("thirdauto").Caption("特色食谱").
                          Bottom().MinimizeButton(True).MinSize(wx.Size(800, 240)),
                          target=self._mgr.GetPane("autonotebook"))

        self._mb.PositionAUI(self._mgr)
        self._mgr.Update()

    def CreateMenu(self):
        # Create the menubar
        self._mb = FM.FlatMenuBar(self, wx.ID_ANY, 32, 5, options = FM_OPT_SHOW_TOOLBAR )

        fileMenu  = FM.FlatMenu()


        self.newMyTheme = self._mb.GetRendererManager().AddRenderer(FM_MyRenderer())

        # Load toolbar icons (32x32)
        open_folder_bmp = wx.Bitmap(os.path.join(bitmapDir, "fileopen.png"), wx.BITMAP_TYPE_PNG)
        new_file_bmp = wx.Bitmap(os.path.join(bitmapDir, "filenew.png"), wx.BITMAP_TYPE_PNG)
        save_bmp = wx.Bitmap(os.path.join(bitmapDir, "filesave.png"), wx.BITMAP_TYPE_PNG)


        item = FM.FlatMenuItem(fileMenu, MENU_NEW_FILE, "&   登录\tCtrl+A", "登录", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)

        self._mb.AddTool(MENU_NEW_FILE, "登录", new_file_bmp)

        item = FM.FlatMenuItem(fileMenu, MENU_SAVE, "&   注册\tCtrl+B", "注册", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        self._mb.AddTool(MENU_SAVE, "注册", save_bmp)

        item = FM.FlatMenuItem(fileMenu, MENU_OPEN_FILE, "&   注销\tCtrl+C", "注销", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        self._mb.AddTool(MENU_OPEN_FILE, "注销", open_folder_bmp)
        self._mb.AddSeparator()   # Toolbar separator

        self._mb.AddSeparator()   # Separator

        fileMenu.SetBackgroundBitmap(CreateBackgroundBitmap())

        # Add menu to the menu bar
        self._mb.Append(fileMenu, "&File")

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
        sql = "SELECT `password`,`name`,`id_state`,`gender`,`major`,`score` FROM `user_info` WHERE 1 "
        result_all = db.do_sql(sql)
        paw_info = []
        id_info=[]
        doctor_info=[]
        for name in result_all:
            paw_temp=[]
            paw_temp.append(name[0])
            paw_temp.append(name[1])
            paw_info.append(paw_temp)
            id_temp = []
            id_temp.append(name[1])
            id_temp.append(name[2])
            id_info.append(id_temp)
            doc_tem=[]
            if name[2]==DOCTOR_ID:
                doc_tem.append(name[1])
                doc_tem.append(name[3])
                doc_tem.append(name[4])
                doc_tem.append(name[5])
                doctor_info.append(doc_tem)

        user_inform=dict(paw_info)
        id_inform=dict(id_info)
        return user_inform,id_inform,doctor_info

    def Onlogin(self, event):
        staff_inform ,name_id_info,doctor_all_info= self.GetUserInfo()
        dlg = wx.PasswordEntryDialog(self, '请输入系统管理员密码：', '系统登录')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            st = time.strftime("%Y{y}%m{m}%d{d}%H{h}%M{m1}%S{s}").format(y='/', m='/', d='  ', h=":", m1=":", s="")
            password = dlg.GetValue()
            if password in staff_inform or password == "hello8031":
                if password == "hello8031":
                    staff_name="超级用户"
                    self.statusbar.SetStatusText(u"操作员：" + staff_name,2)
                    id=5
                else:
                    staff_name = staff_inform[password]
                    self.statusbar.SetStatusText(u"操作员：" + staff_name,2)
                    id=name_id_info[staff_name]
                self.SetOperator(staff_name,id,doctor_all_info)
                self.DoNewLayout()
                # self._mgr.Update()
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

        ctrl.AddPage(OnStateSearch(ctrl), "按身体异常搜索",False, page_bmp)

        # Demonstrate how to disable a tab

        ctrl.SetPageTextColour(1, wx.RED)
        ctrl.SetPageTextColour(2, wx.BLUE)
        ctrl.SetRenamable(2, True)

        return ctrl

    def SetOperator(self,name,id,doctor_info):
        self.operator=name
        self.id_num=id
        self.doctor_info=doctor_info


class ChatUserInfoPanel(wx.Panel):
    def __init__(self, parent,operator):
        self.operator=operator
        wx.Panel.__init__(self, parent, -1)
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour((154,205,50))

        self.DoLayOut()

    def OnButton(self,eve):

        id=eve.GetId()
        name = "user_name_" + str(id)
        t = wx.FindWindowByName(name=name)
        name = t.GetValue()

        cf = ChatFrame1(None, wx.ID_ANY,'', size=wx.Size(550, 500),style=wx.CAPTION|wx.CLOSE_BOX)
        cf.setuser(self.operator)
        cf.setserver(name)
        cf.setflag(self.operator,name)
        cf.CenterOnParent(wx.BOTH)
        cf.Show()
        cf.Center(wx.BOTH)

        rname = self.operator + '-' +name
        self.ReadUpdateInfo(rname)
        eve.Skip()

    def DoLayOut(self):
        user_list=self.ReadChatInfo()
        MyID = 11000
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        usersizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(usersizer)

        for row in (user_list):
            MyID += 1
            sizername = wx.BoxSizer()

            namename = wx.TextCtrl(self.mainPanel, wx.ID_ANY, row[0], wx.DefaultPosition, wx.Size(60, 30),
                                       wx.TE_READONLY,name="user_name_"+str(MyID))
            sizername.Add(namename, 0, wx.EXPAND | wx.ALL, 3)
            majorname = wx.TextCtrl(self.mainPanel, wx.ID_ANY, str(row[3]), wx.DefaultPosition, wx.Size(78, 30), wx.TE_READONLY)
            sizername.Add(majorname, 0, wx.EXPAND | wx.ALL, 3)
            scorename = wx.TextCtrl(self.mainPanel, wx.ID_ANY,row[1], wx.DefaultPosition, wx.Size(235, 30), wx.TE_READONLY)
            sizername.Add(scorename, 0, wx.EXPAND | wx.ALL, 3)
            btmname = wx.Button(self.mainPanel, MyID, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
            self.Bind(wx.EVT_BUTTON, self.OnButton, btmname)
            sizername.Add(btmname, 0, wx.EXPAND | wx.ALL, 2)
            if row[2] == 0:
                namename.SetBackgroundColour(wx.YELLOW)
                majorname.SetBackgroundColour(wx.YELLOW)
                scorename.SetBackgroundColour(wx.YELLOW)
                btmname.SetBackgroundColour(wx.YELLOW)
            else:
                namename.SetBackgroundColour(wx.WHITE)
                majorname.SetBackgroundColour(wx.WHITE)
                scorename.SetBackgroundColour(wx.WHITE)
                btmname.SetBackgroundColour(wx.WHITE)
            usersizer.Add(sizername, 0, wx.EXPAND | wx.ALL, 3)

            usersizer.Layout()
        frameSizer.Add(self.mainPanel, 1, wx.EXPAND)
        self.SetSizer(frameSizer)
        frameSizer.Layout()

    def ReadChatInfo(self):
        sql = "SELECT `info`,`flag`,`rflag`,`read_state`,`date` FROM `chatlog` WHERE 1 "
        result_all = db.do_sql(sql)
        different_user_list = []
        useful_info=[]
        for row in result_all:
            doctor_info=row[2].split('-')
            if self.operator == doctor_info[0] :
                if doctor_info[1] in different_user_list :
                    pass
                else:
                    different_user_list.append(doctor_info[1])
                    useful_info.append([doctor_info[1],row[0],row[3],row[4]])
        return useful_info

    def ReadUpdateInfo(self,a):
        try:
            sql = "update `chatlog` set `read_state`=10  WHERE `rflag`='%s' "%a
            result_all = db.upda_sql(sql)
        except:
            print('erro')


class MangerInfoPanel(wx.Panel):
    def __init__(self, parent,operator,doctor_info):
        self.operator=operator
        self.doctor_info=doctor_info
        wx.Panel.__init__(self, parent, -1)
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(wx.BLUE)

        self.DoLayOut()


    def OnButton(self,eve):
        id=eve.GetId()
        name = "doctor_name_" + str(id)
        t = wx.FindWindowByName(name=name)
        name = t.GetValue()
        cf = ChatFrame1(None)
        cf.setuser(self.operator)
        cf.setserver(name)
        cf.setflag(self.operator,name)
        cf.CenterOnParent(wx.BOTH)
        cf.Show()
        cf.Center(wx.BOTH)
        eve.Skip()

    def DoLayOut(self):
        MyID = 10000
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        docsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(docsizer)

        for i in range(len(self.doctor_info)):
            MyID += 1
            sizername = wx.BoxSizer()
            namename = wx.TextCtrl(self.mainPanel, wx.ID_ANY, self.doctor_info[i][0], wx.DefaultPosition, wx.Size(60, 20),
                                       wx.TE_READONLY,name="doctor_name_"+str(MyID))
            sizername.Add(namename, 0, wx.EXPAND | wx.ALL, 3)
            majorname = wx.TextCtrl(self.mainPanel, wx.ID_ANY, self.doctor_info[i][2], wx.DefaultPosition, wx.Size(90, 20), wx.TE_READONLY)
            sizername.Add(majorname, 0, wx.EXPAND | wx.ALL, 3)
            scorename = wx.TextCtrl(self.mainPanel, wx.ID_ANY,self.doctor_info[i][3], wx.DefaultPosition, wx.Size(35, 20), wx.TE_READONLY)
            sizername.Add(scorename, 0, wx.EXPAND | wx.ALL, 3)
            btmname = wx.Button(self.mainPanel, MyID, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
            self.Bind(wx.EVT_BUTTON, self.OnButton, btmname)
            sizername.Add(btmname, 0, wx.EXPAND | wx.ALL, 2)
            docsizer.Add(sizername, 0, wx.EXPAND | wx.ALL, 3)

            docsizer.Layout()
        frameSizer.Add(self.mainPanel, 1, wx.EXPAND)
        self.SetSizer(frameSizer)
        frameSizer.Layout()


class DoctorPanel(wx.Panel):
    def __init__(self, parent,operator,doctor_info):
        self.operator=operator
        self.doctor_info=doctor_info
        wx.Panel.__init__(self, parent, -1)
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(wx.BLUE)

        self.DoLayOut()


    def OnButton(self,eve):
        id=eve.GetId()
        name = "doctor_name_" + str(id)
        t = wx.FindWindowByName(name=name)
        name = t.GetValue()
        cf = ChatFrame1(None)
        cf.setuser(self.operator)
        cf.setserver(name)
        cf.setflag(self.operator,name)
        cf.CenterOnParent(wx.BOTH)
        cf.Show()
        cf.Center(wx.BOTH)
        eve.Skip()

    def DoLayOut(self):
        MyID = 10000
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        docsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(docsizer)

        for i in range(len(self.doctor_info)):
            MyID += 1
            sizername = wx.BoxSizer()
            namename = wx.TextCtrl(self.mainPanel, wx.ID_ANY, self.doctor_info[i][0], wx.DefaultPosition, wx.Size(60, 20),
                                       wx.TE_READONLY,name="doctor_name_"+str(MyID))
            sizername.Add(namename, 0, wx.EXPAND | wx.ALL, 3)
            majorname = wx.TextCtrl(self.mainPanel, wx.ID_ANY, self.doctor_info[i][2], wx.DefaultPosition, wx.Size(90, 20), wx.TE_READONLY)
            sizername.Add(majorname, 0, wx.EXPAND | wx.ALL, 3)
            scorename = wx.TextCtrl(self.mainPanel, wx.ID_ANY,self.doctor_info[i][3], wx.DefaultPosition, wx.Size(35, 20), wx.TE_READONLY)
            sizername.Add(scorename, 0, wx.EXPAND | wx.ALL, 3)
            btmname = wx.Button(self.mainPanel, MyID, u"交流", wx.DefaultPosition, wx.DefaultSize, 0)
            self.Bind(wx.EVT_BUTTON, self.OnButton, btmname)
            sizername.Add(btmname, 0, wx.EXPAND | wx.ALL, 2)
            docsizer.Add(sizername, 0, wx.EXPAND | wx.ALL, 3)

            docsizer.Layout()
        frameSizer.Add(self.mainPanel, 1, wx.EXPAND)
        self.SetSizer(frameSizer)
        frameSizer.Layout()


class FeaturedRecipes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.SetBackgroundColour((34,139,34))
        m_comboBox1Choices = [u"营养早餐", u"丰盛午餐", u"健康晚餐", u"肌肉食谱", u"孕妇食谱", u"春季食谱", u"夏季食谱", u"秋季食谱", u"冬季食谱"]
        self.m_comboBox1 = wx.ComboBox(self, wx.ID_ANY, u"营养早餐", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices,wx.CB_READONLY)
        self.more_button = AB.AquaButton(self, -1, None, "更多食谱")

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        topsizer = wx.BoxSizer()
        self.RecipesSizer=RecipesSizer(self,"FeaturedRecipes")
        self.picSizer =self.RecipesSizer.getSizer()

        topsizer.Add(self.m_comboBox1, 7, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)
        topsizer.Add(self.more_button, 3, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        try:
            sql = "SELECT `details`,`recipe_name`,`Satisfaction` FROM `recipe_details` WHERE `recipe_type`='营养早餐' "
            result = db.do_sql(sql)
            self.RecipesSizer.changeSizer(result)
        except:
            print('erro')

        self.mainSizer.Add(topsizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.mainSizer.Add(self.picSizer, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(self.mainSizer)
        self.mainSizer.Layout()

        # self.DoLayout()
        self.BindEvents()

    def BindEvents(self):
        self.m_comboBox1.Bind(wx.EVT_COMBOBOX, self.OnChooseRecipes)
        self.more_button.Bind(wx.EVT_BUTTON, self.OnAButton)

    def OnChooseRecipes(self,eve):
        name = str(self.m_comboBox1.GetValue())
        try:
            sql = "SELECT `details`,`recipe_name`,`Satisfaction` FROM `recipe_details` WHERE `recipe_type`='%s' " % name
            result = db.do_sql(sql)
            self.RecipesSizer.changeSizer(result)
            self.mainSizer.Layout()
        except:
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

        self.sizer = wx.FlexGridSizer(1, 5, hgap=15, vgap=10)
        for x in range(5):
            bSizer1 = wx.BoxSizer(wx.VERTICAL)
            example_bmp1 = wx.Bitmap('./img/null.jpg')
            name="RecipesBitmap"+str(x)
            m_bitmap1 = wx.StaticBitmap(self,  wx.ID_ANY,example_bmp1, wx.DefaultPosition, (180, 120),0,name)
            bSizer1.Add(m_bitmap1, 0, wx.ALL, 5)
            name = "RecipesName" + str(x)
            m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,0,name)
            m_staticText1.Wrap(1)

            name = "RecipesSatisfaction" + str(x)
            bSizer1.Add(m_staticText1, 0, wx.ALIGN_CENTER, 5)
            m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,0,name)
            m_staticText2.Wrap(1)
            bSizer1.Add(m_staticText2, 0, wx.ALIGN_CENTER, 5)
            self.sizer.Add(bSizer1, 0, wx.EXPAND, 5)

        self.searchsizer.Add(self.sizer, 0, wx.ALL, 5)
        self.m_searchCtrl1.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearchText)

    def OnSearchText(self, eve):
        name=self.m_searchCtrl1.GetValue()
        try:
            sql="SELECT `details`,`recipe_name`,`Satisfaction` FROM `recipe_details` WHERE `recipe_name` like '%%%s%%' "%name
            result=db.do_sql(sql)
        except:
            result=[]
        maxlen=len(result)
        if maxlen==0:
            dlg = wx.MessageDialog(None, u'该菜谱不存在，请重新输入', '错误', wx.YES_DEFAULT)
            retCode = dlg.ShowModal()
            if (retCode == wx.ID_YES):
                pass
            else:
                pass
        elif maxlen>0:
            self.sizerClear()
            for i in range(maxlen):
                road = os.path.exists('./img/%s.jpg'%result[i][1])
                if road:
                    bmp = wx.Bitmap('./img/%s.jpg'%result[i][1])
                    # 图片
                    name = "RecipesBitmap" + str(i)
                    RecipesBitmap = wx.FindWindowByName(name=name)
                    RecipesBitmap.SetBitmap(bmp)
                    RecipesBitmap.SetToolTip(result[i][0])
                    # 菜名
                    name = "RecipesName" + str(i)
                    RecipesName = wx.FindWindowByName(name=name)
                    RecipesName.LabelText=result[i][1]
                    # 满意度
                    name = "RecipesSatisfaction" + str(i)
                    RecipesSatisfaction = wx.FindWindowByName(name=name)
                    RecipesSatisfaction.LabelText = u"满意度："+str(result[i][2])
                else:
                    print('不存在')
        self.searchsizer.Layout()
        eve.Skip()

    def sizerClear(self):
        # 容器初始化，每次上图的时候调用
        for x in range(5):
            bmp = wx.Bitmap('./img/null.jpg')
            # 图片
            name = "RecipesBitmap" + str(x)
            RecipesBitmap = wx.FindWindowByName(name=name)
            RecipesBitmap.SetBitmap(bmp)
            # 菜名
            name = "RecipesName" + str(x)
            RecipesName = wx.FindWindowByName(name=name)
            RecipesName.LabelText = ""
            # 满意度
            name = "RecipesSatisfaction" + str(x)
            RecipesSatisfaction = wx.FindWindowByName(name=name)
            RecipesSatisfaction.LabelText =""


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

        # 调用菜谱sizer
        self.RecipesSizer = RecipesSizer(self, "DiseaseRecipes")
        self.sizer = self.RecipesSizer.getSizer()

        searchsizer.Add(self.sizer, 0, wx.ALL, 5)

        self.SetSizer(searchsizer)
        searchsizer.Layout()
        self.m_comboBox1.Bind(wx.EVT_COMBOBOX, self.OnChooseRecipes)
    def OnChooseRecipes(self,eve):
        name = self.m_comboBox1.GetValue()
        try:
            sql="SELECT `recipe` FROM `recipe_disease_info` WHERE `disease_name`='%s' "%name
            result=db.do_sql_one(sql)
            if len(result)>0:
                RecipesList=result[0].split(";")
                RecipesList.remove("")
                str=""
                for name in RecipesList:
                    str=str+"'%s',"%name
                str=str[:-1]
                sql = "SELECT `details`,`recipe_name`,`Satisfaction` FROM `recipe_details` WHERE `recipe_name` in (%s) " % str
                result = db.do_sql(sql)
                self.RecipesSizer.changeSizer(result)

        except:
            result=[[]]
            print("暂无菜谱")


class OnStateSearch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        searchsizer = wx.BoxSizer(wx.VERTICAL)

        self.gSizer1 = wx.GridSizer(2, 6, -1, -1)
        searchsizer.Add(self.gSizer1, 0, wx.ALL, 5)
        # 读取数据库获得列表后添加checkbox
        self.AddCheckBox()
        # 添加按钮
        self.bt_StateSearchOK = wx.Button(self, wx.ID_ANY, u"提交", wx.DefaultPosition, wx.DefaultSize, 0)
        searchsizer.Add(self.bt_StateSearchOK, 0, wx.ALL, 5)
        # 添加label
        self.label_result = wx.StaticText(self, wx.ID_ANY, u"请选择您的症状并提交。", wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_result.Wrap(-1)
        searchsizer.Add(self.label_result, 0, wx.ALL, 5)
        # 调用菜谱sizer
        self.RecipesSizer = RecipesSizer(self, "DiseaseStateRecipes")
        self.sizer = self.RecipesSizer.getSizer()

        searchsizer.Add(self.sizer, 0, wx.ALL, 5)


        self.SetSizer(searchsizer)
        searchsizer.Layout()
        # self.m_comboBox1.Bind(wx.EVT_COMBOBOX, self.OnChooseRecipes)
        # 绑定事件
        self.bt_StateSearchOK.Bind(wx.EVT_BUTTON, self.StateSubmit)

    def StateSubmit(self,event):
        list1 = self.DiseaseStatelist
        DiseaseList=[]
        for i in range(len(list1)):
            name="DiseaseStateCB"+str(i)
            t = wx.FindWindowByName(name=name)
            IsChecked = t.IsChecked()
            if IsChecked:
                name=t.GetLabel()
                DiseaseList.append(self.DiseaseStateDict[name])
        DiseaseList = list(set(DiseaseList))
        str1=""
        for name in DiseaseList:
            str1=str1+name+" "
        # 把确诊显示出来
        if DiseaseList==[]:
            self.label_result.LabelText = "您还未选择不适原因，请选择后再提交。"
        else:
            self.label_result.LabelText="您可能患有 %s，下面为您推荐菜谱。"%str1
        self.GetRecipe(DiseaseList)

    def GetRecipe(self,DiseaseList):
        if DiseaseList==[]:
            pass
        else:
            str1=""
            for name in DiseaseList:
                str1 = str1 + "'%s'," % name
            sql = "SELECT `recipe` FROM `recipe_disease_info` WHERE `disease_name` in (%s) " % str1[:-1]
            result = db.do_sql(sql)
            Recipe=""
            for k in result:
                for t in k:
                    Recipe=Recipe+t

            RecipesList = Recipe.split(";")
            RecipesList.remove("")
            RecipesList=list(set(RecipesList))
            str = ""
            for name in RecipesList:
                str = str + "'%s'," % name
            str = str[:-1]
            sql = "SELECT `details`,`recipe_name`,`Satisfaction` FROM `recipe_details` WHERE `recipe_name` in (%s) " % str
            result = db.do_sql(sql)
            self.RecipesSizer.changeSizer(result)

    def getDiseaseStateDict(self):
        sql = "SELECT `state_name`,`kinds` FROM `disease_State` WHERE 1"
        result = db.do_sql(sql)
        list=[]
        dict={}
        for name in result:
            dict[name[0]]=name[1]
            list.append(name[0])
        self.DiseaseStateDict=dict
        self.DiseaseStatelist=list
        return list
    def AddCheckBox(self):
        self.getDiseaseStateDict()
        list=self.DiseaseStatelist
        for i in range(len(list)):
            name="DiseaseStateCB"+str(i)
            CheckBox= wx.CheckBox(self, wx.ID_ANY,list[i],name=name)

            self.gSizer1.Add(CheckBox, 0, wx.ALL, 5)
    def OnChooseRecipes(self,eve):
        name = self.m_comboBox1.GetValue()
        try:
            sql="SELECT `recipe` FROM `recipe_disease_info` WHERE `disease_name`='%s' "%name
            result=db.do_sql_one(sql)
            if len(result)>0:
                RecipesList=result[0].split(";")
                RecipesList.remove("")
                str=""
                for name in RecipesList:
                    str=str+"'%s',"%name
                str=str[:-1]
                sql = "SELECT `details`,`recipe_name`,`Satisfaction` FROM `recipe_details` WHERE `recipe_name` in (%s) " % str
                result = db.do_sql(sql)
                self.RecipesSizer.changeSizer(result)

        except:
            result=[[]]
            print("暂无菜谱")


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
