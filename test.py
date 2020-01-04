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


MENU_NEW_FILE = 10005
MENU_SAVE = 10006
MENU_OPEN_FILE = 10007
MENU_NEW_FOLDER = 10008
MENU_COPY = 10009
MENU_CUT = 10010
MENU_PASTE = 10011


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

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Create a main panel and place some controls on it
        mainPanel = wx.Panel(self, wx.ID_ANY)

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        mainPanel.SetSizer(panelSizer)

        # Create minibar Preview Panel
        minibarPanel= wx.Panel(self, wx.ID_ANY)
        self.CreateMinibar(minibarPanel)
        miniSizer = wx.BoxSizer(wx.VERTICAL)
        miniSizer.Add(self._mtb, 0, wx.EXPAND)
        minibarPanel.SetSizer(miniSizer)

        # Add log window
        self.log = log

        # hs = wx.BoxSizer(wx.HORIZONTAL)
        # btn = wx.Button(mainPanel, wx.ID_ANY, "Press me for pop up menu!")
        # hs.Add(btn, 0, wx.ALL, 5)

        # Connect a button
        # btn.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        #
        # btn = wx.Button(mainPanel, wx.ID_ANY, "Press me for a long menu!")
        # hs.Add(btn, 0, wx.ALL, 5)
        #
        # panelSizer.Add(hs, 0, wx.ALL, 5)

        # Connect a button
        # btn.Bind(wx.EVT_BUTTON, self.OnLongButtonClicked)

        self.statusbar = self.CreateStatusBar(3)
        self.statusbar.SetStatusWidths([-3, -2, -1])
        self.statusbar.SetStatusText("          欢迎使用本系统", 0)
        self.statusbar.SetStatusText("Welcome to wxPython!", 1)
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(100)

        self.CreateMenu()
        self.ConnectEvents()

        mainSizer.Add(self._mb, 0, wx.EXPAND)
        mainSizer.Add(mainPanel, 1, wx.EXPAND)
        self.SetSizer(mainSizer)
        mainSizer.Layout()

        if _hasAUI:
            # AUI support
            self._mgr.AddPane(mainPanel, AuiPaneInfo().Name("main_panel").Top().
                              CenterPane())

            self._mgr.AddPane(minibarPanel, AuiPaneInfo().Name("minibar_panel").
                              Caption("Minibar Preview").Right().
                              MinSize(wx.Size(150, 100)))
            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().
                              Name("thirdauto").Caption("A Third Auto-NB Pane").
                              Bottom().MinimizeButton(True), target=self._mgr.GetPane("autonotebook"))

            self._mgr.AddPane(self.CreateHTMLCtrl(), AuiPaneInfo().Name("test8").Caption("Tree Pane").
                              Bottom().Right().CloseButton(True).MaximizeButton(True).
                              MinimizeButton(True).MinSize(wx.Size(150, 100)))
            self._mb.PositionAUI(self._mgr)
            self._mgr.Update()

        ArtManager.Get().SetMBVerticalGradient(True)
        ArtManager.Get().SetRaiseToolbar(False)

        self._mb.Refresh()
        self._mtb.Refresh()

        self.CenterOnScreen()


    def CreateHTMLCtrl(self, parent=None):

        if not parent:
            parent = self

        ctrl = wx.html.HtmlWindow(parent, -1, wx.DefaultPosition, wx.Size(400, 300))
        ctrl.SetPage(self.GetIntroText())
        return ctrl


    def CreateMinibar(self, parent):
        # create mini toolbar
        self._mtb = FM.FlatMenuBar(parent, wx.ID_ANY, 16, 6, options = FM_OPT_SHOW_TOOLBAR|FM_OPT_MINIBAR)

        checkCancelBmp = wx.Bitmap(os.path.join(bitmapDir, "ok-16.png"), wx.BITMAP_TYPE_PNG)
        viewMagBmp = wx.Bitmap(os.path.join(bitmapDir, "viewmag-16.png"), wx.BITMAP_TYPE_PNG)
        viewMagFitBmp = wx.Bitmap(os.path.join(bitmapDir, "viewmagfit-16.png"), wx.BITMAP_TYPE_PNG)
        viewMagZoomBmp = wx.Bitmap(os.path.join(bitmapDir, "viewmag-p-16.png"), wx.BITMAP_TYPE_PNG)
        viewMagZoomOutBmp = wx.Bitmap(os.path.join(bitmapDir, "viewmag-m-16.png"), wx.BITMAP_TYPE_PNG)

        self._mtb.AddCheckTool(wx.ID_ANY, "Check Settings Item", checkCancelBmp)
        self._mtb.AddCheckTool(wx.ID_ANY, "Check Info Item", checkCancelBmp)
        self._mtb.AddSeparator()
        self._mtb.AddRadioTool(wx.ID_ANY, "Magnifier", viewMagBmp)
        self._mtb.AddRadioTool(wx.ID_ANY, "Fit", viewMagFitBmp)
        self._mtb.AddRadioTool(wx.ID_ANY, "Zoom In", viewMagZoomBmp)
        self._mtb.AddRadioTool(wx.ID_ANY, "Zoom Out", viewMagZoomOutBmp)


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
            "<h3>Welcome to AUI</h3>" \
            "<br/><b>Overview</b><br/>" \
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
            "<p>Plus the following features:" \
            "<p><ul>" \
            "<li><b>AuiManager:</b></li>" \
            "<ul>" \
            "<li>Implementation of a simple minimize pane system: Clicking on this minimize button causes a new " \
            "<i>AuiToolBar</i> to be created and added to the frame manager, (currently the implementation is such " \
            "that panes at West will have a toolbar at the right, panes at South will have toolbars at the " \
            "bottom etc...) and the pane is hidden in the manager. " \
            "<li>Implementation of the <i>RequestUserAttention</i> method for panes;</li>" \
            "<li>Ability to show the caption bar of docked panes on the left instead of on the top (with caption " \
            "text rotated by 90 degrees then). This is similar to what <i>wxDockIt</i> did. To enable this feature on any " \
            "given pane, simply call <i>CaptionVisible(True, left=True)</i>;</li>" \
            "<li>New Aero-style docking guides: you can enable them by using the <i>AuiManager</i> style <tt>AUI_MGR_AERO_DOCKING_GUIDES</tt>;</li>" \
            "<li>New Whidbey-style docking guides: you can enable them by using the <i>AuiManager</i> style <tt>AUI_MGR_WHIDBEY_DOCKING_GUIDES</tt>;</li>" \
            "<li>A slide-in/slide-out preview of minimized panes can be seen by enabling the <i>AuiManager</i> style" \
            "<tt>AUI_MGR_PREVIEW_MINIMIZED_PANES</tt> and by hovering with the mouse on the minimized pane toolbar tool;</li>" \
            "<li>Native of custom-drawn mini frames can be used as floating panes, depending on the <tt>AUI_MGR_USE_NATIVE_MINIFRAMES</tt> style;</li>" \
            "<li>A 'smooth docking effect' can be obtained by using the <tt>AUI_MGR_SMOOTH_DOCKING</tt> style (similar to PyQT docking style);</li>" \
            '<li>Implementation of "Movable" panes, i.e. a pane that is set as `Movable()` but not `Floatable()` can be dragged and docked into a new location but will not form a floating window in between.</li>' \
            "</ul><p>" \
            "<li><b>AuiNotebook:</b></li>" \
            "<ul>" \
            "<li>Implementation of the style <tt>AUI_NB_HIDE_ON_SINGLE_TAB</tt>, a la <i>wx.lib.agw.flatnotebook</i>;</li>" \
            "<li>Implementation of the style <tt>AUI_NB_SMART_TABS</tt>, a la <i>wx.lib.agw.flatnotebook</i>;</li>" \
            "<li>Implementation of the style <tt>AUI_NB_USE_IMAGES_DROPDOWN</tt>, which allows to show tab images " \
            "on the tab dropdown menu instead of bare check menu items (a la <i>wx.lib.agw.flatnotebook</i>);</li>" \
            "<li>6 different tab arts are available, namely:</li>" \
            "<ul>" \
            "<li>Default 'glossy' theme (as in <i>wx.aui.AuiNotebook</i>)</li>" \
            "<li>Simple theme (as in <i>wx.aui.AuiNotebook</i>)</li>" \
            "<li>Firefox 2 theme</li>" \
            "<li>Visual Studio 2003 theme (VC71)</li>" \
            "<li>Visual Studio 2005 theme (VC81)</li>" \
            "<li>Google Chrome theme</li>" \
            "</ul>" \
            "</ul><p>" \
            "<p>" \
            "</body></html>"

        return text


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
