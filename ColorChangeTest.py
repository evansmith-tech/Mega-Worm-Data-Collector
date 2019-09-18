from tkinter import *

def change_color():
    canvas.itemconfig(light_1, fill='blue')

root = Tk()
canvas = Canvas(root)
light_1 = canvas.create_oval(0,100,100,100, fill='green')
root.after(1000, change_color) # 'after' uses milliseconds, so 1,000 = 1 second
root.mainloop()