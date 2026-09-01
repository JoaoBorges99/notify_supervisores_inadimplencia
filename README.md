# Notificar GAs — Relatórios de Inadimplência e Cadastro Incompleto

Gera e envia, via WhatsApp, relatórios Excel semanais para Gerentes de Área (GAs). Há **dois jobs independentes**, com agenda e falha isoladas:

- **Inadimplência**: títulos vencidos (espelho próximo da rotina 8318), com totais por RCA e supervisor.
- **Cadastro incompleto**: clientes bloqueados na rotina 1203 cujo histórico de bloqueio é **CADASTRO INCOMPLETO**.

O scheduler interno dispara cada job nos dias e horários do `.env`. O padrão sugerido é **segunda**: cadastro incompleto às **08:00** e inadimplência às **12:00**, para não colidir no WhatsApp.

## Pré-requisitos

- Python >= 3.9
- Docker e Docker Compose (opcional, para rodar em container)

## Funcionalidades

- Consulta supervisores ativos e o relatório filtrado por GA.
- Gera um Excel (`.xlsx`) por GA em `arquivos-gerados/`.
- **Inadimplência**: totais por RCA e supervisor, além de blocos agrupados por RCA.
- **Cadastro incompleto**: planilha de listagem (sem totais financeiros).
- Envia o Excel pelo WhatsApp. Se o GA não tiver clientes no relatório, nada é enviado.
- `DRY_RUN=true` gera os arquivos e **não** envia WhatsApp.

## Estrutura do projeto

```
.
├── main.py              # orquestra os jobs e o agendamento
├── api_request.py       # APIs externas, JWT e envio de WhatsApp
├── create_excel.py      # geração e formatação dos Excel
├── env_exemplo          # modelo das variáveis de ambiente
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy env_exemplo .env
```

Edite o `.env` com as chaves e URLs reais.

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `AGN_API_KEY` | sim | — | Chave HMAC para as APIs Analytics |
| `AGR_API_URL` | sim | — | URL base da API Analytics |
| `WPP_API_URL` | sim | — | URL base da API do bot WhatsApp |
| `WPP_SESSION_NAME` | não | `cobranca` | Sessão do bot em `POST /senddocument` |
| `RUN_MODE` | não | `once` | `once` (executa e sai) ou `scheduler` (loop) |
| `TIMEZONE` | sim | — | Ex.: `America/Sao_Paulo` |
| `DRY_RUN` | não | `false` | `true` gera Excel sem enviar WhatsApp |
| `INADIMPLENCIA_ENABLED` | não | `true` | Liga/desliga o job de inadimplência |
| `SCHEDULE_DAYS` | se o job estiver ligado | — | Dias da inadimplência (`SEG,TER,...`) |
| `SCHEDULE_TIMES` | se o job estiver ligado | — | Horários da inadimplência (`HH:MM`) |
| `CADASTRO_ENABLED` | não | `true` | Liga/desliga o job de cadastro incompleto |
| `CADASTRO_SCHEDULE_DAYS` | não | `SEG` | Dias do cadastro incompleto |
| `CADASTRO_SCHEDULE_TIMES` | não | `08:00` | Horários do cadastro incompleto |

Dias aceitos: `SEG,TER,QUA,QUI,SEX,SAB,DOM`. Horários em `HH:MM`, separados por vírgula. Falha em um job não cancela o outro nem o loop do scheduler.

Rotas da API Analytics:

- Inadimplência: `/financeiro/clientes_inadimplentes_por_supervisor/index.php`
- Cadastro incompleto: `/financeiro/cadastro_incompleto/index.php`

## Uso

### Execução única (manual)

```powershell
$env:RUN_MODE='once'
python main.py
```

### Validar sem enviar WhatsApp

```powershell
$env:DRY_RUN='true'
$env:RUN_MODE='once'
python main.py
```

### Scheduler (processo contínuo)

```powershell
$env:RUN_MODE='scheduler'
python main.py
```

Com `RUN_MODE='scheduler'`, o processo permanece ativo e dispara nos dias/horários do `.env`.

### Docker

O container usa o scheduler interno (sem cron):

1. Configure o `.env`.
2. Suba o serviço:

```bash
docker-compose up --build -d
```

Os arquivos gerados ficam em `arquivos-gerados/` no host.

## Notas técnicas

- Inadimplência: Excel com tabelas agrupadas e somas (`VALOR_TOTAL_COM_JUROS`, `VALOR_TOTAL_ORIGINAL`). Arquivo `sup-{codigo}-{data}.xlsx`.
- Cadastro incompleto: Excel de listagem. Arquivo `cadastro-sup-{codigo}-{data}.xlsx`.
- Envio via `POST {WPP_API_URL}/senddocument` (JSON com `sessionname`, telefone, caption e documento em base64).
