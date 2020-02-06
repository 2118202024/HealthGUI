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

from chat import ChatFrame1

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


        self._mgr.AddPane(self.CreateNotebook(), AuiPaneInfo().Name("main_panel").Top().
                          CenterPane())
        if self.id_num==USER_ID:
            self._mgr.AddPane(DoctorPanel(self, self.operator,self.doctor_info), AuiPaneInfo().Name("医师信息").
                              Caption("医师信息").Right().CloseButton(False).MaximizeButton(False).MinimizeButton(True).
                              MinSize(wx.Size(300, 150)))
            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().Name("test8").Caption("更多健康食谱文章").
                              Bottom().Right().CloseButton(False).MaximizeButton(True).
                              MinimizeButton(True).MinSize(wx.Size(300, 150)))
        elif self.id_num==MANAGER_ID:
            print('管理员')
        elif self.id_num == DOCTOR_ID:
            print('医生')
            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().Name("user_info").Caption("用户交流窗口").
                              Bottom().Right().CloseButton(False).MaximizeButton(True).
                              MinimizeButton(True).MinSize(wx.Size(300, 100)))
        else:
            print(self.id_num)


        self._mgr.AddPane(FeaturedRecipes(self), AuiPaneInfo().
                          Name("thirdauto").Caption("特色食谱").
                          Bottom().MinimizeButton(True).MinSize(wx.Size(800, 200)),
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

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "按身体异常搜索")

        # Demonstrate how to disable a tab

        ctrl.SetPageTextColour(1, wx.RED)
        ctrl.SetPageTextColour(2, wx.BLUE)
        ctrl.SetRenamable(2, True)

        return ctrl

    def SetOperator(self,name,id,doctor_info):
        self.operator=name
        self.id_num=id
        self.doctor_info=doctor_info


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
            majorname = wx.TextCtrl(self.mainPanel, wx.ID_ANY, self.doctor_info[i][2], wx.DefaultPosition, wx.Size(60, 20), wx.TE_READONLY)
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
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(wx.BLUE)
        m_comboBox1Choices = [u"营养早餐", u"丰盛午餐", u"健康晚餐", u"肌肉食谱", u"孕妇食谱", u"春季食谱", u"夏季食谱", u"秋季食谱", u"冬季食谱"]
        self.m_comboBox1 = wx.ComboBox(self.mainPanel, wx.ID_ANY, u"营养早餐", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices,wx.CB_READONLY)
        self.more_button = AB.AquaButton(self.mainPanel, -1, None, "更多食谱")

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

        self.sizer = wx.FlexGridSizer(1, 5, hgap=15, vgap=10)
        # self.subsizer1=wx.Sizer()

        example_bmp1 = wx.Bitmap('./bitmaps/椒盐大虾.jpg')
        m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY,example_bmp1, wx.DefaultPosition, (180, 120), 0)
        self.sizer.Add(m_bitmap1, 0, wx.EXPAND, 5)

        example_bmp2 = wx.Bitmap('./img/丸子头.jpg')
        m_bitmap2 = wx.StaticBitmap(self, wx.ID_ANY, example_bmp2, wx.DefaultPosition, (180, 120), 0)
        self.sizer.Add(m_bitmap2, 0, wx.EXPAND, 5)

        example_bmp3 = wx.Bitmap('./bitmaps/千叶豆腐.jpg')
        m_bitmap3 = wx.StaticBitmap(self, wx.ID_ANY, example_bmp3, wx.DefaultPosition, (180, 120), 0)
        self.sizer.Add(m_bitmap3, 0,wx.EXPAND, 5)

        example_bmp4 = wx.Bitmap('./bitmaps/牛排.jpg')
        m_bitmap4 = wx.StaticBitmap(self, wx.ID_ANY, example_bmp4, wx.DefaultPosition, (180, 120), 0)
        self.sizer.Add(m_bitmap4, 0, wx.EXPAND, 5)

        example_bmp5 = wx.Bitmap('./bitmaps/烧卖.jpg')
        example_bmp5.SetSize((180,120))
        m_bitmap5 = wx.StaticBitmap(self, wx.ID_ANY, example_bmp5, wx.DefaultPosition, wx.DefaultSize , 0)
        self.sizer.Add(m_bitmap5, 0, wx.EXPAND, 5)

        #第二行 菜谱名称
        # self.sizer.Add(name1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.searchsizer.Add(self.sizer, 0, wx.ALL, 5)
        self.m_searchCtrl1.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearchText)

    #
    def OnSearchText(self, eve):
        name=self.m_searchCtrl1.GetValue()
        try:
            sql="SELECT `details`,`recipe_name` FROM `recipe_details` WHERE `recipe_name` like '%%%s%%' "%name
            result=db.do_sql(sql)
        except:
            result=[]
            # return False
        maxlen=len(result)
        if maxlen==0:
            str1 = wx.StaticText(self, wx.ID_ANY, u"暂无推荐食谱，请重新输入", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.sizer.Add(str1, 0, wx.ALL, 5)
        elif maxlen>0:
            self.sizer.Clear()
            for i in range(maxlen):
                road = os.path.exists('./bitmaps/%s.jpg'%result[i][1])
                if road:
                    bmp = wx.Bitmap('./bitmaps/%s.jpg'%result[i][1])
                    bmp.SetSize((120,120))
                    self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY,
                                                 bmp, wx.DefaultPosition,wx.DefaultSize, 0)
                    self.sizer.Add(self.m_bitmap1, 0, wx.ALL, 5)
                else:
                    print('不存在')


        self.searchsizer.Layout()
        eve.Skip()

    def Ontest(self,eve):
        self.sizer.Clear()
        print(1)

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
