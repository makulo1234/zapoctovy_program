from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import asksaveasfilename
from collections import deque
import pathlib
import pyscreenshot as ImageGrab
import ctypes

class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'
    
    # Windows fix pre high-DPI obrazovky
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # windows version >= 8.1
    except:
        ctypes.windll.user32.SetProcessDPIAware() # win 8.0 or less 
    
    def __init__(self):
        self.root = Tk()
        self.root.title("Tkinter Paint")
        
        # Menu v Tk okne
        self.menubar = Menu(self.root)
        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="Save as...", command=self.save_as)
        self.menubar.add_cascade(label="File", menu=self.menu1)
        self.menu2 = Menu(self.menubar, tearoff=0)
        self.menu2.add_command(label="Undo", command=self.undo)
        self.menu2.add_command(label="Redo", command=self.redo)
        self.menubar.add_cascade(label="Edit", menu=self.menu2)
        self.root.config(menu=self.menubar)

        # 1. riadok buttonov v Tk gride
        self.pen_button = Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.brush_button = Button(self.root, text='brush', command=self.use_brush)
        self.brush_button.grid(row=0, column=1)

        self.eraser_button = Button(self.root, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=2)
        
        self.color_button = Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=3)
        
        self.reset_button = Button(self.root, text='reset', command=self.clear)
        self.reset_button.grid(row=0, column=4)
        
        self.undo_button = Button(self.root, text='undo', command=self.undo)
        self.undo_button.grid(row=0, column=5)

        self.choose_size_button = Scale(self.root, from_=1, to=10, orient=HORIZONTAL)
        self.choose_size_button.grid(row=0, column=6)
        
        # 2. riadok buttonov v Tk gride
        self.line_button = Button(self.root, text='Line',command=self.set_tool("line"))
        self.line_button.grid(row=1,column=0)

        self.circle_button = Button(self.root, text='Circle',command= self.set_tool("circle"))
        self.circle_button.grid(row=1,column=1)

        self.point_button = Button(self.root, text='Point',command = self.set_tool("point"))
        self.point_button.grid(row=1,column=2)

        self.c = Canvas(self.root, bg='white', width=600, height=600)
        self.c.grid(row=2, columnspan=7)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.stack = deque()
        self.line_width = self.choose_size_button.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.c.bind('<Button-1>', self.start)
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_brush(self):
        self.activate_button(self.brush_button)

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y
    
    def set_tool(self, shape):
        self.tool_option = shape
        pass
    
    def start(self, event):
        # self.win = Canvas(self.c)
        pass

    def reset(self, event):
        self.old_x, self.old_y = None, None
        # self.stack.append(self.win)

    def clear(self):
        self.c.delete("all")
        
    def undo(self):
        # if self.stack:
        #     win = self.stack.pop()
        #     win.destroy()
        pass
    
    def redo(self):
        pass
    
    def save_as(self):
        project_path = pathlib.Path(__file__).parent.absolute()
        file_name = asksaveasfilename(
            initialdir = project_path,
            defaultextension = ".ps", 
            filetypes=(("PostScript File", "*.ps"), 
                        ("PNG File", "*.png"))
        )
        if file_name.endswith(".ps"):
            self.c.postscript(file = file_name, colormode = 'color')
        elif file_name.endswith(".png"):
            x2 = self.root.winfo_rootx() + self.c.winfo_x()
            y2 = self.root.winfo_rooty() + self.c.winfo_y()
            x1 = x2 + self.c.winfo_width()
            y1 = y2 + self.c.winfo_height()
            ImageGrab.grab().crop((x2,y2,x1,y1)).save(file_name)
        else:
            print("No file specified.")


if __name__ == '__main__':
    Paint()