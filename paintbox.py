import wxversion
wxversion.select('3.0')
from wx import *
from wx.lib import colourselect as csel
from paintutil import *
from copy import copy
import re

'''
paintbox by tocky matthew mungo scott park rundle; 2015

todo:

-custom cursors
-second buffer for selection stuff/other tool stuff that draws on top
-selection mask
    -add/subtract/intersect selection
-transparency mask
-resize canvas controls
-palette
    -adjust hue/saturation of selected colors
    -graph shows all colors (or selected colors) in hsb space
    -lock/unlock palette (no new colors can be introduced)
    -image as palette
    -tree style palette (ramps and wasd)
-fill tool, magic wand selection

-tiles

-line/shape tools
    -eventually

-layers? animation? weird 8d shit

'''

tool = 1                      #the current tool id, 1 is the pencil tool
lcol = wx.Colour(0,0,0)       #left click brush color
rcol = wx.Colour(255,255,255) #right click brush color
size = 3                      #brush size in px (the right click is size+10px)


def setlcol(e): #e is a color or an event with a color
    col = e if isinstance(e,Colour) else e.GetValue()
    global lcol, lcol_ctrl
    lcol = col
    lcol_ctrl.SetValue(col)

def setrcol(e): #e is a color or an event with a color
    col = e if isinstance(e,Colour) else e.GetValue()
    global rcol,rcol_ctrl
    rcol = col
    rcol_ctrl.SetValue(col)
    
def settool(e):
    global tool, tb
    newid = e if isinstance(e,int) else e.GetId()
    if tool != newid:
        tool = newid
        tb.ToggleTool(tool, True)

def addsize(n):
    global size
    size+=n

