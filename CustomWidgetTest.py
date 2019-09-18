from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty

class RootWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.add_widget(Button(text="btn1"))
        self.add_widget(Button(text="btn2"))
        self.add_widget(CustomBtn())

        

class CustomBtn(Widget):

    pressed = ListProperty([0,0])

    def on_touch_down(self, touch):
        self.pressed = touch.pos
        return False

    def on_pressed(self, instance, value):
        print("[CustomBtn] touch down at ", value)

class Demo(App):

    def build(self):
        return RootWidget()


if __name__ == '__main__':
    Demo().run()