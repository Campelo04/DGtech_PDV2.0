from kivy.lang import Builder #Faz referencia ao arquivo .kv 
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner,SpinnerOption
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput 
from kivy.utils  import get_color_from_hex as hex 
import requests
from typing import List, Optional
from datetime import datetime
from pydantic import Field
from kivy.uix.popup import Popup
API_URL = "http://127.0.0.1:8000/clientes/"

Builder.load_file("screens/pedidos/pedidos.kv") #Carrega o arquivo .kv

class MyPopUp_Alerta(Popup):
    def __init__(self,text,**kwargs) -> None:
        self.text =text
        super().__init__(**kwargs)
    
class Pedido():
    def __init__(self, id, codigo, id_cliente, id_funcionario, endereco, origem, itens, formas_pagamento, valor_total, abertura="", fechamento="", estado="", obs="", **kwargs):
        self.id = id
        self.codigo = codigo 
        self.id_cliente = id_cliente 
        self.id_funcionario = id_funcionario
        self.emdereco = endereco
        self.origem = origem
        self.itens = itens
        self.formas_pagamento =formas_pagamento
        self.valor_total = valor_total 
        self.abertura = abertura
        self.fechamento = fechamento
        self.estado = estado
        self.obs = obs
class Produto():
    def __init__(self, id, codigo, categoria, nome, valor, descr="", **kwargs):
        self.id = id 
        self.codigo = codigo
        self.categoria = categoria
        self.nome = nome
        self.valor = valor
        self.descr = descr

class Btn(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #-->> Possibilita modificar o alinhamento do texto no Objeto
        self.bind(size=self.setter('text_size')) 
        Window.bind(mouse_pos=self.on_mouseover)
        self.original = .35,0,0
        self.color_original = 1,1,1
    def on_mouseover(self, window, pos):
        if self.collide_point(*pos):
            self.background_color=hex("#4982F3")
            self.color=self.original
            self.bold=True
        else:
            self.background_color=self.original
            self.color=self.color_original
            self.bold=False
class Btn_Categoria(Button,BoxLayout):
    def __init__(self, categoria, **kwargs):
        self.categoria = categoria
        self.bind(size=self.setter('text_size')) 
        super().__init__(**kwargs)

class InfoTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)        

class Btn_Item(Button,BoxLayout): #,
    def __init__(self, categoria, id, nome, valor,**kwargs):
        self.categoria = categoria
        self.id = id
        self.nome = nome
        self.valor = valor
        super().__init__(**kwargs)
        #-->> Possibilita modificar o alinhamento do texto no Objeto
        self.bind(size=self.setter('text_size')) 
        self.color = 0,0,0
    def printar_id(self, id):
        self.id = id
        print(f"Aqui o ID, doido! {self.id}")
    def editar_pedido(self, pedido_id, codigo, id_cliente, id_funcionario, itens, origem, valor, obs):
        API_URL = "http://127.0.0.1:8000/pedidos/"
        try:    
            response = requests.put(f"{API_URL}{pedido_id}", json={"codigo":codigo, "id_cliente": id_cliente, "id_funcionario":id_funcionario, "itens":itens, "origem":origem, "valor":valor, "obs":obs})
        except:
            return "Falha na cominicação.\nVerifique o seu funcionamento da API."
        return response.json()
    
   
class Pedido_aberto(BoxLayout):
    def __init__(self, id, headers,**kwargs):
        self.headers = headers
        self.id = id
        API_URL = "http://127.0.0.1:8000/pedidos/"
        print("#  ENTROU NO CARREGAMENTO DE PEDIDOS")
        try:
            print("#  ENTROU NO 'TRY' CARREGAMENTO DE PEDIDOS")
            response = requests.get(f"{API_URL}{self.id}",headers=self.headers)
        except:
            return "Falha na cominicação.\nVerifique o seu funcionamento da API."
        for i in response.json():
            p = Pedido(**response.json())
            print("# PEDIDOS AQUI")
            #for j in vars(p):
            #    print(j)
            self.codigo = p.codigo
            self.id_cliente = p.id_cliente
            self.id_funcionario = p.id_funcionario
            self.itens = p.itens
            self.formas_pagamento = p.formas_pagamento
            self.origem = p.origem
            self.valor_total = p.valor_total
            self.abertura = p.abertura
            self.fechamento = p.fechamento
            self.estado = p.estado
            self.obs = p.obs
        super().__init__(**kwargs)
        for i in self.itens:
            self.ids.itens_pedido.add_widget(ItemPedido(i))