class MainFrame(Frame):
    def __init__(self, parent, title):
        fstyle = CAPTION | RESIZE_BORDER | CLOSE_BOX
        Frame.__init__(self, parent, title=title, size=(500,400), style=fstyle)
        self.CreateStatusBar(2,style= STB_DEFAULT_STYLE & ~(STB_SIZEGRIP) ) 
        self.canvas = Canvas(self)
        self.init_menu()
        self.init_toolbar()
        self.Show(True)
        self.Bind(EVT_CLOSE, self.close)
   
    def init_menu(self):
        filemenu= Menu()
        editmenu= Menu()        
        file_new = filemenu.Append(ID_NEW, "New","Create a new image")
        file_open = filemenu.Append(ID_OPEN, "Open","Load an existing image")
        file_save = filemenu.Append(ID_SAVE, "Save","Save the current image")
        filemenu.AppendSeparator()
        file_exit = filemenu.Append(ID_EXIT,"Exit"," Quit the program")

        edit_undo = editmenu.Append(ID_UNDO, "Undo","Undo the last edit")
        edit_redo = editmenu.Append(ID_REDO, "Redo","Redo the last edit")

        self.Bind(EVT_MENU, self.new, file_new)
        self.Bind(EVT_MENU, self.load, file_open)
        self.Bind(EVT_MENU, self.save, file_save)
        self.Bind(EVT_MENU, self.close, file_exit)
        
        self.Bind(EVT_MENU, self.undo, edit_undo)
        self.Bind(EVT_MENU, self.redo, edit_redo)
        
        menuBar = MenuBar()
        menuBar.Append(filemenu,"File")
        menuBar.Append(editmenu,"Edit")
        self.SetMenuBar(menuBar)
    
    def init_toolbar(self):
        icons = strip(load_bmp("tool_icon.png"))
        self.toolnames = ['Color Picker','Pencil','Fill','Select','Zoom',
                          'Magic Wand']
        self.short = ['Q','B','F','','','','']
        global tb
        tb = self.CreateToolBar( TB_NODIVIDER )
        tb.SetToolBitmapSize((24,24))
        for i in (0, 1):
            tb.AddRadioLabelTool(i, self.toolnames[i], icons[i],
                        longHelp=self.toolnames[i], shortHelp=self.short[i])
            self.Bind(wx.EVT_TOOL, settool, id=i)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.configure, id=1)
        global tool, lcol, rcol
        tb.ToggleTool(tool, True)
        
        global lcol_ctrl
        lcol_ctrl = csel.ColourSelect(tb, -1, '', lcol,
                                       size=(30,30))
        self.Bind(csel.EVT_COLOURSELECT, setlcol, lcol_ctrl) 

        global rcol_ctrl
        rcol_ctrl = csel.ColourSelect(tb, -1, '', rcol,
                                       size=(30,30))
        self.Bind(csel.EVT_COLOURSELECT, setrcol, rcol_ctrl)

        tb.AddSeparator()
        tb.AddControl(lcol_ctrl) 
        tb.AddControl(rcol_ctrl)
        tb.Realize()

    def configure(self,e):
        tool = e.GetId()
        title = "Configure " + self.toolnames[tool]
        if tool == 1:
            global size
            msg = Input(title, [["Pencil Size", str(size)]])
            out = msg.get()
            if out:
                size = int(out[0])
            msg.Destroy()
            
    def new(self,e):
        msg = Input("New File", [["Width", "300"],["Height","300"]])
        if msg.get():
            w,h = msg.get()
            self.canvas.buff(size=(int(w),int(h)))
            self.SetTitle('Tok Paintbox')
        msg.Destroy()
        global history
        history.new(True)
        
    def save(self,e):
        fd = FileDialog(self, "Save File", "", "", "", FD_SAVE |
                        FD_OVERWRITE_PROMPT)
        if fd.ShowModal() == ID_CANCEL:
            return
        path = fd.GetPath()
        global bufferbmp
        bmp = bufferbmp
        isgood = bmp is not None and path is not None
        if not re.match('[^\.]*\.[^\.]*',path, re.I):
            path+='.png'
        
        if isgood:
            save_bmp(bmp, path)
            self.SetTitle(path)
            
    def load(self,e):
        fd = FileDialog(self, "Open File", "", "", "", FD_OPEN |
                        FD_FILE_MUST_EXIST)
        if fd.ShowModal() == ID_CANCEL:
            return
        path = fd.GetPath()
        self.canvas.buff(load_bmp(path))
        self.SetTitle(path)
        global history
        history.new(True)
        
    def close(self,e):
        e.StopPropagation()
        #if Input("Really quit?", buttons=('No','Yes')).final():
        self.Destroy()

    def key(self, e):
        #self.canvas acts as the EventHandler for keys.
        #that window eats key events, so im redirecting them to this frame.
        #kind of hacky solution but whatever; it will work.
        try: code = chr(e.GetKeyCode())
        except ValueError: code = e.GetKeyCode()
        if e.ControlDown():
            if   code == 'Z': self.undo(e)
            elif code == 'Y': self.redo(e)
        else:
            if   code == 'E': addsize(-1) #adjust brush size
            elif code == 'R': addsize(1) 
            elif code == 'Q': settool(0) #color picker
            elif code == 'B': settool(1) #pencil

    def undo(self,e):
        global history
        history.step_backward()
        self.Refresh()

    def redo(self,e):
        global history
        history.step_forward()
        self.Refresh()
        
