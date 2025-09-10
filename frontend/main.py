from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager 
from screens.login.login import Login
from screens.pedidos.pedidos import Pedidos
from kivy import Config
from pynput.keyboard import Key, Controller
keyboard = Controller()
Config.set('input', 'mouse', 'mouse,disable_multitouch') #quando se usa o botão auxiliar do mouse surge uma bolinha vermelha a cada click, está linha desabilita isso
Config.set('kivy','exit_on_escape','0') #Desabilita o fechamento do programda pela tecla "ESC"

class MyBL(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Master(ScreenManager):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

class Main(App):
    def build(self):
        # IMPORTANTE: retornar **uma instância**, não a classe
        Master = MyBL()
        with keyboard.pressed(Key.cmd_l):
            keyboard.press(Key.left)
        keyboard.release(Key.esc)
        return Master

if __name__ == "__main__":
    Main().run()
