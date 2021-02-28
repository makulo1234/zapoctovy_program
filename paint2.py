from tkinter import *

class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'
    SCREEN_W=800
    SCREEN_H=800


    def __init__(self):    
        self.master = Tk()    

        self.line_button = Button(self.master, text='Line',command=self.set_tool_line)
        self.line_button.grid(row=0,column=0)

        self.circle_button = Button(self.master, text='Circle',command= self.set_tool_circle)
        self.circle_button.grid(row=0,column=1)

        self.point_button = Button(self.master, text='Point',command = self.set_tool_point)
        self.point_button.grid(row=0,column=2)

        self.draw_zone = Canvas(self.master,height=600,width=600,bg='white')
        self.draw_zone.grid(row=1,columnspan=5)

        self.menubar = Menu(self.master)
        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="Nouveau", command=self.alert)
        self.menu1.add_command(label="Ouvrir", command=self.alert)
        self.menu1.add_separator()
        self.menu1.add_command(label="Quitter", command=self.master.destroy)
        self.menubar.add_cascade(label="Fichier", menu=self.menu1)
        self.menu2 = Menu(self.menubar, tearoff=0)
        self.menu2.add_command(label="Undo", command=self.undo )

        self.menu2.add_command(label="Redo", command=self.alert)
        self.menubar.add_cascade(label="Editer", menu=self.menu2)

        self.master.config(menu=self.menubar)
        self.master.title('UI')

        self.setup()
        self.master.mainloop()    

    def setup(self):
        self.line_start_x = None
        self.line_start_y = None

        self.circle_start_x = None
        self.circle_start_y = None

        self.tool_option = 'line'

        self.Line_objects = []
        self.Circle_objects = []
        self.Point_objects = []
        self.stack = []    

        self.draw_zone.bind('<Button-1>', self.draw_start)
        self.draw_zone.bind('<B1-Motion>',self.draw_motion)
        self.draw_zone.bind('<ButtonRelease-1>',self.draw_end)


    def line_start(self,event):
        self.line_start_x=event.x
        self.line_start_y=event.y
    def line_motion(self,event):
        self.draw_zone.delete('temp_line_objects')
        self.draw_zone.create_line(self.line_start_x,self.line_start_y,event.x,event.y,fill=self.DEFAULT_COLOR,smooth=1,tags='temp_line_objects')
    def line_end(self,event):
        x=self.draw_zone.create_line(self.line_start_x,self.line_start_y,event.x,event.y,fill=self.DEFAULT_COLOR,smooth=1)
        self.Line_objects.append(x)
        self.stack.append(x)

    def circle_start(self,event):
        self.circle_start_x = event.x
        self.circle_start_y = event.y
    def circle_motion(self,event):
        self.draw_zone.delete('temp_circle_objects')   #sym de circle_end par rapport a circle_start
        #self.draw_zone.create_oval(event.x,event.y,(2*self.circle_start_x-event.x),(2*self.circle_start_y-event.y),tags='temp_circle_objects')
        self.draw_zone.create_oval((self.circle_start_x),(self.circle_start_y),event.x,event.y,fill=self.DEFAULT_COLOR,tags='temp_circle_objects')
    def circle_end(self,event):
        #x=self.draw_zone.create_oval(event.x,event.y,(2*self.circle_start_x-event.x),(2*self.circle_start_y-event.y))
        x=self.draw_zone.create_oval((self.circle_start_x),(self.circle_start_y),event.x,event.y,fill=self.DEFAULT_COLOR)
        self.Circle_objects.append(x)
        self.stack.append(x)

    def point_start(self,event):
        x = self.draw_zone.create_line(event.x,event.y,event.x+1,event.y+1)
        self.Point_objects.append(x)

    def set_tool_line(self):
        self.tool_option = 'line'
    def set_tool_circle(self):
        self.tool_option = 'circle'
    def set_tool_point(self):
        self.tool_option = 'point'

    def draw_start(self,event):
        if self.tool_option=='line':
            self.line_start(event)
        elif self.tool_option == 'circle':
            self.circle_start(event)
        elif self.tool_option=='point':
            self.point_start(event)

    def draw_motion(self,event):
        if self.tool_option=='line':
            self.line_motion(event)
        elif self.tool_option == 'circle':
            self.circle_motion(event)
    def draw_end(self,event):
        if self.tool_option=='line':
            self.line_end(event)
        elif self.tool_option == 'circle':
            self.circle_end(event)

    def undo(self):
        x = self.stack.pop()
        self.draw_zone.delete(x)        

    def alert(self):
        print('yo')

if __name__ == '__main__':
    ge = Paint()