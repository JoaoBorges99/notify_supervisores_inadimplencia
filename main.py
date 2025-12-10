from api_request import ApiRequest
import re

def get_relatorio_por_supervisor ():
     sup_data = ApiRequest().get_supervisores_ativos()

     for supervisor in sup_data:
          if supervisor['telefone'] != None:
               numero_limpo = re.sub(r'[^0-9]', '', supervisor['telefone'])
               # retorno_msg = api_request.send_mensagem_chatbot(f"Olá {supervisor['titulo']}, segue em anexo o realtorio de inadimplência dos clientes da sua equipe", "5533991165622")
               # print(retorno_msg)


get_relatorio_por_supervisor()