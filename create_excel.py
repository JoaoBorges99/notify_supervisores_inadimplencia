import pandas as pd
import os

def writeExcel(data: list, file_name:str, extension: str = 'xlsx'):
    os.makedirs('arquivos-gerados', exist_ok=True)

    df = pd.DataFrame(data,)
    if extension == 'xlsx':
        df.to_excel(f'arquivos-gerados/{file_name}.{extension}', index=False)
        return f'arquivos-gerados/{file_name}.{extension}'
    elif extension == 'csv':
        df.to_csv(f'arquivos-gerados/{file_name}.{extension}', index=False)
        return f'arquivos-gerados/{file_name}.{extension}'
    else:
        raise ValueError('Extensão não suportada, use xlsx ou csv')