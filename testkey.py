import wxversion
wxversion.select('3.0')
from wx import *
from wx.lib import colourselect as csel
from paintutil import *
from copy import copy
import re

class MainFrame(Frame):
    def __init__(self, parent, title):
        Frame.__init__( self, parent, title=title, size=(100,100),
                style=  CAPTION | RESIZE_BORDER | CLOSE_BOX)
        self.Bind(EVT_KEY_UP, self.key)
        
        StaticText(self, 0, "push stuff")
        self.Show()

    def key(self,e):
        try:
            print chr(e.GetKeyCode())+ " " + str(e.GetKeyCode())
        except ValueError:
            print '- '+ str(e.GetKeyCode())
app = App(False)
mainframe = MainFrame(None, 'key test')
app.MainLoop()

