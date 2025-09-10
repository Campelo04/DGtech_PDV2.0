from kivy.uix.screenmanager import Screen
from kivy.lang import Builder #Faz referencia ao arquivo .kv
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils  import get_color_from_hex as hex 
import time
Builder.load_file('screens/login/login.kv') #Carrega o arquivo .kv
URL = "http://127.0.0.1:8000/auth/login"

class MyBoxLogin(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class BtnLogin(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #-->> Possibilita modificar o alinhamento do texto no Objeto
        self.bind(size=self.setter('text_size')) 
        Window.bind(mouse_pos=self.on_mouseover)
        self.original = hex("#2A2666")
        self.color_original = hex("#DBDAEF")
    def on_mouseover(self, window, pos):
        if self.collide_point(*pos):
            self.background_color=hex("#CDDDFC")
            self.color=self.original
            self.bold=True
        else:
            self.background_color=self.original
            self.color=self.color_original
            self.bold=False
class InfoTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.bind(size=self.setter('text_size'))
        Window.bind(mouse_pos=self.on_mouseover)
        self.aux = self.height
    def on_mouseover(self, window, pos):
        if self.collide_point(*pos):
            self.height =35
            self.size_hint_x =1.01
        else:
            self.size_hint_y =None
            self.height =33
            self.size_hint_x =1

class InfoLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        Window.bind(mouse_pos=self.on_mouseover)
        self.original = hex("#2A2666")
        self.color_original = hex("#2A2666")
    def on_mouseover(self, window, pos):
        if self.collide_point(*pos):
            self.background_color=hex("#060426")
            self.color=self.original
            self.bold=True
        else:
            self.background_color=self.original
            self.color=self.color_original
            self.bold=False


class Login(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        
    def entrar(self, user =str, password=str):
        self.user = user
        self.password = password
        try: 
            response = requests.post(URL,
                          data={"username": self.user, 
                                "password": self.password},
                                timeout=10)
            print("Status da resposta: ",response.status_code,"\nResposta", response.json())
            data = response.json()  # {"access_token": "...", "token_type": "bearer"}
            self.token = data["access_token"]
            #Guarda o token no cabeçalho das próximas requisições

            self.headers = {"Authorization": f"Bearer {self.token}"}
            #self.session.headers.update({"Authorization": f"Bearer {self.token}"})


            #self.ids.login_mensage.text = response.json()["detail"]
            if response.status_code == 200:
                print("\n \n PÁGINA ATUAL: ",self.manager.current)
                pedidos = self.manager.get_screen('pedidos')
                pedidos.headers = self.headers 
                self.manager.current = "pedidos"
                try:
                    self.ids.login_mensage.text = response.json()["detail"]
                except:
                    self.ids.login_mensage.text = "a mensagem falhou"
        except:
            self.ids.login_mensage.text = "Falha de conexão."
            print(f"Falha na execussão! \nUsuário: {self.user} \nSenha: {self.password} verifique suas informações de login e tente novamnete.")
    def enviar_para_pedidos(self):
        login = self.manager.get_screen('login')
        login.b = self.a              # <-- passa o valor
        self.manager.current = 'screen_b'
    
        