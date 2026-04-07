# Notificar RCAs - Relatório de Inadimplência

## Descrição do Projeto

Este projeto automatiza a geração e envio de relatórios semanais de inadimplência para Gerentes Regionais (GRs) e Gerentes de Área (GAs). O sistema é projetado para ser executado semanalmente, idealmente aos sábados pela manhã (por exemplo, às 08:00), utilizando dados de inadimplência dos Representantes Comerciais (RCAs) associados.

O relatório é baseado em um espelho similar ao sistema 8318 e inclui informações detalhadas sobre clientes inadimplentes, com foco em títulos vencidos entre 90 e 10 dias de atraso.

## Funcionalidades Principais

- **Obtenção de Dados**: Consulta APIs para recuperar listas de supervisores ativos e relatórios de inadimplência filtrados por supervisor.
- **Geração de Relatórios**: Cria arquivos Excel (.xlsx) com dados organizados, incluindo:
  - Nome do GA
  - Nome do GR
  - Nome do RCA (com quebra por inadimplência individual)
  - Dados dos clientes: razão social, endereço, telefones de contato, e-mails
  - Dados do título
  - Últimos 3 históricos de cobranças (rotina 1214, se disponível)
- **Agrupamentos e Somas**: No final do relatório, soma os valores por RCA, por GR e por GA.
- **Envio Automático**: Envia os relatórios gerados via WhatsApp para os destinatários apropriados.

## Estrutura do Projeto

- `api_request.py`: Classe responsável por interações com APIs externas, geração de tokens JWT e envio de mensagens.
- `create_excel.py`: Função para criar e formatar arquivos Excel a partir dos dados obtidos.
- `main.py`: Script principal que orquestra a execução do processo.
- `requirements.txt`: Lista de dependências Python necessárias.

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
SCHEDULE_DAYS='SEG,TER,QUA,QUI,SEX'
SCHEDULE_TIMES='08:00,12:00'
```

- `TIMEZONE` é obrigatório e deve ser um timezone válido (ex.: `America/Sao_Paulo`).
- `SCHEDULE_DAYS` aceita: `SEG,TER,QUA,QUI,SEX,SAB,DOM`.
- `SCHEDULE_TIMES` aceita múltiplos horários em `HH:MM`, separados por vírgula.
- O scheduler executa pela combinação de dias x horários.

### Execução sem Docker

- Execução única (manual):

  ```
  python main.py
  ```

  Use `RUN_MODE='once'` para finalizar após uma execução.

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

   O container será executado em background e o sistema seguirá o agendamento definido no `.env`. Os arquivos gerados serão salvos na pasta `arquivos-gerados/` do host.

## Período de Vencimento

O relatório foca em títulos com vencimento entre 90 e 10 dias de atraso.

## Notas Técnicas

- Gera arquivos Excel com formatação avançada, incluindo tabelas agrupadas e somas automáticas.
- Envio de mídia via WhatsApp API.