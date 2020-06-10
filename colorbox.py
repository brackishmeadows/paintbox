import wxversion
wxversion.select('3.0')
from wx import *

'''

colorbox by tocky matthew mungo scott park rundle, 2015

-adjust hue/saturation of selected colors
-graph shows all colors (or selected colors) in hsb space
-lock/unlock palette (no new colors can be introduced)
-image as palette
-tree style palette (ramps and wasd)

'''


class ColFrame(Frame):
    def __init__(self,parent,title):
        fstyle = CAPTION | RESIZE_BORDER | CLOSE_BOX
        Frame.__init__(self,parent,title=title,size=(220,300),style=fstyle)
        self.Show(True)

class ColCanvas(ScrolledWindow):
    def __init__(self, parent, id =-1, size=DefaultSize):
        ScrolledWindow.__init__(self,parent,id,(0,0),size=size)
        self.parent = parent
        self.SetBackgroundColour("#660000")
        self.SetScrollRate(20,20)
        
app = App(False)
colframe = ColFrame(None, "Color Box")
app.MainLoop()
