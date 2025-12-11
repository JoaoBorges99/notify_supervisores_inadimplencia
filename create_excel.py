import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
import os

def writeExcel(data: list, file_name:str, extension: str = 'xlsx'):
     os.makedirs('arquivos-gerados', exist_ok=True)


     df = pd.DataFrame(data,)
     
     for colunas in df.columns:
          if colunas == 'valor_total_original':
               df["valor_total_original"] = pd.to_numeric(df["valor_total_original"], errors="coerce")

          if colunas == 'valor_total_com_juros':
               df["valor_total_com_juros"] = pd.to_numeric(df["valor_total_com_juros"], errors="coerce")

     df.columns = df.columns.str.upper()

     if extension == 'xlsx':

          df.to_excel(f'arquivos-gerados/{file_name}.{extension}', index=False)
          wb = load_workbook(f'arquivos-gerados/{file_name}.{extension}')
          ws = wb['Sheet1']

          for col in ws.columns:
               max_length = 0
               col_letter = col[0].column_letter
               
               for cell in col:
                    if cell.value:
                         max_length = max(max_length, len(str(cell.value)))

               ws.column_dimensions[col_letter].width = max_length + 2 

          ws["A1"].font = Font(bold=True)
          ws["A1"].alignment = Alignment(horizontal="center")

          
          wb.save(f'arquivos-gerados/{file_name}.{extension}')
          return f'arquivos-gerados/{file_name}.{extension}'
     
     elif extension == 'csv':
          df.to_csv(f'arquivos-gerados/{file_name}.{extension}', index=False)
          return f'arquivos-gerados/{file_name}.{extension}'
     else:
          raise ValueError('Extensão não suportada, use xlsx ou csv')