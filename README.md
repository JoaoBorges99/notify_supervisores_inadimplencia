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

1. Configure as variáveis de ambiente necessárias (chaves de API, URLs) em um arquivo `.env`.
2. Execute o script principal:

   ```
   python main.py
   ```

   Idealmente, configure um agendamento semanal (ex.: via cron job ou task scheduler) para execução automática aos sábados.

## Período de Vencimento

O relatório foca em títulos com vencimento entre 90 e 10 dias de atraso.

## Notas Técnicas

- Gera arquivos Excel com formatação avançada, incluindo tabelas agrupadas e somas automáticas.
- Envio de mídia via WhatsApp API.