class Btn_Pedido(Button,BoxLayout):
    def __init__(self, id, codigo, id_cliente, id_funcionario, itens, origem, valor, abertura, fechamento, estado, obs, **kwargs):
        self.id = id
        self.codigo = codigo 
        self.id_cliente = id_cliente 
        self.id_funcionario = id_funcionario
        self.itens = itens
        self.origem = origem
        self.valor = valor 
        self.abertura = abertura
        self.fechamento = fechamento
        self.estado = estado
        self.obs = obs
        super().__init__(**kwargs)
        #-->> Possibilita modificar o alinhamento do texto no Objeto
        self.bind(size=self.setter('text_size')) 
        self.color = 0,0,0
    def minha_cor(self,estado):
        match estado:
            case "Finalizado":
                return "#10ff10"
            case "Entregue/servido":
                return "#00BFFF"
            case "Em produção":
                return "#FF8C00"
            case _:
                return "#d5d5d5"
      

    def printar_id(self, id):
        self.id = id
        print(f"Aqui o ID, doido! {self.id}")
    def obter_pedido(self,pedido_id=""):
        print(f"\n\nID DO PEDIDO AQUI, MISÉEEERA! {pedido_id} \n\n")
        API_URL = "http://127.0.0.1:8000/pedidos/"
        try:
            print("BATEU NO TRY DE OBTENÇÃO")
            response = requests.get(f"{API_URL}{pedido_id}")
        except:
            return "Falha na comunicação.\nVerifique o seu funcionamento da API."
        return response.json()
    
    def editar_pedido(self, pedido_id, 
                    codigo, 
                    id_cliente, 
                    id_funcionario, 
                    itens, 
                    origem, 
                    valor,
                    abertura,
                    fechamento,
                    estado, 
                    obs):
        API_URL = "http://127.0.0.1:8000/pedidos/"
        try:    
            response = requests.put(f"{API_URL}{pedido_id}", json={"codigo":codigo, 
                                                                    "id_cliente": id_cliente, 
                                                                    "id_funcionario":id_funcionario, 
                                                                    "itens":itens, 
                                                                    "origem":origem, 
                                                                    "valor":valor,
                                                                    "abertura": abertura,
                                                                    "fechamento": fechamento, 
                                                                    "estado":estado, 
                                                                    "obs":obs})
        except:
            return "Falha na cominicação.\nVerifique o seu funcionamento da API."
        return response.json() 
    def editar_origem(self,pedido_id,origem):
        p = Pedido(**self.obter_pedido(pedido_id))
        p.origem = origem
        self.editar_pedido(p.id,p.codigo,p.id_cliente,p.id_funcionario,p.itens,p.origem,p.valor,p.abertura,p.fechamento,p.estado,p.obs)
    def editar_campo(self,pedido_id,campo,conteudo):
        p = Pedido(**self.obter_pedido(pedido_id))
        match campo:
            case "codigo":
                p.codigo = conteudo
            case "id_cliente":
                p.id_cliente = conteudo
            case "abertura":
                p.abertura = conteudo
            case "fechamento":
                p.fechamento = conteudo
            case "estado":
                p.estado = conteudo
            case "valor":
                p.valor = conteudo
            case "origem":
                p.origem = conteudo
        self.editar_pedido(p.id,p.codigo,p.id_cliente,p.id_funcionario,p.itens,p.origem,p.valor,p.abertura,p.fechamento,p.estado,p.obs)
    def deletar(self,pedido_id):
        API_URL = "http://127.0.0.1:8000/pedidos/"
        try:
            response = requests.delete(f"{API_URL}{pedido_id}")
        except:
            return "Falha na comnicação.\nVerifique o seu funcionamento da API."
        return response.json()