class Canvas(ScrolledWindow):
    def __init__(self, parent, id = -1, size = DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size)
        self.Bind(EVT_KEY_UP, parent.key)

        self.parent = parent
        self.x = self.y = 0
        self.drawing = 0
        
        self.SetBackgroundColour("#666666")
        self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
        self.SetScrollRate(20,20)
        
        self.buff()

        global history
        history.new(True)
 
        self.Bind(wx.EVT_LEFT_DOWN,     self.mouse) 
        self.Bind(wx.EVT_LEFT_DCLICK,   self.mouse)
        self.Bind(wx.EVT_LEFT_UP,       self.mouse)
        self.Bind(wx.EVT_RIGHT_DOWN,    self.mouse)
        self.Bind(wx.EVT_RIGHT_DCLICK,  self.mouse)
        self.Bind(wx.EVT_RIGHT_UP,      self.mouse)
        self.Bind(wx.EVT_MOTION,        self.mouse)
        self.Bind(wx.EVT_PAINT,         self.paint)

    def buff(self,bmp=None,size=(300,300)):
        global bufferbmp    
        if bmp:
            bufferbmp = bmp
            self.SetVirtualSize(bmp.GetSize())
        else:
            bufferbmp = wx.EmptyBitmap(size[0], size[1])
            self.SetVirtualSize(size)
            dc = wx.BufferedDC(None, bufferbmp)
            dc.Clear()
        self.Refresh()

    def paint(self, e):
        global bufferbmp
        dc = wx.BufferedPaintDC(self, bufferbmp, wx.BUFFER_VIRTUAL_AREA)
        e.Skip()
        
    def pos(self, e): return self.CalcUnscrolledPosition(e.GetX(), e.GetY())

    def mouse(self, e):
        global bufferbmp
        if self.IsAutoScrolling():
            self.StopAutoScrolling()
        
        if ( e.LeftDown() or e.LeftDClick()
        or e.RightDown() or e.RightDClick() ):
            self.SetFocus()
            self.CaptureMouse()
            self.x, self.y = self.pos(e)
            global tool
            if tool == 1: #pencil 
                self.drawing = 1
                if e.RightDown() or e.RightDClick():
                    self.drawing = 2
            
        elif e.Dragging():
            if tool == 1 and self.drawing:
                self.pencil_draw(e)
            self.x, self.y = self.pos(e)
            
        elif (e.LeftUp() or e.RightUp()):
            if self.drawing:
                self.drawing = 0
                global history
                history.new()
            self.ReleaseMouse()
            self.x, self.y = self.pos(e)
            if tool == 0: #color picker
                self.color_pick(e)

    def pencil_draw(self, e):
        dc = wx.BufferedDC(None, bufferbmp)
        global lcol,rcol,size
        esize = size if self.drawing == 1 else size+10
        col = lcol if self.drawing ==1 else rcol
        dc.SetPen(wx.Pen(col, esize))
        coords = (self.x, self.y) + self.pos(e)
        dc.DrawLine(*coords)
        x1,y1, x2,y2 = dc.GetBoundingBox()
        x1,y1 = self.CalcScrolledPosition(x1, y1)
        x2,y2 = self.CalcScrolledPosition(x2, y2)
        rect = Rect()
        rect.SetTopLeft((x1,y1))
        rect.SetBottomRight((x2,y2))
        rect.Inflate(esize,esize)
        self.RefreshRect(rect)

    def color_pick(self,e):
        global lcol,rcol,lcol_ctrl,rcol_ctrl,tb
        dc = wx.BufferedDC(None, bufferbmp)
        col = dc.GetPixel(self.x,self.y)
        if e.LeftUp():
            lcol = col
            lcol_ctrl.SetColour(col)
        else:
            rcol = col
            rcol_ctrl.SetColour(col)
        tool = 1
        settool(1)

class History():
    def new(self, flush = False):
        self.state = [] if flush else self.state[:self.tick+1]

        global bufferbmp
        newbmp = bufferbmp.GetSubBitmap( Rect(0,0,bufferbmp.GetWidth(),
                                               bufferbmp.GetHeight() ) )
        self.state.append(newbmp)
        self.tick = len(self.state)-1
        self.show()
    
    def step_backward(self):
        global bufferbmp
        self.tick = clamp(self.tick-1, 0, len(self.state)-1)
        print self.tick, self.str(self.tick)
        bufferbmp = copy(self.state[self.tick])
        self.show()

    def step_forward(self):
        global bufferbmp
        self.tick = clamp(self.tick+1, 0, len(self.state)-1)
        print self.tick, self.str(self.tick)
        bufferbmp = copy(self.state[self.tick])
        self.show()

    def show(self):
        for i in range(len(self.state)):
            print str(i) + ('[.]' if i == self.tick else '[ ]') +self.str(i)
        print self.tick
        print ''

    def str(self,tick):
        return str (self.state[tick])[-6:-3]

app = App(False)
history = History()
mainframe = MainFrame(None, 'Paintbox')

app.MainLoop()
