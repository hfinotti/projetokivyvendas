from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
import os
from functools import partial
from myfirebase import MyFirebase
from datetime import date


GUI = Builder.load_file('main.kv')

class MainApp(App):

    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase()

        return GUI

    def on_start(self):
        # CARREGA AS FOTOS DE PERFIL
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_fotoperfil, foto))
            lista_fotos.add_widget(imagem)

        # CARREGA AS FOTOS DOS CLIENTES
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}", on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(), on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        # CARREGA AS FOTOS DOS PRODUTOS
        arquivos = os.listdir("icones/fotos_produtos")
        pagina_fotoproduto = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_fotoproduto.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        # CARREGA DATA ATUAL PARA O CADASTRO DA VENDA
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        label_data = pagina_adicionarvendas.ids["label_data"]
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        # CARREGA AS INFORMAÇÕES DO USUARIO
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            # LE O ARQUIVO COM O REFRESH_TOKEN DO USUARIO
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # PEGA AS INFORMAÇÕES DO USUARIO NO BANCO DE DADOS
            requisicao = requests.get(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()

            # PREENCHE A FOTO DE PERFIL DO USUÁRIO
            avatar = requisicao_dic["avatar"]
            self.avatar = avatar
            foto_perfil = self.root.ids["id_foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            # PREENCHE O ID UNICO DO USUARIO
            id_vendedor = requisicao_dic["id_vendedor"]
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_vendedor"].text = f"Seu ID Único: {id_vendedor}"

            # PREENCHE O TOTAL DE VENDAS DO USUARIO
            total_vendas = requisicao_dic["total_vendas"]
            self.total_vendas = total_vendas
            pagina_home = self.root.ids["homepage"]
            pagina_home.ids["label_total_vendas"].text = f"Total de Vendas: [b]R$ [color=#00FF00]{total_vendas}[/color][/b]"

            # PREENCHE A VARIAVEL EQUIPE DO USUÁRIO
            self.equipe = requisicao_dic["equipe"]

            # PREENCHE AS VENDAS DO USUÁRIO
            try:
                vendas = requisicao_dic['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"], foto_cliente=venda["foto_cliente"],
                                         foto_produto=venda["foto_produto"], data=venda["data"], preco=venda["preco"],
                                         quantidade=venda["quantidade"], unidade=venda["unidade"])

                    pag_homepage = self.root.ids["homepage"]
                    lista_vendas = pag_homepage.ids["lista_vendas"]
                    lista_vendas.add_widget(banner)
            except Exception as excecao:
                print(excecao, "aaa")

            # CARREGA AS INFORMAÇÕES DA EQUIPE DO USUARIO
            equipe = requisicao_dic["equipe"]
            lista_equipe = equipe.split(",")
            pagina_lista_vendedores = self.root.ids["listarvendedorespage"]
            lista_vendedores = pagina_lista_vendedores.ids["lista_vendedores"]
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            # APOS CARREGAR AS INFORMAÇÕES DO USUARIO DIRECIONA ELE PARA A HOMEPAGE
            self.mudar_tela("homepage")
        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela


    def mudar_fotoperfil(self, foto, *args):
        foto_perfil = self.root.ids["id_foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)
        self.mudar_tela("ajustespage")


    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://appvendaskivy-55847-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo={id_vendedor_adicionado}'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        pagina_adicionar_vendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adicionar_vendedor.ids["mensagem_outrovendedor"]
        mensagem_texto.text = ""
        input_texto = pagina_adicionar_vendedor.ids["input_id_outrovendedor"]
        if int(id_vendedor_adicionado) == int(self.id_vendedor):
            mensagem_texto.text = "[b][color=#FF0000]Você não pode se adcionar à equipe.[/b][/color]"
        elif requisicao_dic == {}:
            mensagem_texto.text = "[b][color=#FF0000]Vendedor não encontrado.[/b][/color]"
        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "[b][color=#FF0000]Vendedor já faz parte da equipe.[/b][/color]"
            else:
                if self.equipe == "":
                    self.equipe = id_vendedor_adicionado
                else:
                    self.equipe = self.equipe + "," + id_vendedor_adicionado
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)
                mensagem_texto.text = "[b][color=#00FF00]Vendedor integrado com sucesso.[/b][/color]"
                # ADICIONA O  NOVO BANNER NA LISTA DE VENDEDORES
                pagina_lista_vendedores = self.root.ids["listarvendedorespage"]
                lista_vendedores = pagina_lista_vendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)
        input_texto.text = ""


    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace(".png", "")
        # marcar de azul o selecionado
        # voltar a branco todos os outros
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 1, 1, 1)
        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if texto == foto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        self.produto = foto.replace(".png", "")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 1, 1, 1)
        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if texto == foto:
                    item.color = (0, 207 / 255, 219 / 255, 1)
            except:
                pass


    def selecionar_unidade(self, id_label, *args):
        self.unidade = id_label.replace("unidades_", "")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        pagina_adicionarvendas.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_un"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_lt"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids[id_label].color = (0, 207 / 255, 219 / 255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data:", "")
        preco = pagina_adicionarvendas.ids["preco_total"].text
        quantidade = pagina_adicionarvendas.ids["quantidade_total"].text

        if not cliente:
            pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_un"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_lt"].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)

        if cliente and produto and unidade and preco and quantidade and (type(preco) == float and type(quantidade) == float):
            cliente = cliente.capitalize()
            produto = produto.capitalize()
            unidade = unidade.capitalize()
            foto_produto = produto.lower() + ".png"
            foto_cliente = cliente.lower() + ".png"

        # CRIAR E ENVIAR A NOVA VENDA
        info = (f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", '
                f'"foto_produto": "{foto_produto}", "unidade": "{unidade}", "data": "{data}", "preco": "{preco}", '
                f'"quantidade": "{quantidade}"}}')
        requests.post(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}", data=info)

        # CRIAR O BANNER E INCLUIR NA HOMEPAGE
        banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto,
                             unidade=unidade, data=data, preco=preco, quantidade=quantidade)
        pagina_homepage = self.root.ids["homepage"]
        lista_venda = pagina_homepage.ids["lista_vendas"]
        lista_venda.add_widget(banner)

        requisicao = requests.get(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
        total_vendas = requisicao.json()
        total_vendas = float(total_vendas) + preco
        info = f'{{"total_vendas": "{total_vendas}"}}'
        requests.patch(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{self.local_id}/.json?auth={self.id_token}", data=info)

        pagina_homepage.ids["label_total_vendas"].text = f"Total de Vendas: [b]R$ [color=#00FF00]{total_vendas}[/color][/b]"

        self.mudar_tela("homepage")

        cliente = None
        produto = None
        unidade = None


    def carregar_todas_vendas(self):
        pagina_todasvendas = self.root.ids["todasvendaspage"]
        lista_vendas = pagina_todasvendas.ids["lista_vendas"]

        # REMOVE TODOS OS ITENS DA LISTA_VENDAS ANTES DE POPULAR ELA.
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # PEGA AS INFORMAÇÕES DA EMPRESA NO BANCO DE DADOS
        requisicao = requests.get(f'https://appvendaskivy-55847-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()

        # PREENCHE A FOTO DE PERFIL DO USUÁRIO
        foto_perfil = self.root.ids["id_foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/hash.png"

        total_vendas_empresa = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas_empresa += float(venda["preco"])
                    banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"], foto_cliente=venda["foto_cliente"],
                                         foto_produto=venda["foto_produto"], unidade=venda["unidade"], data=venda["data"],
                                         preco=venda["preco"], quantidade=venda["quantidade"])
                    lista_vendas.add_widget(banner)
            except:
                pass

        # PREENCHE O TOTAL DE VENDAS DO USUARIO
        pagina_todasvendas.ids["label_total_vendas"].text = f"Vendas da Empresa: [b]R$ [color=#00FF00]{total_vendas_empresa:,.2f}[/color][/b]"
        self.mudar_tela("todasvendaspage")


    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):
        pagina_vendasoutrovendedorpage = self.root.ids["vendasoutrovendedorpage"]
        lista_vendas = pagina_vendasoutrovendedorpage.ids["lista_vendas"]

        # REMOVE TODOS OS ITENS DA LISTA_VENDAS ANTES DE POPULAR ELA.
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        try:
            vendas = dic_info_vendedor["vendas"]
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"],
                                     foto_cliente=venda["foto_cliente"],
                                     foto_produto=venda["foto_produto"], unidade=venda["unidade"], data=venda["data"],
                                     preco=venda["preco"], quantidade=venda["quantidade"])
                lista_vendas.add_widget(banner)
        except:
            pass
        # PREENCHE O TOTAL DE VENDAS DO USUARIO
        total_vendas = dic_info_vendedor["total_vendas"]
        pagina_vendasoutrovendedorpage.ids["label_total_vendas"].text = f"Vendas da Empresa: [b]R$ [color=#00FF00]{total_vendas}[/color][/b]"

        # PREENCHE A FOTO DE PERFIL DO USUÁRIO
        foto_perfil = self.root.ids["id_foto_perfil"]
        avatar = dic_info_vendedor["avatar"]
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"

        self.mudar_tela("vendasoutrovendedorpage")


    def sair_todas_vendas(self, id_pagina):
        foto_perfil = self.root.ids["id_foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"
        self.mudar_tela(f"{id_pagina}")


MainApp().run()

