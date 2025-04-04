"""
gui_about.py: About frame
"""

import wx
import wx.adv
import logging

from .. import constants

from ..wx_gui import gui_support


class AboutFrame(wx.Frame):

    def __init__(self, global_constants: constants.Constants) -> None:
        if wx.FindWindowByName("关于"):
            return

        logging.info("Generating About frame")
        super(AboutFrame, self).__init__(None, title="关于", size=(350, 350), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.constants: constants.Constants = global_constants
        self.Centre()
        self.hyperlink_colour = (25, 179, 231)

        self._generate_elements(self)

        self.Show()


    def _generate_elements(self, frame: wx.Frame) -> None:

        # Set title
        title = wx.StaticText(frame, label="OCLP-Mod By laobamac", pos=(-1, 5))
        title.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title.Centre(wx.HORIZONTAL)

        # Set version
        version = wx.StaticText(frame, label=f"版本: {self.constants.patcher_version}", pos=(-1, title.GetPosition()[1] + title.GetSize()[1] + 5))
        version.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
        version.Centre(wx.HORIZONTAL)

        # Description
        description = [
            "这是一个喜欢咕咕的高中生Mod的OCLP",
            "SimpleHac[laobamac]修改并汉化",
            "SimpleHac资源社：www.simplehac.cn",
            "Q群：965625664",
        ]
        spacer = 5
        for line in description:
            desc = wx.StaticText(frame, label=line, pos=(-1, version.GetPosition()[1] + version.GetSize()[1] + 5 + spacer))
            desc.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            desc.Centre(wx.HORIZONTAL)

            spacer += 20

        # Set icon
        icon_mac = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/com.apple.macbook-unibody-plastic.icns"
        icon_mac = wx.StaticBitmap(frame, bitmap=wx.Bitmap(icon_mac, wx.BITMAP_TYPE_ICON), pos=(5, desc.GetPosition()[1] - 15))
        icon_mac.SetSize((160, 160))
        icon_mac.Centre(wx.HORIZONTAL)

        icon_path = str(self.constants.app_icon_path)
        icon = wx.StaticBitmap(frame, bitmap=wx.Bitmap(icon_path, wx.BITMAP_TYPE_ICON), pos=(5, desc.GetPosition()[1] + desc.GetSize()[1] + 17))
        icon.SetSize((64, 64))
        icon.Centre(wx.HORIZONTAL)

        # Set frame size
        frame.SetSize((-1, icon.GetPosition()[1] + icon.GetSize()[1] + 60))
