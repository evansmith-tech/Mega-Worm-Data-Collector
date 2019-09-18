import time
from pprint import pprint
from tkinter import *
master = Tk()

w = Canvas(master, width=1000, height=500)


	#w.create_text(((x * 100) + 55, 55), text="1", fill="white")
rectangleArray = [[],[]]

def createRectangleArray(rows, cols):
	for x in range(0,9):
		rectangleArray[0].append(w.create_rectangle(x * 100 + 10, 10, x * 100 + 100, 110, fill="black"))
		rectangleArray[1].append(w.create_rectangle(x * 100 + 10, 130, x * 100 + 100, 230, fill="black"))


def cycleColor():
	pass
	# for x in range(0,9):
	# 	#w.itemconfig(rectangleArray[0][x], fill='black')
	# 	#time.sleep(1)
	# 	w.after(1000, w.itemconfig(rectangleArray[0][x], fill='red'))
	# 	#time.sleep(1)
	# 	#w.pack()

createRectangleArray(2, 12)

#w.after(1000,cycleColor())
#cycleColor()


w.after(1000, w.itemconfig(rectangleArray[0][1], fill='red'))
# w.after(1000, w.itemconfig(rectangleArray[0][2], fill='red'))
# w.after(1000, w.itemconfig(rectangleArray[0][3], fill='red'))
# w.after(1000, w.itemconfig(rectangleArray[0][4], fill='red'))


#pprint(rectangleArray)

#pprint(type(rectangleArray[0]))



#w.create_rectangle(0, 0, 100, 100, fill="black", outline = 'black')
#w.create_rectangle(110, 0, 210, 100, fill="blue", outline = 'blue')
#w.create_rectangle(50, 50, 100, 100, fill="red", outcline = 'blue') 
w.pack()
master.mainloop()
