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
    
    def __init__(self, DEFAULT_CANVAS_WIDTH = 600, DEFAULT_CANVAS_HEIGHT = 600):
        self.root = Tk()
        
        # Menu v Tk okne
        self.menubar = Menu(self.root)
        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="Save", command=self.save)
        self.menu1.add_command(label="Save as...", command=self.save_as)
        self.menubar.add_cascade(label="File", menu=self.menu1)
        self.menu2 = Menu(self.menubar, tearoff=0)
        self.menu2.add_command(label="Undo", command=self.undo)
        self.menu2.add_command(label="Redo", command=self.redo)
        self.menubar.add_cascade(label="Edit", menu=self.menu2)
        self.root.config(menu=self.menubar)

        # 1. riadok buttonov v Tk gride
        self.eraser_button = Button(self.root, text='Eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=0)
        
        self.color_button = Button(self.root, text='Color', command=self.choose_color)
        self.color_button.grid(row=0, column=1)
        
        self.reset_button = Button(self.root, text='Reset', command=self.clear)
        self.reset_button.grid(row=0, column=2)

        self.choose_size_button = Scale(self.root, from_=1, to=10, orient=HORIZONTAL, label="Line size")
        self.choose_size_button.grid(row=0, column=3)
        
        # 2. riadok buttonov v Tk gride
        self.pen_button = Button(self.root, text='Pen', command=self.use_pen)
        self.pen_button.grid(row=1, column=0)
        
        self.line_button = Button(self.root, text='Line', command=self.use_line)
        self.line_button.grid(row=1,column=1)

        self.circle_button = Button(self.root, text='Circle', command=self.use_circle)
        self.circle_button.grid(row=1,column=2)

        self.point_button = Button(self.root, text='Point', command=self.use_point)
        self.point_button.grid(row=1,column=3)

        self.c = Canvas(self.root, bg='white', width=DEFAULT_CANVAS_WIDTH, height=DEFAULT_CANVAS_HEIGHT)
        self.c.grid(row=2, columnspan=4)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.root.title("New file - Tkinter Paint")
        
        self.old_x = None
        self.old_y = None
        self.size = 1
        self.choose_size_button.set(1)
        self.paint_color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.use_pen()
        
        self.Line_objects = []
        self.Circle_objects = []
        self.Point_objects = []
        self.stack = deque()
        
        self.c.bind('<Button-1>', self.start)
        self.c.bind('<B1-Motion>', self.motion)
        self.c.bind('<ButtonRelease-1>', self.end)


    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode
        self.paint_color = 'white' if self.eraser_on else self.paint_color
        self.outline_color = 'white' if self.eraser_on else self.paint_color


    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
    def choose_color(self):
        self.eraser_on = False
        self.paint_color = self.outline_color = askcolor(color=self.paint_color)[1]
    def clear(self):
        self.c.delete("all")
    
    def use_pen(self):
        self.tool = "pen"
        self.activate_button(self.pen_button)
    def use_line(self):
        self.tool = "line"
        self.activate_button(self.line_button)
    def use_circle(self):
        self.tool = "circle"
        self.activate_button(self.circle_button)   
    def use_point(self):
        self.tool = "point"
        self.activate_button(self.point_button)
            
            
    def start(self, event):
        if self.tool == 'line':
            self.line_start(event)
        elif self.tool == 'circle':
            self.circle_start(event)
        elif self.tool == 'point':
            self.point(event)
    
    def motion(self,event):
        if self.tool == "pen":
            self.pen_draw(event)
        elif self.tool == 'line':
            self.line_motion(event)
        elif self.tool == 'circle':
            self.circle_motion(event)
    
    def end(self,event):
        if self.tool == 'pen':
            self.old_x, self.old_y = None, None
        elif self.tool == 'line':
            self.line_end(event)
        elif self.tool == 'circle':
            self.circle_end(event)


    def pen_draw(self, event):
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.size, fill=self.paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def line_start(self,event):
        self.size = self.choose_size_button.get()
        self.line_start_x=event.x
        self.line_start_y=event.y
    def line_motion(self,event):
        self.c.delete('temp_line_objects')
        self.c.create_line(self.line_start_x, self.line_start_y, event.x, event.y, width=self.size, fill=self.paint_color, smooth=1, tags='temp_line_objects')
    def line_end(self, event):
        x = self.c.create_line(self.line_start_x, self.line_start_y, event.x, event.y, width=self.size, fill=self.paint_color, smooth=1)
        self.Line_objects.append(x)
        self.stack.append(x)

    def circle_start(self,event):
        self.circle_start_x = event.x
        self.circle_start_y = event.y
    def circle_motion(self,event):
        self.c.delete('temp_circle_objects')
        self.c.create_oval((self.circle_start_x), (self.circle_start_y), event.x, event.y, fill=self.paint_color, outline=self.outline_color, tags='temp_circle_objects')
    def circle_end(self, event):
        x = self.c.create_oval((self.circle_start_x), (self.circle_start_y), event.x, event.y, fill=self.paint_color, outline=self.outline_color)
        self.Circle_objects.append(x)
        self.stack.append(x)
    
    def point(self,event):
        self.size = self.choose_size_button.get()
        x = self.c.create_oval(event.x, event.y, event.x + self.size, event.y + self.size, fill=self.paint_color, outline=self.outline_color)
        self.Point_objects.append(x)

        
    def undo(self):
        if self.stack:
            object = self.stack.pop()
            object.destroy()
        pass
    
    def redo(self):
        pass
    
    def save(self):
        pass
        
    def save_as(self):
        project_path = pathlib.Path(__file__).parent.absolute()
        self.file_dir = str(asksaveasfilename(
            initialdir = project_path,
            defaultextension = ".ps", 
            filetypes=(("PostScript File", "*.ps"), 
                        ("PNG File", "*.png"))
        ))
        
        start_index = self.file_dir.rfind("/") + 1
        end_index = self.file_dir.rfind(".")
        file_name = self.file_dir[start_index:end_index]
        if file_name: 
            self.root.title(file_name + " - Tkinter Paint")
        
        if self.file_dir.endswith(".ps"):
            self.c.postscript(file = self.file_dir, colormode = 'color')
        elif self.file_dir.endswith(".png"):
            x2 = self.root.winfo_rootx() + self.c.winfo_x() + 2
            y2 = self.root.winfo_rooty() + self.c.winfo_y() + 2
            x1 = x2 + self.c.winfo_width() - 4
            y1 = y2 + self.c.winfo_height() - 4
            ImageGrab.grab().crop((x2,y2,x1,y1)).save(self.file_dir)
        else:
            print("No file specified.")


if __name__ == '__main__':
    Paint()