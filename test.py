#!/usr/bin/env python
import time
import wx.html
import wx
import os

import sys

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


MENU_NEW_FILE = 10010
MENU_SAVE = 10011
MENU_OPEN_FILE = 10012
MENU_NEW_FOLDER = 10013
MENU_COPY = 10014
MENU_CUT = 10015
MENU_PASTE = 10016


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

        self.statusbar = self.CreateStatusBar(3)
        self.statusbar.SetStatusWidths([-3, -2, -1])
        self.statusbar.SetStatusText("          欢迎使用本系统", 0)
        self.statusbar.SetStatusText("Welcome to wxPython!", 1)
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

        self.newMyTheme = self._mb.GetRendererManager().AddRenderer(FM_MyRenderer())

        # Load toolbar icons (32x32)
        open_folder_bmp = wx.Bitmap(os.path.join(bitmapDir, "fileopen.png"), wx.BITMAP_TYPE_PNG)
        new_file_bmp = wx.Bitmap(os.path.join(bitmapDir, "filenew.png"), wx.BITMAP_TYPE_PNG)
        save_bmp = wx.Bitmap(os.path.join(bitmapDir, "filesave.png"), wx.BITMAP_TYPE_PNG)
        context_bmp = wx.Bitmap(os.path.join(bitmapDir, "contexthelp-16.png"), wx.BITMAP_TYPE_PNG)

        # Create a context menu
        context_menu = FM.FlatMenu()

        # Create the menu items
        menuItem = FM.FlatMenuItem(context_menu, wx.ID_ANY, "Test Item", "", wx.ITEM_NORMAL, None, context_bmp)
        context_menu.AppendItem(menuItem)

        item = FM.FlatMenuItem(fileMenu, MENU_NEW_FILE, "&登录", "登录", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        item.SetContextMenu(context_menu)

        self._mb.AddTool(MENU_NEW_FILE, "登录", new_file_bmp)

        item = FM.FlatMenuItem(fileMenu, MENU_SAVE, "&注册", "注册", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        self._mb.AddTool(MENU_SAVE, "注册", save_bmp)

        item = FM.FlatMenuItem(fileMenu, MENU_OPEN_FILE, "&注销", "注销", wx.ITEM_NORMAL)
        fileMenu.AppendItem(item)
        self._mb.AddTool(MENU_OPEN_FILE, "注销", open_folder_bmp)
        self._mb.AddSeparator()   # Toolbar separator

        # Add a wx.ComboBox to FlatToolbar
        combo = wx.ComboBox(self._mb, -1, choices=["Hello", "World", "wxPython"])
        self._mb.AddControl(combo)

        self._mb.AddSeparator()   # Separator

        stext = wx.StaticText(self._mb, -1, "Hello")
        #stext.SetBackgroundStyle(wx.BG_STYLE_CUSTOM )

        self._mb.AddControl(stext)

        self._mb.AddSeparator()   # Separator

        fileMenu.SetBackgroundBitmap(CreateBackgroundBitmap())

        # Add menu to the menu bar
        self._mb.Append(fileMenu, "&File")


    def ConnectEvents(self):

        # Attach menu events to some handlers
        self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnQuit, id=wx.ID_EXIT)

        if "__WXMAC__" in wx.Platform:
            self.Bind(wx.EVT_SIZE, self.OnSize)


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

# ------------------------------------------
# Event handlers
# ------------------------------------------

    def OnStyle(self, event):

        eventId = event.GetId()

        self._mb.ClearBitmaps()

        self._mb.Refresh()
        self._mtb.Refresh()
        self.Update()


    def OnShowCustom(self, event):

        self._mb.ShowCustomize(event.IsChecked())


    def OnLCDMonitor(self, event):

        self._mb.SetLCDMonitor(event.IsChecked())


    def OnTransparency(self, event):

        transparency = ArtManager.Get().GetTransparency()
        dlg = wx.TextEntryDialog(self, 'Please enter a value for menu transparency',
                                 'FlatMenu Transparency', str(transparency))

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        value = dlg.GetValue()
        dlg.Destroy()

        try:
            value = int(value)
        except:
            dlg = wx.MessageDialog(self, "Invalid transparency value!", "Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        if value < 0 or value > 255:
            dlg = wx.MessageDialog(self, "Invalid transparency value!", "Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        ArtManager.Get().SetTransparency(value)

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
            self.SetStatusText(st, 2)
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
        ctrl.AddPage(self.CreateHTMLCtrl(ctrl), "Welcome to AUI", False, page_bmp)

        panel = wx.Panel(ctrl, -1)
        flex = wx.FlexGridSizer(rows=0, cols=2, vgap=2, hgap=2)
        flex.Add((5, 5))
        flex.Add((5, 5))
        flex.Add(wx.StaticText(panel, -1, "wxTextCtrl:"), 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        flex.Add(wx.TextCtrl(panel, -1, "", wx.DefaultPosition, wx.Size(100, -1)),
                 1, wx.ALL | wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, "wxSpinCtrl:"), 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        flex.Add(wx.SpinCtrl(panel, -1, "5", wx.DefaultPosition, wx.Size(100, -1),
                             wx.SP_ARROW_KEYS, 5, 50, 5), 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        flex.Add((5, 5))
        flex.Add((5, 5))
        flex.AddGrowableRow(0)
        flex.AddGrowableRow(3)
        flex.AddGrowableCol(1)
        panel.SetSizer(flex)
        ctrl.AddPage(panel, "Disabled", False, page_bmp)

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "DClick Edit!", False, page_bmp)

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "Blue Tab")

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "A Control")

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 4")

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 5")

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 6")

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 7 (longer title)")

        ctrl.AddPage(wx.TextCtrl(ctrl, -1, "Some more text", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 8")

        # Demonstrate how to disable a tab
        ctrl.EnableTab(1, False)

        ctrl.SetPageTextColour(2, wx.RED)
        ctrl.SetPageTextColour(3, wx.BLUE)
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

        searchsizer = wx.BoxSizer(wx.VERTICAL)
        sh_sizer1= wx.BoxSizer()
        m_comboBox1Choices = [u"营养早餐", u"丰盛午餐", u"健康晚餐", u"肌肉食谱", u"孕妇食谱", u"春季食谱", u"夏季食谱", u"秋季食谱", u"冬季食谱"]
        self.m_comboBox1 = wx.ComboBox(self, wx.ID_ANY, u"营养早餐", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices,wx.CB_READONLY)
        sh_sizer1.Add(self.m_comboBox1, 7, wx.ALL, 5)
        self.more_button = AB.AquaButton(self, -1, None, "更多食谱")
        sh_sizer1.Add(self.more_button, 3, wx.ALL, 5)

        searchsizer.Add(sh_sizer1, 0, wx.ALL, 5)

        self.SetSizer(searchsizer)
        searchsizer.Layout()

        self.m_comboBox1.Bind(wx.EVT_COMBOBOX, self.OnChooseRecipes)
        self.more_button.Bind(wx.EVT_BUTTON,self.OnAButton)

    def OnChooseRecipes(self,eve):
        print("1")
        eve.Skip()

    def OnAButton(self,eve):
        print("2")
        eve.Skip()


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
