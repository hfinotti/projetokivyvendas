import requests
from kivy.app import App

class MyFirebase():
    API_KEY = "AIzaSyCXX4wwYFgAWLuZeFE04qYoK5X8afs8FPo"

    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        info = {"email": email, "password": senha, "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            meu_app = App.get_running_app()
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = "[color=#00FF00]CONTA CRIADA COM SUCESSO![/color]"

            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            meu_app.local_id = local_id
            meu_app.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            req_id = requests.get(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id.json()

            # CRIA UM NOVO USUÁRIO NO BANCO DE DADOS
            link = f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "0", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)

            # ATUALIZA O NUMERO DO ID DO PROXIMO VENDEDOR
            proximo_id_vendedor = int(id_vendedor) + 1
            inf_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://appvendaskivy-55847-default-rtdb.firebaseio.com/.json?auth={id_token}", data=inf_id_vendedor)

            meu_app.carregar_infos_usuario()
            meu_app.mudar_tela("homepage")
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_app = App.get_running_app()
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = f"[color=#FF0000]{mensagem_erro}[/color]".replace(":","\n")

    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email, "password": senha, "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            meu_app = App.get_running_app()
            meu_app.local_id = local_id
            meu_app.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            # CARREGA AS IFORMAÇOES DO USUÁRIO LOGADO
            meu_app.carregar_infos_usuario()
            meu_app.mudar_tela("homepage")
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_app = App.get_running_app()
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = f"[color=#FF0000]{mensagem_erro}[/color]".replace(":","\n")


    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"

        info = {"grant_type": "refresh_token", "refresh_token": refresh_token}

        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic["user_id"]
        id_token = requisicao_dic["id_token"]
        return local_id, id_token


