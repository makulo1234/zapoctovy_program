from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.simpledialog import askfloat
from tkinter.messagebox import showinfo, showerror, askyesnocancel
from tkinter.font import Font
import pathlib
from PIL import Image as Img
import pyscreenshot as ImageGrab

class Paint(object):
    """
    Paint App driven by Tkinter for drawing lines, ellipses, rectangles, polygons and points with basic settings adjustments.
    
    Attributes
    ----------
    default_canvas_width : int
        the width of the drawing area (600 by default)
    default_canvas_height : int
        the width of the drawing area (600 by default)
    default_color : string
        the default color used at the start of the application ("black" by default)
    default_pen_size : int
        the default pen (tool outline) size used at the start of the application (5 by default)
    """

    # Default values for Paint app that can be changed
    DEFAULT_PEN_SIZE = 5
    DEFAULT_COLOR = 'black'
    DEFAULT_CANVAS_WIDTH = 600
    DEFAULT_CANVAS_HEIGHT = 600
    
    def __init__(self, default_canvas_width=DEFAULT_CANVAS_WIDTH, default_canvas_height=DEFAULT_CANVAS_HEIGHT, 
                 default_color=DEFAULT_COLOR, default_pen_size=DEFAULT_PEN_SIZE):
        
        self.default_canvas_width = default_canvas_width
        self.default_canvas_height = default_canvas_height
        self.default_color = default_color
        self.default_pen_size = default_pen_size
        
        self.root = Tk()
        
        # Top GUI menubar that consists of menu1, menu2 and menu3
        self.menubar = Menu(self.root)
        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="New file", command=self.new_file)
        self.menu1.add_command(label="Save (Ctrl+S)", command=self.save)
        self.menu1.add_command(label="Save as... (Ctrl+A)", command=self.save_as)
        self.menubar.add_cascade(label="File", menu=self.menu1)
        
        self.menu2 = Menu(self.menubar, tearoff=0)
        self.menu2.add_command(label="Undo (Ctrl+Z)", command=self.undo)
        self.menu2.add_command(label="Redo (Ctrl+Y)", command=self.redo)
        self.menubar.add_cascade(label="Edit", menu=self.menu2)
        
        self.menu3 = Menu(self.menubar, tearoff=0)
        self.menu3.add_command(label="Import image", command=self.import_img)
        self.menubar.add_cascade(label="Import", menu=self.menu3)
        
        self.root.config(menu=self.menubar)

        # 1. row in Tk grid layout
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
        
        # 2. row in Tk grid layout
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
        
        self.text_button = Button(self.root, text='Text', command=self.use_text)
        self.text_button.grid(row=1,column=6)

        # Canvas implementation with default dimensions
        self.c = Canvas(self.root, bg='white', width=self.default_canvas_width, height=self.default_canvas_height)
        self.c.grid(row=2, columnspan=7)

        # Tk GUI setup and mainloop to run the Tcl window in a loop
        self.setup()
        self.root.mainloop()

    # Variable definitions used in the program and default settings 
    def setup(self):
        # Window setup and project_path definition using pathlib library
        self.root.title("New file - Tkinter Paint")
        self.project_path = pathlib.Path(__file__).parent.absolute()
        
        # Main variables, counters and default settings
        self.old_x = None
        self.old_y = None
        self.size = self.default_pen_size
        self.choose_size_button.set(self.default_pen_size)
        self.paint_color = self.default_color
        self.current_color.config(bg=self.paint_color)
        self.eraser_on = False
        self.active_button = self.pen_button
        self.use_pen()
        # self.changes_index = 0
        self.index = 0
        self.img_counter = 0
        self.file_dir = ""
        
        # Stacks/lists used in tool functions
        self.Pen_objects = []
        self.Line_objects = []
        self.Circle_objects = []
        self.Rectangle_objects = []
        self.Polygon_objects = []
        self.Point_objects = []
        self.Image_objects = []
        self.polygon_points = []
        self.polygon_temp = []
        # self.changes = []
        self.stack = []
        
        # Basic key/mouse binds
        self.c.bind('<Button-1>', self.start)
        self.c.bind('<B1-Motion>', self.motion)
        self.c.bind('<ButtonRelease-1>', self.end)
        self.c.bind("<Button-3>", self.mouse_right)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        self.root.bind("<Control-s>", self.save)
        self.root.bind("<Control-a>", self.save_as)

    # Function that sets tool settings triggered by button click
    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode
        self.paint_color = self.outline_color = 'white' if self.eraser_on else self.paint_color

    # Sets fill color option to white
    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
        self.current_color.config(bg="white")
    
    # Chooses fill color option to be used by tools
    def choose_color(self):
        self.eraser_on = False
        self.paint_color = self.outline_color = askcolor(color=self.paint_color)[1]
        self.current_color.config(bg=self.paint_color)

    # Resets the canvas by drawing a white rectangle over it
    def clear(self):
        x = self.c.create_rectangle(0, 0, self.default_canvas_width, self.default_canvas_height, fill="white", outline="white")
        self.stack.append(x)
        self.index = len(self.stack) - 1
    
