import os

import wx
class RecipesSizer():
    def __init__(self,plane, planeName):
        self.planeName=planeName # RecipesBitmap 名称
        self.sizer = wx.FlexGridSizer(1, 5, hgap=15, vgap=10)
        for x in range(5):
            bSizer1 = wx.BoxSizer(wx.VERTICAL)
            example_bmp1 = wx.Bitmap('./img/null.jpg')
            # 图片
            name = self.planeName+"Bitmap" + str(x)
            m_bitmap1 = wx.StaticBitmap(plane,wx.ID_ANY, example_bmp1, wx.DefaultPosition, (180, 120), 0, name)
            bSizer1.Add(m_bitmap1, 0, wx.ALL, 5)
            # 菜名
            name = self.planeName+"Name" + str(x)
            m_staticText1 = wx.StaticText(plane, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0, name)
            m_staticText1.Wrap(1)
            # 满意度
            name = self.planeName+"Satisfaction" + str(x)
            bSizer1.Add(m_staticText1, 0, wx.ALIGN_CENTER, 5)
            m_staticText2 = wx.StaticText(plane, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0, name)
            m_staticText2.Wrap(1)
            bSizer1.Add(m_staticText2, 0, wx.ALIGN_CENTER, 5)
            self.sizer.Add(bSizer1, 0, wx.EXPAND, 5)
    def getSizer(self):
        return self.sizer
    def sizerClear(self):
        # 容器初始化，每次上图的时候调用
        for x in range(5):
            bmp = wx.Bitmap('./img/null.jpg')
            # 图片
            name = self.planeName + "Bitmap" + str(x)
            RecipesBitmap = wx.FindWindowByName(name=name)
            RecipesBitmap.SetBitmap(bmp)
            # 菜名
            name = self.planeName + "Name" + str(x)
            RecipesName = wx.FindWindowByName(name=name)
            RecipesName.LabelText = ""
            # 满意度
            name = self.planeName+"Satisfaction" + str(x)
            RecipesSatisfaction = wx.FindWindowByName(name=name)
            RecipesSatisfaction.LabelText = ""
    def changeSizer(self,result):
        maxlen = len(result)
        if maxlen == 0:
            dlg = wx.MessageDialog(None, u'该菜谱不存在，请重新输入', '错误', wx.YES_DEFAULT)
            retCode = dlg.ShowModal()
            if (retCode == wx.ID_YES):
                pass
            else:
                pass
        elif maxlen > 0:
            self.sizerClear()
            for i in range(maxlen):
                road = os.path.exists('./img/%s.jpg' % result[i][1])
                print("..."+result[i][1])
                if road:
                    bmp = wx.Bitmap('./img/%s.jpg' % result[i][1])
                    # 图片
                    name = self.planeName + "Bitmap" + str(i)
                    RecipesBitmap = wx.FindWindowByName(name=name)
                    RecipesBitmap.SetBitmap(bmp)
                    RecipesBitmap.SetToolTip(result[i][0])
                    # 菜名
                    name = self.planeName + "Name" + str(i)
                    RecipesName = wx.FindWindowByName(name=name)
                    RecipesName.LabelText = result[i][1]
                    # 满意度
                    name = self.planeName + "Satisfaction" + str(i)
                    RecipesSatisfaction = wx.FindWindowByName(name=name)
                    RecipesSatisfaction.LabelText = u"满意度：" + str(result[i][2])
                else:
                    print('不存在')
