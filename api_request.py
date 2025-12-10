import requests
import logging
import base64
import hmac
import json
import hashlib


def generate_token_request (body: dict) -> str:
     header = {
          "alg": "HS256",
          "typ": "JWT",
     }
     header_body = json.dumps(header).encode("utf-8")
     header64 = base64.b64encode(header_body).decode("utf-8")

     payload = body
     payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
     payload64 = base64.b64encode(payload_json).decode("utf-8")

     secret = "tisa098*"
     message = f"{header64}.{payload64}".encode("utf-8")

     digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
     sign = base64.b64encode(digest).decode("utf-8")

     token = f"{header64}.{payload64}.{sign}"     
     return token


def get_relatorio() -> str:
     return ""


def get_supervisores_ativos () -> dict:
     try:
          json_data = {
               "function" : "getSupervisor",
               "database" : "atacado",
               "matricula" : "3312"
          }

          token = generate_token_request(json_data)

          body = {
               "connection" : "atacado",
               "token" : token
          }

          response = requests.post('https://analytics.agnconsultoria.com.br/api/filtros/query_filtros.php', json=body)
          
          if response.status_code != 200:
               raise Exception("Erro ao executar solicitação na API, erro interno da API de terceiros!")
          
          return response.json()
     except Exception as e:
          logging.error(e)
          return {}

def relatorio_inadiplencia_filtrando_supervisor() -> dict:
     try:
          json_body = {

          }
          token = generate_token_request(json_body)

          body_request = {
               "connection" : "atacado",
               "token" : token
          }

          response = requests.post("", json=body_request)

          if response.status_code == 200:
               return response.json()
          else:
               raise Exception("Status code diferente de 200, erro ao executar requisisção de relatorio na função relatorio_inadiplencia_filtrando_supervisor")

     except Exception as e:
          print(e)
          return {}
     
def send_mensagem_chatbot(msg: str, numero: str) -> str:
     try:
          
          headers = {
               "Content-Type": "application/json",
               "apikey": "429683C4C977415CAAFCCE10F7D57E11"
          }

          body_message_json = {
               "number": numero,
               "text": msg
          }
          
          response = requests.post("http://192.33.0.24:8081/message/sendText/ti", headers=headers, json=body_message_json)
          
          if response.status_code != 201 and response.status_code != 200:
               raise Exception(response.json())
          
          return f"Mensagem enviada com sucesso para o numero {numero} "
     except Exception as e :
          return f"Erro ao enviar mensagem: {e}"