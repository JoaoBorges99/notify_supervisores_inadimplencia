# Notificar GAs — Relatórios de Inadimplência e Cadastro Incompleto

## Descrição do Projeto

Este projeto automatiza a geração e o envio semanal de relatórios para Gerentes de Área (GAs) via WhatsApp. Há **dois jobs independentes**, cada um com agenda e falha isoladas:

- **Inadimplência**: títulos vencidos (espelho próximo da rotina 8318), com totais por RCA e supervisor.
- **Cadastro incompleto**: clientes **bloqueados** na rotina 1203 cujo histórico de bloqueio é **CADASTRO INCOMPLETO**.

O scheduler interno dispara cada job nos dias e horários configurados. O padrão sugerido é **segunda**: cadastro incompleto às **08:00** e inadimplência às **12:00**, para não colidir no WhatsApp.

## Funcionalidades Principais

- **Obtenção de Dados**: consulta a lista de supervisores ativos e o relatório filtrado por GA.
- **Geração de Relatórios**: cria arquivos Excel (.xlsx) por GA.
- **Inadimplência**: totais por RCA e supervisor, além de blocos agrupados por RCA.
- **Cadastro incompleto**: planilha de listagem (sem totais financeiros), com blocos por RCA quando a coluna existir.
- **Envio Automático**: WhatsApp com o Excel em anexo. Se o GA não tiver clientes no relatório, nada é enviado.

## Estrutura do Projeto

- `api_request.py`: APIs externas, JWT e envio de mensagens.
- `create_excel.py`: geração e formatação dos Excel.
- `main.py`: orquestra os jobs e o agendamento.
- `requirements.txt`: dependências Python.

## Como Usar

### Variáveis de ambiente

Configure as variáveis em `.env`:

```env
AGN_API_KEY='...'
AGR_API_URL='...'
WPP_API_KEY='...'
WPP_API_URL='...'

RUN_MODE='scheduler'
TIMEZONE='America/Sao_Paulo'

INADIMPLENCIA_ENABLED='true'
SCHEDULE_DAYS='SEG'
SCHEDULE_TIMES='12:00'

CADASTRO_ENABLED='true'
CADASTRO_SCHEDULE_DAYS='SEG'
CADASTRO_SCHEDULE_TIMES='08:00'
```

- `TIMEZONE` é obrigatório (ex.: `America/Sao_Paulo`).
- `INADIMPLENCIA_ENABLED` e `CADASTRO_ENABLED` aceitam `true`/`false`. Padrão: `true`.
- `SCHEDULE_DAYS` / `SCHEDULE_TIMES`: agenda da **inadimplência** (obrigatórios se o job estiver ligado).
- `CADASTRO_SCHEDULE_DAYS` / `CADASTRO_SCHEDULE_TIMES`: agenda do **cadastro incompleto**. Se omitidos, usam `SEG` e `08:00`.
- Dias aceitos: `SEG,TER,QUA,QUI,SEX,SAB,DOM`.
- Horários em `HH:MM`, separados por vírgula.
- Falha em um job não cancela o outro nem o loop do scheduler.
- `DRY_RUN=true`: gera os Excel e **não** envia WhatsApp (para validar o fluxo).

Rotas da API analytics:

- Inadimplência: `/financeiro/clientes_inadimplentes_por_supervisor/index.php`
- Cadastro incompleto: `/financeiro/cadastro_incompleto/index.php`

### Execução com .venv

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Validar sem enviar WhatsApp:

```
python -m unittest test_servico.py -v
```

```
set DRY_RUN=true
set RUN_MODE=once
python main.py
```

No PowerShell:

```
$env:DRY_RUN='true'
$env:RUN_MODE='once'
python main.py
```

### Execução sem Docker

- Execução única (manual) dos jobs habilitados:

  ```
  python main.py
  ```

  Use `RUN_MODE='once'` para finalizar após a execução.

- Execução contínua (agendada pelo próprio Python):

  ```
  python main.py
  ```

  Use `RUN_MODE='scheduler'` para manter o processo ativo e disparar nos dias/horários do `.env`.

### Usando Docker

Para executar com Docker usando scheduler interno (sem cron no container):

1. Certifique-se de que o Docker e Docker Compose estão instalados.
2. Configure o arquivo `.env` com as variáveis necessárias.
3. Execute:

   ```
   docker-compose up --build -d
   ```

   O container segue o agendamento do `.env`. Os arquivos gerados vão para `arquivos-gerados/` no host.

## Notas Técnicas

- Inadimplência: Excel com tabelas agrupadas e somas automáticas (`VALOR_TOTAL_COM_JUROS`, `VALOR_TOTAL_ORIGINAL`).
- Cadastro incompleto: Excel de listagem, arquivo `cadastro-sup-{codigo}-{data}.xlsx`.
- Envio de mídia via WhatsApp API.
