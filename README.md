# Demonstração — Download de XML de notas no FSist

> Projeto de portfólio de **Victória Pedrosa**. **Demonstração** de download de XML de notas no FSist — versão com dados fictícios (nomes, CNPJs, e-mails e IDs internos substituídos).

## Problema de negócio
Baixar os XML de notas no FSist para cada empresa é repetitivo.

## Antes x depois
| | Antes | Depois |
|---|---|---|
| Como é feito | Download manual. | Robô baixa os XML para a pasta da empresa/competência. |

## Ganho
- XMLs disponíveis sem download manual.

## Tecnologias
Python, SQLite, Selenium, pandas

## Arquivos
- `baixar_notas.py`
- `requirements.txt`

## Como rodar
1. `pip install -r requirements.txt`
2. Copie `.env.exemplo` para `.env` e preencha os caminhos.
3. Execute o script principal.

## Autora
Victória Pedrosa — Product Owner do Time de IA, automação de processos contábeis e fiscais.
