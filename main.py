from api_request import ApiRequest
import create_excel
from datetime import datetime
import re

def get_relatorio_por_supervisor ():
     sup_data = ApiRequest().get_supervisores_ativos()

     for supervisor in sup_data:
          if supervisor['telefone'] != None:
               numero_limpo = re.sub(r'[^0-9]', '', supervisor['telefone'])
               json_relatorio = ApiRequest().relatorio_inadiplencia_filtrando_supervisor(supervisor['codigo'], supervisor['titulo'])
               
               if json_relatorio == []:
                    print(f"Não há nanhum conteudo a ser enviado para o {supervisor['codigo']}-{str(supervisor['titulo']).upper()}")
                    continue
               
               caminho_arquivo = create_excel.writeExcel(json_relatorio, f"{supervisor['codigo']}-{datetime.now().date()}")
               
               retorno_msg = ApiRequest().send_mensagem_chatbot(
                    f"Olá *{str(supervisor['titulo']).upper()}*, segue em anexo o realtorio de inadimplência dos clientes da base de sua equipe.", 
                    "5533991165622",
                    caminho_arquivo,
                    f"{supervisor['codigo']}-{datetime.now().date()}.xlsx"
               )
               print(retorno_msg)


get_relatorio_por_supervisor()