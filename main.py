import shutil
import os
from api_request import ApiRequest
import create_excel
from datetime import datetime
import re

def get_relatorio_por_supervisor ():
     print(f'Execução do envio de mensgens iniciada - {datetime.today()} ')

     if os.path.exists('arquivos-gerados'):
          for filename in os.listdir('arquivos-gerados'):
               file_path = os.path.join('arquivos-gerados', filename)
               if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
               elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
               
     sup_data = ApiRequest().get_supervisores_ativos()

     for supervisor in sup_data:
          if supervisor['telefone'] != None:
               numero_limpo = re.sub(r'[^0-9]', '', supervisor['telefone'])
               
               try:
                    nome = str(supervisor['titulo']).split('-')[1].strip().upper()
               except:
                    nome = str(supervisor['titulo']).upper()

               json_relatorio = ApiRequest().relatorio_inadiplencia_filtrando_supervisor(supervisor['codigo'], supervisor['titulo'])
               
               if json_relatorio == []:
                    print(f"Não há nenhum conteudo a ser enviado para o {supervisor['codigo']}-{str(supervisor['titulo']).upper()}")
                    continue

               caminho_arquivo = create_excel.writeExcel(json_relatorio, f"sup-{supervisor['codigo']}-{datetime.now().date()}")
               
               retorno_msg = ApiRequest().send_mensagem_chatbot(
                    f"Olá *{nome}*, segue em anexo o realtorio de inadimplência dos clientes da base de sua equipe.", 
                    # '5533991165622',
                    f"55{numero_limpo}",
                    caminho_arquivo,
                    f"sup-{supervisor['codigo']}-{datetime.now().date()}.xlsx"
               )
               print(retorno_msg)

     print(f'Execução finalizada - {datetime.today()} ')

get_relatorio_por_supervisor()