# Functions triggered by their respective buttons
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
    # Function uses showinfo function to inform user how to use the tool
    def use_polygon(self):
        showinfo(title="Polygon tutorial", message="Left-click to create polygon points and then right-click to create polygon.")
        self.tool = "polygon"
        self.activate_button(self.polygon_button)
    def use_point(self):
        self.tool = "point"
        self.activate_button(self.point_button)
    def use_text(self):
        self.tool = "text"
        self.activate_button(self.text_button)
            
    # Start function triggered by mouse left button click that checks the current tool setting and triggers their respective functions
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
            self.index = len(self.stack) - 1
        elif self.tool == "text":
            self.text_start(event)
    
    # Motion function triggered by holding mouse left button that checks the current tool setting and triggers their respective functions
    # Only available to certain tools that use the motion effect
    def motion(self,event):
        if self.tool == "pen":
            self.pen_draw(event)
        elif self.tool == 'line':
            self.line_motion(event)
        elif self.tool == 'circle':
            self.circle_motion(event)
        elif self.tool == 'rectangle':
            self.rectangle_motion(event)
        elif self.tool == 'text':
            self.text_motion(event)
    
    # End function triggered by releasing mouse left button that checks the current tool setting and triggers their respective functions
    def end(self,event):
        if self.tool == 'pen':
            self.old_x, self.old_y = None, None
            self.stack.append(self.Pen_objects)
            self.Pen_objects = []
            self.index = len(self.stack) - 1
        elif self.tool == 'line':
            self.line_end(event)
            self.index = len(self.stack) - 1
        elif self.tool == 'circle':
            self.circle_end(event)
            self.index = len(self.stack) - 1
        elif self.tool == 'rectangle':
            self.rectangle_end(event)
            self.index = len(self.stack) - 1
        elif self.tool == 'text':
            self.text_end(event)

    # Only available to Polygon function to trigger the creation of polygon
    def mouse_right(self, event):
        if self.tool == "polygon":
            self.polygon_finish(event)
            self.index = len(self.stack) - 1
        if self.tool == "text":
            if not self.text_created:
                self.text_counter = False
                self.text_finish(event)
                self.index = len(self.stack) - 1

    # Motion function for pen tool
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

    # Line tool start, motion and end effect
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

    # Circle tool start, motion and end effect
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
    
    # Rectangle tool start, motion and end effect
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
    
    # Polygon points used to define the polygon corners
    def polygon_point(self, event):
        self.polygon_points.append(event.x)
        self.polygon_points.append(event.y)
        self.size = self.choose_size_button.get()
        self.polygon_temp.append(
            self.c.create_oval(event.x, event.y, event.x + self.size, event.y + self.size, 
                               fill=self.paint_color, outline=self.outline_color)
            )
    # Polygon draw function to create polygon from Polygon points
    def polygon_finish(self, event):
        for point in self.polygon_temp:
            self.c.delete(point)
        if self.polygon_points:
            x = self.c.create_polygon(*self.polygon_points, fill=self.paint_color, outline=self.outline_color)
            self.polygon_points = []
            self.Polygon_objects.append(x)
            self.stack.append(x)
    
    # Point tool to draw small circles that represent points
    def point(self, event):
        self.size = self.choose_size_button.get()
        x = self.c.create_oval(event.x, event.y, event.x + self.size, event.y + self.size, 
                               fill=self.paint_color, outline=self.outline_color)
        self.Point_objects.append(x)
        self.stack.append(x)
        
    def text_start(self, event):
        self.text_created = False
        self.text_start_x = event.x
        self.text_start_y = event.y
        self.text_rel_x = 0
        self.text_rel_y = 0
        # print(Font(font="Courier").metrics()) #-> Arial, size: 12
    def text_motion(self, event):
        self.text_rel_x = event.x - self.text_start_x
        self.text_rel_y = event.y - self.text_start_y
        char_width = 7.2006
        char_height = 22
        if self.text_rel_x > 0 and self.text_rel_y > 0:
            char_count_row = int(self.text_rel_x // char_width)
            count_lines = int(self.text_rel_y // char_height)
            
            self.c.delete('temp_text_objects')
            self.text_widget = Text(self.c, width=char_count_row, height=count_lines, bd=1, 
                                    fg=self.paint_color, font="Courier", highlightthickness=0,
                                    wrap=WORD)
            self.c.create_window(self.text_start_x, self.text_start_y, anchor=NW, window=self.text_widget, tags='temp_text_objects')
    def text_end(self, event):
        self.c.delete('temp_text_objects')
        self.text_window = self.c.create_window(self.text_start_x, self.text_start_y, anchor=NW, window=self.text_widget)
    def text_finish(self, event):
        self.text_widget.config(state="disabled")
        self.stack.append(self.text_window)

    # Image import function
    def import_img(self):
        # The user is asked to provide location for the import file
        img_dir = str(askopenfilename(
            initialdir = self.project_path,
            filetypes=(("Image file", "*.jpeg *.jpg *.png *.gif"), 
                       ("All files", "*.*"))
        ))
        # If the user selected some file
        if img_dir:
            # The user is asked for the resize factor, that is used to resize the image
            resize_factor = askfloat(title="Resize factor", 
                prompt="Type the image resize factor:\n0 > factor < 1.0 (shrink)\nfactor = 1 (origin)\nfactor > 1.0 (enlarge)")
            
            # The program tries to open the file selected by the user
            # If the file is not a file that can be opened as an image or cannot be converted using PIL library,
            # the program raises an exception and shows error dialog window
            try:
                img_temp = Img.open(img_dir)
                width, height = img_temp.size
                # The original image is resized using the resize factor
                img_temp = img_temp.resize((int(width * resize_factor), int(height * resize_factor)), Img.ANTIALIAS)
                # The image in any supported format (png, jpg, gif, ...) is converted into .ppm format that is supported by Tkinter
                img_temp.convert("RGB").save("temp/img_temp.ppm", format="ppm")
                
                # Image_objects list is used to store PhotoImage objects, that represent images in memory, that are used later in
                # undo, redo functions
                self.Image_objects.append(PhotoImage(file="temp/img_temp.ppm"))
                # The image is drawn on the canvas in the middle
                x = self.c.create_image(self.default_canvas_width // 2, self.default_canvas_height // 2, 
                                        image=self.Image_objects[self.img_counter])
                self.img_counter += 1
                self.stack.append(x)
                self.index = len(self.stack) - 1
            except:
                showerror(title="Import error", message="Wrong image format!")
    
    # Undo function triggered by key bind and menu button click
    def undo(self, event=None):
        # The function checks if the current index is greater or equal to 0 (index of ids defined in self.stack)
        if self.index >= 0:
            x = self.stack[self.index]
            # if type(x) is list:
            #     for item in x:
            #         if self.c.itemcget(item, "state") == "hidden":
            #             self.c.itemconfigure(item, state="normal")
            #         else:
            #             self.c.itemconfigure(item, state="hidden")
            # else:
            #     if self.c.itemcget(x, "state") == "hidden":
            #         self.c.itemconfigure(x, state="normal")
            #     else:
            #         self.c.itemconfigure(x, state="hidden")
            
            # If the current item in self.stack is a list (pen objects), then it hides all it's items, if not, then it hides the item
            # specified by id in self.stack
            if type(x) is list:
                for item in x:
                    self.c.itemconfigure(item, state="hidden")
            else:
                self.c.itemconfigure(x, state="hidden")
            # the self.index is lowered by 1 to indicate the current working item id in self.stack
            self.index -= 1
    
    # Redo function triggered by key bind and menu button click similar to Undo function
    def redo(self, event=None):
        # The function checks if the current index is lower than the last index in self.stack
        if self.index < (len(self.stack) - 1):
            self.index += 1
            x = self.stack[self.index]
            # if type(x) is list:
            #     for item in x:
            #         if self.c.itemcget(item, "state") == "hidden":
            #             self.c.itemconfigure(item, state="normal")
            #         else:
            #             self.c.itemconfigure(item, state="hidden")
            # else:
            #     if self.c.itemcget(x, "state") == "hidden":
            #         self.c.itemconfigure(x, state="normal")
            #     else:
            #         self.c.itemconfigure(x, state="hidden")
            if type(x) is list:
                for item in x:
                    self.c.itemconfigure(item, state="normal")
            else:
                self.c.itemconfigure(x, state="normal")
                    
    # Function starts a new file, sets currently active button to RAISED, resets canvas and resets all settings
    def new_file(self):
        answer = askyesnocancel("Save file?", "Do you want to save the file before proceeding?")
        if answer == True:
            self.save()
            self.active_button.config(relief=RAISED)
            self.c.delete("all")
            self.setup()
        elif answer == False:
            self.active_button.config(relief=RAISED)
            self.c.delete("all")
            self.setup()
    
    # Supporting saving function used in save() and save_as()
    def saving(self):
        # If the chosen export file format is Postscript (.ps), than it uses Tkinter built-in function
        if self.file_dir.endswith(".ps"):
                self.c.postscript(file = self.file_dir, colormode = 'color')
        # If the chosen export file format is PNG, than it creates a screenshot of the screen and crops the image using
        # coordinates of the canvas upper left and down right corners
        elif self.file_dir.endswith(".png"):
            # winfo_rootx() and winfo_rooty() is root's upper left corner coords + winfo_x() and winfo_y() is 
            # canvase's upper left corner coords relative to root (0)
            x2 = self.root.winfo_rootx() + self.c.winfo_x() + 2 # +2 is needed to compensate for root's window padding
            y2 = self.root.winfo_rooty() + self.c.winfo_y() + 2
            x1 = x2 + self.c.winfo_width() - 4 # -4 is needed to compensate for winfo_width/height() return value being incremented by 4
            y1 = y2 + self.c.winfo_height() - 4
            ImageGrab.grab().crop((x2,y2,x1,y1)).save(self.file_dir)
    
    # Save function that triggers saving() if the export file_dir is already chosen, if not, triggers save_as()
    def save(self, event=None):
        if self.file_dir:
            self.saving()
        else:
            self.save_as()
    
    # Function triggers the standard save dialog, asks the location of export file and sets the root window's title
    # to export file name
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