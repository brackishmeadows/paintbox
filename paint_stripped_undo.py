import wxversion
wxversion.select('3.0')
from wx import *
from copy import copy

class Canvas(ScrolledWindow):
    def __init__(self, parent, id = -1, size = DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size)

        self.parent = parent
        self.x = self.y = 0
        self.drawing = 0
        self.SetBackgroundColour("#666666")
        self.SetCursor(StockCursor(CURSOR_CROSS))
        self.SetScrollRate(20,20)
        self.buff()

        self.Bind(EVT_KEY_UP,       parent.key)

        self.Bind(EVT_PAINT,     self.paint)

        self.Bind(EVT_LEFT_DOWN, self.mouse)
        self.Bind(EVT_LEFT_DCLICK, self.mouse)
        self.Bind(EVT_LEFT_UP,   self.mouse)
        self.Bind(EVT_MOTION,    self.mouse)
        
    def buff(self,bmp=None,size=(300,300)):
        global bufferbmp    
        if bmp:
            bufferbmp = bmp
            self.SetVirtualSize(bmp.GetSize())
        else:
            bufferbmp = EmptyBitmap(size[0], size[1])
            self.SetVirtualSize(size)
            dc = BufferedDC(None, bufferbmp)
            dc.Clear()
        self.Refresh()

    def paint(self, e):
        global bufferbmp
        dc = BufferedPaintDC(self, bufferbmp, BUFFER_VIRTUAL_AREA)
        e.Skip()
        
    def pos(self, e): return self.CalcUnscrolledPosition(e.GetX(), e.GetY())

    def mouse(self, e):
        size = 5
        global bufferbmp
        if self.IsAutoScrolling():
            self.StopAutoScrolling()
        
        if e.LeftDown() or e.LeftDClick():
            self.SetFocus()
            self.CaptureMouse()
            self.x, self.y = self.pos(e)
            self.drawing = 1
            
        elif e.Dragging():
            #this is from the scrolledwindow demo
            dc = wx.BufferedDC(None, bufferbmp)
            dc.SetPen(Pen(wx.Colour(0,0,0), 3))
            coords = (self.x, self.y) + self.pos(e)
            dc.DrawLine(*coords)
            x1,y1, x2,y2 = dc.GetBoundingBox()
            x1,y1 = self.CalcScrolledPosition(x1, y1)
            x2,y2 = self.CalcScrolledPosition(x2, y2)
            rect = Rect()
            rect.SetTopLeft((x1,y1))
            rect.SetBottomRight((x2,y2))
            rect.Inflate(size,size)
            self.RefreshRect(rect)
            self.x, self.y = self.pos(e)
            
        elif e.LeftUp():
            if self.drawing:
                self.drawing = 0
                global history
                history.new()
            self.ReleaseMouse()
            self.x, self.y = self.pos(e)

class MainFrame(Frame):
    def __init__(self, parent, title):
        fstyle = CAPTION | RESIZE_BORDER | CLOSE_BOX
        Frame.__init__(self, parent, title=title, size=(500,400), style=fstyle)
        self.canvas = Canvas(self)
        self.Show(True)
        self.init_menu()
        self.new(None)

    def init_menu(self):
        menu= Menu()      
        menu_new = menu.Append(ID_NEW, "New")
        menu_undo = menu.Append(ID_UNDO, "Undo")
        menu_redo = menu.Append(ID_REDO, "Redo")

        self.Bind(EVT_MENU, self.new, menu_new)
        self.Bind(EVT_MENU, self.undo, menu_undo)
        self.Bind(EVT_MENU, self.redo, menu_redo)
        
        menuBar = MenuBar()
        menuBar.Append(menu,"File")
        self.SetMenuBar(menuBar)

    def key(self, e):
        '''self.canvas acts as the EventHandler for this method.
        that window eats key events, so im redirecting them to this frame.
        kind of hacky solution but whatever; it will work.'''
        if e.ControlDown():
            code = chr(e.GetKeyCode())
            if (code == 'Y'): self.redo(e)
            if (code == 'N'): self.new(e)
            if (code == 'Z'): self.undo(e)

    def new(self,e):
        print 'new'
        self.canvas.buff(size=(300,300))
        global history
        history.new(True)
        
    def undo(self,e):
        print 'undo'
        global history
        history.step_backward()
        self.Refresh()

    def redo(self,e):
        print 'redo'
        global history
        history.step_forward()
        self.Refresh()

class History():
    '''
    self.state is a list of copies of the buffer bitmap (using GetSubBitmap())
    self.tick keeps track of where you are in the undo stack
    '''
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
        'makes a clearer ascii representation than str(self.state)'
        for i in range(len(self.state)):
            print str(i) + ('[.]' if i == self.tick else '[ ]') +self.str(i)
        print self.tick
        print ''

    def str(self,tick):
        return str (self.state[tick])[-6:-4]

def clamp(n,lo,hi):
    return sorted([n,lo,hi])[1]
    
app = App(False)
history = History()
mainframe = MainFrame(None, 'Paint')

app.MainLoop()