class Box_List(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Label_Itens(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.setter('text_size')) 
        self.color =0,0,0

class ScrollBox(BoxLayout):
    def __init__(self, **kwargs):
        #self.bind(minimum_height=self.setter('height'))
        super().__init__(**kwargs)

class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size')) 
        self.background_normal = ''
        self.background_color = [.8, .8, .8, 1]    # blue colour
        self.color = 0,0,0
        self.height = 30
        self.halign = "left"
        self.padding = 10,0,0,0
        self.font_size = 12

class SpinnerDropdown(DropDown):
    def __init__(self, **kwargs):
        super(SpinnerDropdown, self).__init__(**kwargs)
        self.auto_width = False
        self.width = 150
        self.font_size = 12
        #self.bind(size=self.setter('text_size'))
class MyFooterLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
class MySpinner(Spinner):
    def __init__(self, **kwargs):
        super(MySpinner, self).__init__(**kwargs)
        self.font_size = 12
        self.dropdown_cls = SpinnerDropdown
        self.option_cls = SpinnerOptions
        self.halign = "left"
        self.padding = 10,0,0,0
        self.bind(size=self.setter('text_size'))
class Back(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
class ItemPedido(BoxLayout):
    def __init__(self,item, **kwargs):
        self.item =item
        super().__init__(**kwargs) 
        
class Pedidos(Screen):
    def __init__(self, **kw):
        self.pedido_ativo = ""
        self.pedidos_qnt = 0
        super().__init__(**kw)
    def criar_pedido(self, codigo, 
                    id_funcionario,
                    abertura  
                    ): 
        API_URL = "http://127.0.0.1:8000/pedidos/"
        #print("\n\n A URL FOI REQUISITADA \n\n")
        try:
            response = requests.post(API_URL, json={"codigo":codigo, 
                                                    "id_cliente": "anonimo", 
                                                    "id_funcionario":id_funcionario,
                                                    "endereco":"", 
                                                    "origem":"selecionar", 
                                                    "itens":[], 
                                                    "formas_pagamento":[],
                                                    "valor_total": "", 
                                                    "abertura": abertura,
                                                    "fechamento": "", 
                                                    "estado":"Criado",
                                                    "obs":""},headers=self.headers,timeout=10)
            #print("\n\n TRY RESPONSE DO MAIN \n\n")
        except:
            return "Falha na comunicação.\nVerifique o funcionamento da API."
        #print("\n\n A RESPOSTA SERÁ ENVIADA \n\n")
        return response.json()
    
    def deletar_pedido(self,pedido_id):
        API_URL = "http://127.0.0.1:8000/pedidos/"
        try:
            response = requests.delete(f"{API_URL}{pedido_id}",headers=self.headers)
        except:
            return "Falha na comnicação.\nVerifique o seu funcionamento da API."
        return response.json()
    def marcar_abertura(self):
        agora = datetime.now()
        hora_minuto = agora.strftime("%H:%M")
        return hora_minuto
    def contar_pedidos(self):
        API_URL = "http://127.0.0.1:8000/pedidos/"
        #print("#  ENTROU NO CARREGAMENTO DE PEDIDOS")
        if self.pedidos_qnt != 0:
            try:
                #print("#  ENTROU NO 'TRY' CARREGAMENTO DE PEDIDOS")
                response = requests.get(f"{API_URL}",headers=self.headers,timeout=10)
            except:
                return "Falha na comunicação.\n Verifique o seu funcionamento da API."
            try:
                for i in response.json():
                    p = Pedido(**i)
                self.pedidos_qnt = int(p.codigo) +1
            except:
                self.pedidos_qnt = 1
        else:
            self.pedidos_qnt += 1
        return self.pedidos_qnt
    def carregar_pedidos(self,pedido_id):
        API_URL = "http://127.0.0.1:8000/pedidos/"
        #print("#  ENTROU NO CARREGAMENTO DE PEDIDOS")
        try:
            #print("#  ENTROU NO 'TRY' CARREGAMENTO DE PEDIDOS")
            response = requests.get(f"{API_URL}{pedido_id}",headers=self.headers,timeout=10)
            if not response.ok:
                try:
                    return (response.json().get("detail") or response.text).strip()
                except ValueError:
                    return (response.text or f"Erro {response.status_code}").strip()

        except:
            return "Falha na cominicação.\nVerifique o seu funcionamento da API."    
        return response
    def listar_pedidos(self):
        response = self.carregar_pedidos("")
        for i in response.json():
            try:
                p = Pedido(**i)
            except:
                p = Pedido(**response.json())
            #print("# PEDIDOS AQUI")
            #for j in vars(p):
            #    print(j)
            self.ids.lista_pedidos.add_widget(Btn_Pedido(p.id,p.codigo,p.id_cliente,p.id_funcionario,p.itens,p.origem,p.valor_total,p.abertura,p.fechamento,p.estado,p.obs))
    def carregar_cardapio(self,produto_id):
        API_URL = "http://127.0.0.1:8000/produtos/"
        try:
            response = requests.get(f"{API_URL}{produto_id}",headers=self.headers,timeout=10)
            if not response.ok:
                try:
                    return (response.json().get("detail") or response.text).strip()
                except ValueError:
                    return (response.text or f"Erro {response.status_code}").strip()
        except:
            return "Falha na comunicação.\nVerifique o seu funcionamento da API."
        print(str(response.json()))
        for i in response.json():
            print(f"# PRODUTOS AQUI {str(i)}")

            p = Produto(**i)
            print(f'{p.categoria},{p.codigo},{p.nome},{p.valor}')
            self.ids.itens_cardapio.add_widget(Btn_Item(p.categoria,p.codigo,p.nome,p.valor))
        return response.json()
    def pesquisar_produtos(self, response, pesquisa):
        print("\n Entrou na leitura de resposta\n",response)
        self.ids.itens_cardapio.clear_widgets()
        for i in response:
            p = Produto(**i)
            if (pesquisa.lower() in str(p.categoria).lower() or pesquisa.lower() in str(p.nome).lower()):
                self.ids.itens_cardapio.add_widget(Btn_Item(p.categoria,p.codigo,p.nome,p.valor))
    def pesquisar_pedidos(self, response, pesquisa):
        print("\n Entroun na leitura de resposta\n",response)
        self.ids.lista_pedidos.clear_widgets()
        for i in response.json():
            p = Pedido(**i)
            if (pesquisa.lower() in str(p.id_cliente).lower() or pesquisa.lower() in str(p.id_funcionario).lower()):
                self.ids.lista_pedidos.add_widget(Btn_Pedido(p.id,p.codigo,p.id_cliente,p.id_funcionario,p.itens,p.origem,p.valor,p.abertura,p.fechamento,p.estado,p.obs))
    def abrir_pedido(self,id):
        self.ids.lista_pedidos.add_widget(Pedido_aberto(id,self.headers))
        self.pedido_ativo = id
        
    def udpade_pedido(self,id_pedido,campo,valor):
        API_URL = f"http://127.0.0.1:8000/pedidos/{id_pedido}/update"
        update = {"campo": f"{campo}","valor": f"{valor}"}
        response = requests.patch(API_URL, params=update, headers=self.headers,timeout=10)
    def adicionar_item_pedido(self,codigo,nome,valor):
        API_URL = fr"http://127.0.0.1:8000/pedidos/{self.pedido_ativo}/itens/add"
        payload = {"codigo": f"{codigo}","nome": f"{nome}","valor_und": f"{valor}","qnt": "1"}
        response = requests.put(API_URL, json=payload, headers=self.headers,timeout=10)
        #MyPopUp_Alerta("adicionou").open()
    #     API_URL = f"http://127.0.0.1:8000/pedidos/{self.pedido_ativo}/itens/add"

    #     response2 = self.carregar_pedidos(self.pedido_ativo)
    #     p = Pedido(**response2)
    #     novo_valor = float(valor.replace(",", "."))  + float(p.valor.replace(",", "."))
    #     payload = {"item": {"cod": f"{codigo}", "nome": f"{nome}", "valor": f"{valor}","qnt":"1"},"novo_valor": f"{novo_valor}"}
    #     response = requests.put(API_URL, json=payload, headers=self.headers, timeout=10)
        
        #self.editar_atributo(self.pedido_ativo,"valor",str(valor))
    # def editar_atributo(self,id_pedido, atributo, valor):
    #     aux = Pedido(**self.carregar_pedidos(id_pedido))
    #     setattr(aux,atributo,valor)
    #     #aux.id_cliente = atributo
    #     self.editar_pedido(id_pedido,aux.codigo,aux.id_cliente,aux.id_funcionario,aux.origem,aux.valor,aux.abertura,aux.fechamento,aux.estado,aux.obs)
    
#editar pedido -----------------
    # def editar_pedido(self, pedido_id, 
    #                   codigo, 
    #                   id_cliente, 
    #                   id_funcionario,  
    #                   origem, 
    #                   valor,
    #                   abertura,
    #                   fechamento,
    #                   estado, 
    #                   obs):
    #     API_URL = "http://127.0.0.1:8000/pedidos/"
    #     try:    
    #         response = requests.put(f"{API_URL}{pedido_id}", json={"codigo":codigo, 
    #                                                                 "id_cliente": id_cliente, 
    #                                                                 "id_funcionario":id_funcionario, 
    #                                                                 "itens":[], 
    #                                                                 "origem":origem, 
    #                                                                 "valor":valor,
    #                                                                 "abertura": abertura,
    #                                                                 "fechamento": fechamento, 
    #                                                                 "estado":estado, 
    #                                                                 "obs":obs},headers=self.headers)
    #     except:
    #         return "Falha na cominicação.\nVerifique o seu funcionamento da API."
    #     return response.json()
#fim editar pedido ---------------------------------------------
#     def gerar_codigo(self):
#         timestamp = str(datetime.now())
#         print(f"Carimbo de tempo: {timestamp}")
#         return timestamp
#     def criar_pedido(self, 
#                     codigo: str = "0000",
#                     id_cliente: str = "Anônimo",
#                     id_funcionario: str = "Geral",
#                     itens: Optional[List[dict]] = Field(default_factory=list),
#                     origem: str = "desconhecida",
#                     valor_centavos: int = 0,  # ex.: 1299 = R$ 12,99
#                     abertura: Optional[str] = Field(default_factory=str),
#                     fechamento: Optional[str] = Field(default_factory=str),
#                     estado: str = "Criado",
#                     obs: str = "Insira informações para a validação"
#                     # codigo=f"0000", 
#                     # id_cliente="Anônimo",
#                     # id_funcionario="Geral",
#                     # itens=[],
#                     # origem="desconhecida",
#                     # valor="00,00",
#                     # abertura=f"{datetime.today()}",
#                     # fechamento="XX:XX",
#                     # estado="Criado", 
#                     # obs="Insira informações para a validação"
#                     ):
#         if itens is None:
#             itens = []
#         if abertura is None:
#             abertura = str(datetime.now().isoformat())
#         if fechamento is None:
#             fechamento = "XX:XX"
#         payload = {
#             "codigo": codigo,
#             "id_cliente": id_cliente,
#             "id_funcionario": id_funcionario,
#             "itens": itens,
#             "origem": origem,
#             "valor_centavos": valor_centavos,
#             "abertura": abertura,
#             "fechamento": fechamento,
#             "estado": estado,
#             "obs": obs,
#         }
#         API_URL = "http://127.0.0.1:8000/pedidos/"
#         print("\n\n A URL FOI REQUISITADA \n\n")
#         try:
#             response = requests.post(API_URL, json=payload)
#             print("\n\n TRY RESPONSE DO MAIN \n\n")
#         except:
#             return "Falha na comunicação.\nVerifique o funcionamento da API."
#         print("\n\n A RESPOSTA SERÁ ENVIADA \n\n")
#         return response.json()
        
#     def limpar(self):
#         self.ids.itens_cardapio.clear_widgets()
#         self.ids.lista_pedidos.clear_widgets()
#     def carregar_cardapio(self,produto_id):
#         API_URL = "http://127.0.0.1:8000/produtos/"
#         try:
#             response = requests.get(f"{API_URL}{produto_id}")
#         except:
#             return "Falha na comunicação.\nVerifique o seu funcionamento da API."
#         print(str(response.json()))
#         for i in response.json():
#             print("# PRODUTOS AQUI")
#             p = Produto(**i)
#             print(f'{p.categoria},{p.codigo},{p.nome},{p.valor}')
#             self.ids.itens_cardapio.add_widget(Btn_Item(p.categoria,p.codigo,p.nome,p.valor))
#     def carregar_cardapio_categoria(self,categoria):
#         self.categoria = categoria
#         self.produto_id = ""
#         API_URL = "http://127.0.0.1:8000/produtos/"
#         try:
#             response = requests.get(f"{API_URL}{self.produto_id}")
#         except:
#             return "Falha na comunicação.\nVerifique o seu funcionamento da API."
#         print(str(response.json()))
#         #self.ids.Pedidos.ids.header_itens.add_widget(Back)
#         for i in response.json():
#             print("# PRODUTOS AQUI")
#             p = Produto(**i)
#             print(f'{p.categoria},{p.codigo},{p.nome},{p.valor}')
#             if p.categoria == self.categoria:
#                 self.ids.itens_cardapio.add_widget(Btn_Item(p.categoria,p.codigo,p.nome,p.valor))
#     def carregar_categorias(self,produto_id):
#         API_URL = "http://127.0.0.1:8000/produtos/"
#         try:
#             response = requests.get(f"{API_URL}{produto_id}")
#         except:
#             return "Falha na comunicação.\nVerifique o seu funcionamento da API."
#         print(str(response.json()))
#         ctrl_categoria = ""
#         for i in response.json():
#             print("# PRODUTOS AQUI")
#             p = Produto(**i)
            
#             print(f'{p.categoria},{p.codigo},{p.nome},{p.valor}')
#             if p.categoria != ctrl_categoria:
#                 ctrl_categoria = p.categoria
#                 self.ids.itens_cardapio.add_widget(Btn_Categoria(p.categoria))
# # ITENS
#     def obter_itens(self,pedido_id=""):
#         print(f"\n\nID DO PEDIDO AQUI, MISÉEEERA! {pedido_id} \n\n")
#         API_URL = "http://127.0.0.1:8000/produtos/"
#         try:
#             print("BATEU NO TRY DE OBTENÇÃO")
#             response = requests.get(f"{API_URL}{pedido_id}")
#         except:
#             return "Falha na comunicação.\nVerifique o seu funcionamento da API."
#         return response.json()
# # ITENS
#     def carregar_pedidos(self,pedido_id):
#         API_URL = "http://127.0.0.1:8000/pedidos/"
#         print("#  ENTROU NO CARREGAMENTO DE PEDIDOS")
#         try:
#             print("#  ENTROU NO 'TRY' CARREGAMENTO DE PEDIDOS")
#             response = requests.get(f"{API_URL}{pedido_id}")
#         except:
#             return "Falha na cominicação.\nVerifique o seu funcionamento da API."
#         for i in response.json():
#             p = Pedido(**i)
#             print("# PEDIDOS AQUI")
#             #for j in vars(p):
#             #    print(j)
#             self.ids.lista_pedidos.add_widget(Btn_Pedido(p.id,p.codigo,p.id_cliente,p.id_funcionario,p.itens,p.origem,p.valor,p.abertura,p.fechamento,p.estado,p.obs))    
#         return response.json()
#     def editar_pedido(self, pedido_id='', 
#                       codigo ='', 
#                       id_cliente ='', 
#                       id_funcionario ='', 
#                       itens='', 
#                       origem='', 
#                       valor='',
#                       abertura='',
#                       fechamento='',
#                       estado='', 
#                       obs=''):
        
#         API_URL = "http://127.0.0.1:8000/pedidos/"
#         try:    
#             response = requests.put(f"{API_URL}{pedido_id}", json={"codigo":codigo, 
#                                                                     "id_cliente": id_cliente, 
#                                                                     "id_funcionario":id_funcionario, 
#                                                                     "itens":itens, "origem":origem, 
#                                                                     "valor":valor,
#                                                                     "abertura": abertura,
#                                                                     "fechamento": fechamento, 
#                                                                     "estado":estado, 
#                                                                     "obs":obs})
#         except:
#             return "Falha na cominicação.\nVerifique o seu funcionamento da API."
#         return response.json() 
#     #------
#     def atualizar_campo_pedido(self, pedido_id: str, campo: str, valor:dict):
#         API_URL = f"http://127.0.0.1:8000/pedidos/{pedido_id}"
#         print(f"Esta é a URL: {API_URL}")
#         payload = {
#             "campo": campo,
#             "valor": valor
#         }
#         print(f"Esta é o campo: {campo}")
#         print(f"Esta é o campo: {valor}")
#         try:
#             response = requests.patch(API_URL, json=payload)
#             response.raise_for_status()  # Lança erro para status 4xx/5xx
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             return {"erro": str(e)}