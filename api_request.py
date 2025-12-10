import requests
import logging
import base64
import hmac
import json
import hashlib
import os
import dotenv

class ApiRequest:

     def __init__(self) -> None:
          dotenv.load_dotenv()
          self.agn_api_Key = os.getenv('AGN_API_KEY')
          self.agn_api_url = os.getenv('AGR_API_URL')
          self.wpp_api_key = os.getenv('WPP_API_KEY')
          self.wpp_api_url = os.getenv('WPP_API_URL')

     def generate_token_request (self,body: dict) -> str:
          try:
               header = {
                    "alg": "HS256",
                    "typ": "JWT",
               }
               header_body = json.dumps(header).encode("utf-8")
               header64 = base64.b64encode(header_body).decode("utf-8")

               payload = body
               payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
               payload64 = base64.b64encode(payload_json).decode("utf-8")

               secret = self.agn_api_Key
               if secret is None:
                    raise Exception("ERRO!A chave de api não pode ser lida ou não foi definida nas variaveis de ambiente.")

               message = f"{header64}.{payload64}".encode("utf-8")

               digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
               sign = base64.b64encode(digest).decode("utf-8")

               token = f"{header64}.{payload64}.{sign}"     
               return token
          except Exception as e:
               print(e)
               return ''



     def get_supervisores_ativos (self) -> dict:
          try:
               json_data = {
                    "function" : "getSupervisor",
                    "database" : "atacado",
                    "matricula" : "3312"
               }

               token = self.generate_token_request(json_data)

               body = {
                    "connection" : "atacado",
                    "token" : token
               }

               response = requests.post(f'{self.agn_api_url}/filtros/query_filtros.php', json=body)
               
               if response.status_code != 200:
                    raise Exception("Erro ao executar solicitação na API, erro interno da API de terceiros!")
               
               return response.json()
          except Exception as e:
               logging.error(e)
               return {}

     def relatorio_inadiplencia_filtrando_supervisor(self, codigo_supervisor: str, nome_supervisor: str) -> list :
          try:
               json_body = {
                    "database" : "atacado",
                    "matricula" : "3312",
                    "indexPage" : 0,
                    "cardsupervisor" : [{"codigo" : codigo_supervisor, "titulo": nome_supervisor}]
               }
               token = self.generate_token_request(json_body)

               body_request = {
                    "connection" : "atacado",
                    "token" : token
               }

               response = requests.post(f"{self.agn_api_url}/financeiro/clientes_inadimplentes_por_supervisor/index.php", json=body_request)

               if response.status_code == 200:
                    return response.json()
               else:
                    raise Exception("Status code diferente de 200, erro ao executar requisisção de relatorio na função relatorio_inadiplencia_filtrando_supervisor")

          except Exception as e:
               print(e)
               return []
          
     def send_mensagem_chatbot(self, msg: str, numero: str, caminho_arquivo: str, nome_nome_arquivo: str) -> str:
          try:
               
               headers = {
                    "Content-Type": "application/json",
                    "apikey": self.wpp_api_key
               }
               
               with open(caminho_arquivo, 'rb') as arquivo:
                    conteudo = arquivo.read()

               body_message_json = {
                    "number": numero,
                    "mediatype" : "document",
                    "fileName": f"{nome_nome_arquivo}",
                    "caption": f"{msg}",
                    "media": f"{base64.b64encode(conteudo).decode('utf-8')}"
                                   
               }

               response = requests.post(f"{self.wpp_api_url}/message/sendMedia/ti", headers=headers, json=body_message_json)
               
               if response.status_code != 201 and response.status_code != 200:
                    raise Exception(response.json())
               
               return f"Mensagem enviada com sucesso para o numero {numero} "
          except Exception as e :
               return f"Erro ao enviar mensagem: {e}"