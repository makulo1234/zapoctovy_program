from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.simpledialog import askfloat
from tkinter.messagebox import showinfo, showerror
import pathlib
from PIL import Image as Img
import pyscreenshot as ImageGrab

class Paint(object):
    """
    Paint App driven by Tkinter for drawing lines, circles, points with basic settings adjustments.

    Attributes
    ----------
    canvas_width : int
        the width of the drawing area (600 by default)
    canvas_height : int
        the width of the drawing area (600 by default)
    """

    DEFAULT_PEN_SIZE = 5
    DEFAULT_COLOR = 'black'
    DEFAULT_CANVAS_WIDTH = 600
    DEFAULT_CANVAS_HEIGHT = 600
    
    def __init__(self, canvas_width = DEFAULT_CANVAS_WIDTH, canvas_height = DEFAULT_CANVAS_HEIGHT):
        self.root = Tk()
        
        # Menu v Tk okne
        self.menubar = Menu(self.root)
        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="Save (Ctrl+S)", command=self.save)
        self.menu1.add_command(label="Save as... (Ctrl+A)", command=self.save_as)
        self.menubar.add_cascade(label="File", menu=self.menu1)
        
        self.menu2 = Menu(self.menubar, tearoff=0)
        self.menu2.add_command(label="Undo (Ctrl+Z)", command=self.undo)
        self.menubar.add_cascade(label="Edit", menu=self.menu2)
        
        self.menu3 = Menu(self.menubar, tearoff=0)
        self.menu3.add_command(label="Import image", command=self.import_img)
        self.menubar.add_cascade(label="Import", menu=self.menu3)
        
        self.root.config(menu=self.menubar)

        # 1. riadok buttonov v Tk gride
        self.eraser_button = Button(self.root, text='Eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=0)
        
        self.reset_button = Button(self.root, text='Reset', command=self.clear)
        self.reset_button.grid(row=0, column=1)
        
        self.color_button = Button(self.root, text='Color', command=self.choose_color)
        self.color_button.grid(row=0, column=2)
        
        self.current_color = Label(self.root, text="", padx=20, pady=10, bg=self.DEFAULT_COLOR)
        self.current_color.grid(row=0, column=3)

        self.choose_size_button = Scale(self.root, from_=1, to=10, orient=HORIZONTAL, label="Size")
        self.choose_size_button.grid(row=0, column=4)
        
        # 2. riadok buttonov v Tk gride
        self.pen_button = Button(self.root, text='Pen', command=self.use_pen)
        self.pen_button.grid(row=1, column=0)
        
        self.line_button = Button(self.root, text='Line', command=self.use_line)
        self.line_button.grid(row=1,column=1)

        self.circle_button = Button(self.root, text='Circle', command=self.use_circle)
        self.circle_button.grid(row=1,column=2)
        
        self.rectangle_button = Button(self.root, text='Rectangle', command=self.use_rectangle)
        self.rectangle_button.grid(row=1,column=3)
        
        self.polygon_button = Button(self.root, text='Polygon', command=self.use_polygon)
        self.polygon_button.grid(row=1,column=4)

        self.point_button = Button(self.root, text='Point', command=self.use_point)
        self.point_button.grid(row=1,column=5)

        
        self.c = Canvas(self.root, bg='white', width=canvas_width, height=canvas_height)
        self.c.grid(row=2, columnspan=6)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.root.title("New file - Tkinter Paint")
        self.project_path = pathlib.Path(__file__).parent.absolute()
        
        self.old_x = None
        self.old_y = None
        self.size = self.DEFAULT_PEN_SIZE
        self.choose_size_button.set(self.DEFAULT_PEN_SIZE)
        self.paint_color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.use_pen()
        
        self.Pen_objects = []
        self.Line_objects = []
        self.Circle_objects = []
        self.Rectangle_objects = []
        self.Polygon_objects = []
        self.Point_objects = []
        self.stack = []
        self.polygon_points = []
        self.polygon_temp = []
        self.file_dir = ""
        
        self.c.bind('<Button-1>', self.start)
        self.c.bind('<B1-Motion>', self.motion)
        self.c.bind('<ButtonRelease-1>', self.end)
        self.c.bind("<Button-3>", self.mouse_right)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-s>", self.save)
        self.root.bind("<Control-a>", self.save_as)


    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode
        self.paint_color = self.outline_color = 'white' if self.eraser_on else self.paint_color

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
        self.current_color.config(bg="white")
    def choose_color(self):
        self.eraser_on = False
        self.paint_color = self.outline_color = askcolor(color=self.paint_color)[1]
        self.current_color.config(bg=self.paint_color)
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
    def use_rectangle(self):
        self.tool = "rectangle"
        self.activate_button(self.rectangle_button)
    def use_polygon(self):
        showinfo(title="Polygon tutorial", message="Left-click to create polygon points and then right-click to create polygon.")
        self.tool = "polygon"
        self.activate_button(self.polygon_button)
    def use_point(self):
        self.tool = "point"
        self.activate_button(self.point_button)
            
            
    def start(self, event):
        if self.tool == "pen":
            self.size = self.choose_size_button.get()
        elif self.tool == 'line':
            self.line_start(event)
        elif self.tool == 'circle':
            self.circle_start(event)
        elif self.tool == 'rectangle':
            self.rectangle_start(event)
        elif self.tool == "polygon":
            self.polygon_point(event)
        elif self.tool == 'point':
            self.point(event)
    
    def motion(self,event):
        if self.tool == "pen":
            self.pen_draw(event)
        elif self.tool == 'line':
            self.line_motion(event)
        elif self.tool == 'circle':
            self.circle_motion(event)
        elif self.tool == 'rectangle':
            self.rectangle_motion(event)
    
    def end(self,event):
        if self.tool == 'pen':
            self.old_x, self.old_y = None, None
            self.stack.append(self.Pen_objects)
            self.Pen_objects = []
        elif self.tool == 'line':
            self.line_end(event)
        elif self.tool == 'circle':
            self.circle_end(event)
        elif self.tool == 'rectangle':
            self.rectangle_end(event)

    def mouse_right(self, event):
        if self.tool == "polygon":
            self.polygon_finish(event)


    def pen_draw(self, event):
        if self.old_x and self.old_y:
            self.Pen_objects.append(
                self.c.create_line(
                    self.old_x, self.old_y, event.x, event.y,
                    width=self.size, fill=self.paint_color,
                    capstyle=ROUND, smooth=TRUE, splinesteps=36
                    )
                )
        self.old_x = event.x
        self.old_y = event.y

    def line_start(self,event):
        self.size = self.choose_size_button.get()
        self.line_start_x=event.x
        self.line_start_y=event.y
    def line_motion(self,event):
        self.c.delete('temp_line_objects')
        self.c.create_line(self.line_start_x, self.line_start_y, event.x, event.y, 
                           width=self.size, fill=self.paint_color, smooth=1, tags='temp_line_objects')
    def line_end(self, event):
        self.c.delete('temp_line_objects')
        x = self.c.create_line(self.line_start_x, self.line_start_y, event.x, event.y, 
                               width=self.size, fill=self.paint_color, smooth=1)
        self.Line_objects.append(x)
        self.stack.append(x)
        return event.x, event.y

    def circle_start(self,event):
        self.circle_start_x = event.x
        self.circle_start_y = event.y
    def circle_motion(self,event):
        self.c.delete('temp_circle_objects')
        self.c.create_oval(self.circle_start_x, self.circle_start_y, event.x, event.y, 
                           fill=self.paint_color, outline=self.outline_color, tags='temp_circle_objects')
    def circle_end(self, event):
        self.c.delete('temp_circle_objects')
        x = self.c.create_oval(self.circle_start_x, self.circle_start_y, event.x, event.y, 
                               fill=self.paint_color, outline=self.outline_color)
        self.Circle_objects.append(x)
        self.stack.append(x)
    
    def rectangle_start(self,event):
        self.rectangle_start_x = event.x
        self.rectangle_start_y = event.y
    def rectangle_motion(self,event):
        self.c.delete('temp_rectangle_objects')
        self.c.create_rectangle(self.rectangle_start_x, self.rectangle_start_y, event.x, event.y, 
                           fill=self.paint_color, outline=self.outline_color, tags='temp_rectangle_objects')
    def rectangle_end(self, event):
        self.c.delete('temp_rectangle_objects')
        x = self.c.create_rectangle(self.rectangle_start_x, self.rectangle_start_y, event.x, event.y, 
                               fill=self.paint_color, outline=self.outline_color)
        self.Rectangle_objects.append(x)
        self.stack.append(x)
    
    def polygon_point(self, event):
        self.polygon_points.append(event.x)
        self.polygon_points.append(event.y)
        self.size = self.choose_size_button.get()
        self.polygon_temp.append(
            self.c.create_oval(event.x, event.y, event.x + self.size, event.y + self.size, 
                               fill=self.paint_color, outline=self.outline_color)
            )
    def polygon_finish(self, event):
        for point in self.polygon_temp:
            self.c.delete(point)
        x = self.c.create_polygon(*self.polygon_points, fill=self.paint_color, outline=self.outline_color)
        self.polygon_points = []
        self.Polygon_objects.append(x)
        self.stack.append(x)
    
    def point(self,event):
        self.size = self.choose_size_button.get()
        x = self.c.create_oval(event.x, event.y, event.x + self.size, event.y + self.size, 
                               fill=self.paint_color, outline=self.outline_color)
        self.Point_objects.append(x)
        self.stack.append(x)

    
    def import_img(self):
        img_dir = str(askopenfilename(
            initialdir = self.project_path,
            filetypes=(("Image file", "*.jpeg *.jpg *.png *.gif"), 
                       ("All files", "*.*"))
        ))
        if img_dir:
            resize_factor = askfloat(title="Resize factor", 
                prompt="Type the image resize factor:\n0 > factor < 1.0 (shrink)\nfactor = 1 (origin)\nfactor > 1.0 (enlarge)")
            
            try:
                img_temp = Img.open(img_dir)
                width, height = img_temp.size
                img_temp = img_temp.resize((int(width * resize_factor), int(height * resize_factor)), Img.ANTIALIAS)
                img_temp.convert("RGB").save("img_temp.ppm", format="ppm")
                
                self.img = PhotoImage(file="img_temp.ppm")
                x = self.c.create_image(self.DEFAULT_CANVAS_WIDTH // 2, self.DEFAULT_CANVAS_HEIGHT // 2, image=self.img)
                self.stack.append(x)
            except:
                showerror(title="Import error", message="Wrong image format!")
        
    def undo(self, event=None):
        if self.stack:
            x = self.stack.pop()
            if type(x) is list:
                for item in x:
                    self.c.delete(item)
            else:
                self.c.delete(x)
    
    def saving(self):
        if self.file_dir.endswith(".ps"):
                self.c.postscript(file = self.file_dir, colormode = 'color')
        elif self.file_dir.endswith(".png"):
            x2 = self.root.winfo_rootx() + self.c.winfo_x() + 2
            y2 = self.root.winfo_rooty() + self.c.winfo_y() + 2
            x1 = x2 + self.c.winfo_width() - 4
            y1 = y2 + self.c.winfo_height() - 4
            ImageGrab.grab().crop((x2,y2,x1,y1)).save(self.file_dir)
    
    def save(self, event):
        if self.file_dir:
            self.saving()
        else:
            self.save_as(event)
        
    def save_as(self, event=None):
        self.file_dir = str(asksaveasfilename(
            initialdir = self.project_path,
            defaultextension = ".ps", 
            filetypes=(("PostScript File", "*.ps"), 
                        ("PNG File", "*.png"))
        ))
        
        start_index = self.file_dir.rfind("/") + 1
        end_index = self.file_dir.rfind(".")
        file_name = self.file_dir[start_index:end_index]
        if file_name: 
            self.root.title(file_name + " - Tkinter Paint")
        
        self.saving()