from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.properties import ListProperty


import threading
import time

class Setup(FloatLayout):
	def __init__(self):
		super(Setup, self).__init__()

		Window.size = (800, 480)
		self.size = Window.size

		self.deviceArray = Widget(size=(100,100))
		self.add_widget(self.deviceArray)

		self.setNodeProperties()
		self.populateNodes(self.nodeSize)

		#self.add_widget(CustomBtn())

	def createNode(self, xpos, ypos):
		button = Button(text='', pos=(xpos, ypos), size_hint = (.125,.20833))
		#button.bind(on_press=self.highlightNode)
		return button
		#return Line(rounded_rectangle=(xpos, ypos, 100, 100, 10))

	def highlightNode(self):
		pass

	def populateNodes(self, size):
		with self.deviceArray.canvas:
			for rowNum in range(0,size[0]):
				for colNum in range(0, size[1]):
					currentNode = rowNum * size[1] + colNum
					if currentNode == self.activeNode:
						Color(1,0,0,1)
						#self.recordingProgressBar.value = (currentNode / self.nodeCount) * 1000
					else:
						Color(1,1,1,1)
					self.deviceArrayList.append(self.createNode(colNum * 100 + colNum * 10 + 10, Window.size[1] - (rowNum + 1) * 110))

	def setNodeProperties(self):
		self.nodeSize = (2, 7)
		self.activeNode = 0
		self.nodeCount = self.getNodeCount()
		self.deviceArrayList = []

	def getNodeCount(self):
		return self.nodeSize[0] * self.nodeSize[1]

class CustomBtn(Widget):

    pressed = ListProperty([0,0])

    def on_touch_down(self, touch):
        self.pressed = touch.pos
        return False

    def on_pressed(self, instance, value):
        print("[CustomBtn] touch down at ", value)
	
class SetupInterface(App):
    def build(self):
        return Setup()

if __name__ == '__main__':
     SetupInterface().run()