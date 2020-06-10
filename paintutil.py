import wxversion
wxversion.select('3.0')
from wx import *
import PIL.Image as pim

def clamp(n,hi,lo):
    return sorted([n,hi,lo])[1]

def pim_to_wx(p_img):
    wx_img = wx.EmptyImage( *p_img.size )
    rgba = p_img.copy()
    rgb = rgba.convert( 'RGB' )
    hasAlpha = rgba.mode[ -1 ] == 'A'
    rgb_str = rgb.tostring()
    wx_img.SetData(rgb_str)
    if hasAlpha:
        a_str = rgba.tostring()[3::4]
        wx_img.SetAlphaData( a_str )
    return wx_img

def wx_to_pim(wx_img):
    size = wx_img.GetSize()
    prgb = pim.new( 'RGB', size )
    prgb.fromstring( wx_img.GetData() )
    if wx_img.HasAlpha():
        prgba = pim.new( 'RGBA', size )
        r,g,b = prgb.split()
        a = pim.new('L', size)
        a.fromstring( wx_img.GetAlphaData() )
        prgba = pim.merge('RGBA',(r,g,b,a))
        return prgba
    else: return prgb

def pim_to_bmp(p_img):
    wx_img = pim_to_wx(p_img)
    return wx_img.ConvertToBitmap()
    
def bmp_to_pim(wx_bmp):
    wx_img = ImageFromBitmap(wx_bmp)
    return wx_to_pim(wx_img)

def load_bmp(path):
    p_img = pim.open(path)
    return pim_to_bmp(p_img)
    
def save_bmp(wx_bmp, path):
    p_img = bmp_to_pim(wx_bmp)
    p_img.save(path)

def strip(wx_bmp):
    w,h = size = wx_bmp.GetSize()
    n = w//h
    bmps = []
    for i in range(n):
        rect = Rect()
        rect.SetTopLeft((i*h,0))
        rect.SetBottomRight( ( ( (i+1) *h)-1, h-1))
        bmps.append( wx_bmp.GetSubBitmap(rect) )
    return bmps
    
def new_bmp(e):
    msg = Input("New File", [["Width", "300"],["Height","300"]])
    w,h = msg.get()
    msg.Destroy()
    print size
    bmp = EmptyBitmap(size[0],size[1])
    self.canvas.window.SetMinSize(size)
    self.Refresh()
    self.Update()
    self.SetTitle('Tok Paintbox')
            
class Input(Dialog):
    def __init__(self, msg, values=None, buttons=('Cancel','Ok')):
        Dialog.__init__(self, None, title=msg)
        panel = Panel(self)
        mainbox = BoxSizer(VERTICAL)
        self.outvalues = []
        if values:
            textbox = GridSizer(rows=len(values), cols=2,vgap=10,hgap=0)
            count = 0
            for n in range(len(values)):
                label = StaticText(panel, label=values[n][0])
                self.outvalues.append( TextCtrl(panel, value=values[n][1]) )
                textbox.AddMany([label, self.outvalues[n]])
            mainbox.Add(textbox, 0, EXPAND | ALL, 30 )
        else: mainbox.Add((0,20));
        buttbox = BoxSizer()
        btn0 = Button(panel, ID_CANCEL, label=buttons[0])
        btn1 = Button(panel, ID_OK, label=buttons[1])
        self.Bind(EVT_BUTTON, self.button, btn0)
        self.Bind(EVT_BUTTON, self.button, btn1)
        buttbox.AddMany([btn0,(60,0), btn1])
        mainbox.Add(buttbox, 0, EXPAND | ALL, 10 )
        panel.SetSizer(mainbox)
        mainbox.Fit(self)

    def button(self, e):
        eid = e.GetId()
        self.SetEscapeId(eid)
        self.EndModal(eid == ID_OK)
        self.Close()

    def get(self):
        ok = self.ShowModal() == 1
        values = []
        for n in range(len(self.outvalues)):
            values.append ( str(self.outvalues[n].GetValue()) )
        if values and ok:
            return values
        return ok
    def final():
        get = get(self)
        self.Destroy()
        return get
