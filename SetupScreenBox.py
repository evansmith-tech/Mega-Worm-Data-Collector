from kivy.base import runTouchApp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.vector import Vector
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.config import Config

import json
import os
import sys

#Window.borderless = True
#Window.size = (600, 360)


# Builder.load_string('''
# <CircularButton>
#     background_color: 0.5,.5,.5,.5
#     canvas.before:
#         Color:
#             rgba: self.background_color
#         Ellipse:
#             pos: self.pos
#             size: self.size
#     ''')

Builder.load_string('''
<Node>
    background_color: 1,1,1,1
    canvas:
        Color:
            rgba: self.background_color
        Line:
            rounded_rectangle: (self.x+17, self.y+5, 45, 45, 10)

    ''')

class NodeArray(GridLayout):
	def __init__(self):
		super(NodeArray, self).__init__()
		#Window.maximize = True
		#Window.borderless = True
		self.padding = 10
		self.cols = 9
		self.rows = 8
		self.intialChar = 'F'
		self.initialNum = 1 #self.rows - 1
		self.nodeList = []
		self.binaryMatrix = [0 for x in range((self.cols - 1) * (self.rows - 1))]
		self.populateGrid()
		self.addButtons()

	def populateGrid(self):
		for x in range(0, self.rows * self.cols):
			if self.checkLastRow(x, self.rows, self.cols):
				pass
			elif self.checkSecondToLastRow(x, self.rows, self.cols):
				if x == (self.rows * self.cols - self.cols):
					self.add_widget(Label(text=''))
				else:
					self.add_widget(Label(text=str(self.initialNum), font_size = '20sp'))
					self.initialNum = self.initialNum + 1
					#self.add_widget(Label(text=self.intialChar, font_size = '20sp'))
					#self.intialChar = chr(ord(self.intialChar) + 1)
			else:
				if x % 9 == 0:
					if x == (self.rows - 1) * self.cols:
						pass
						#self.addApplyButton()
					else:
						#self.add_widget(Label(text=str(self.initialNum), font_size = '20sp'))
						if self.intialChar == '@':
							self.add_widget(Label(text=' ', font_size = '20sp'))
						else:
							self.add_widget(Label(text=self.intialChar, font_size = '20sp'))
					#self.initialNum = self.initialNum - 1
					self.intialChar = chr(ord(self.intialChar) - 1)
				else:
					self.createNode()

	def createNode(self):
		node = Node()
		self.nodeList.append(node)
		self.add_widget(node)
	
	def addButtons(self):
		self.addApplyButton()
		self.add_widget(Label(text=''))
		self.addUsePreviousButton()
		self.add_widget(Label(text=''))
		self.addSelectAllButton()
		self.add_widget(Label(text=''))
		self.addDeselectAllButton()
		self.add_widget(Label(text=''))
		self.addCloseButton()

	def checkLastRow(self, index, rows, cols):
		if index > (rows * cols - cols):
			return True

	def checkSecondToLastRow(self, index, rows, cols):
		if (index > (rows * cols - 2*cols)) and (index < (rows * cols - cols)):
			return True

	def addApplyButton(self):
		self.applyButton = Button(text='Apply')
		self.applyButton.bind(on_press=self.exportNodeConfiguration)
		self.add_widget(self.applyButton)

	def addUsePreviousButton(self):
		self.usePreviousButton = Button(text='    Use\nPrevious')
		self.usePreviousButton.bind(on_press=self.exportNodeConfiguration)
		self.add_widget(self.usePreviousButton)
	
	def addSelectAllButton(self):
		self.selectAllButton = Button(text='Select\n   All')
		self.selectAllButton.bind(on_press=self.selectAllNodes)
		self.add_widget(self.selectAllButton)

	def addDeselectAllButton(self):
		self.deselectAllButton = Button(text='Deselect\n     All')
		self.deselectAllButton.bind(on_press=self.deselectAllNodes)
		self.add_widget(self.deselectAllButton)
	
	def addCloseButton(self):
		self.closeButton = Button(text='Close')
		self.closeButton.bind(on_press=self.closeSetupScreen)
		self.add_widget(self.closeButton)

	def createBinaryMatrix(self):
		for index, node in enumerate(self.nodeList):
			self.binaryMatrix[index] = int(node.activated)
		self.binaryMatrix.reverse()
		#print(self.binaryMatrix)
		self.binaryMatrix = [self.binaryMatrix[i:i + 8] for i in range(0, len(self.binaryMatrix), 8)]
		self.correct = []
		for row in self.binaryMatrix:
			row.reverse()
			self.correct.append(row)
		self.binaryMatrix = [item for sublist in self.correct for item in sublist]

	def createConfigDictionary(self):
		self.configDict = {'rows':self.rows, 'cols':self.cols, 'data':self.binaryMatrix}

	def outputJSON(self):
		with open('nodeInfo.dat', 'w') as file:
			json.dump(self.configDict, file)

	def selectAllNodes(self):
		pass

	def deselectAllNodes(self):
		pass

	def usePreviousConfiguration(self):
		pass
	
	def closeSetupScreen(self):
		pass

	def exportNodeConfiguration(self, instance):
		self.createBinaryMatrix()
		self.createConfigDictionary()
		self.outputJSON()
		os.system('python3 HomeScreen.py')
		sys.exit()


class Node(ButtonBehavior, Label):
	def __init__(self, **kwargs):
		super(Node, self).__init__(**kwargs)
		self.activated = False

	def on_press(self, *args):
		self.activated = not self.activated
		if not self.activated:
			self.background_color = (1, 1, 1, 1)
		else:
			self.background_color = (1, 0, 0, 1)

	def collide_point(self, x, y):
		return Vector(x, y).distance((self.x + 30, self.y + 30)) <= 30

if __name__ == '__main__':
	#Config.set('graphics', 'fullscreen', 0)
	Config.set('graphics', 'window_state', 'maximized')
	Config.write()
	runTouchApp(NodeArray())