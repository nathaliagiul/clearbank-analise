# ClearBank — Análise Financeira com Python

Notebook em Python que lê e valida um arquivo CSV de transações bancárias, agrupa os dados por mês,
calcula métricas financeiras, sinaliza movimentações potencialmente suspeitas, exibe um relatório
formatado no terminal e exporta o resultado em JSON.

Projeto do desafio final do módulo de Python aplicado à análise de dados. Os requisitos obrigatórios
usam **apenas a biblioteca padrão** (`csv`, `json`, `datetime`) — `pandas` e `matplotlib` aparecem
somente nos requisitos opcionais.

## Como executar

**No Google Colab**

1. Abra `desafio-final.ipynb` no Colab.
2. Menu `Ambiente de execução → Executar tudo`.

**No Jupyter local** (Python 3.10 ou superior)

```bash
pip install pandas matplotlib
```

```bash
jupyter notebook desafio-final.ipynb
```

Depois execute as células **em ordem, do início ao fim**. Não é preciso baixar nada: a Célula 3 gera
o `transacoes.csv` usado na análise, então o notebook roda do zero.

Para rodar só a versão em pandas, com o `relatorio.json` já gerado:

```bash
python analise_pandas.py
```

## O que o notebook gera

| Arquivo | Conteúdo |
|---|---|
| `transacoes.csv` | Base de entrada: 15 registros válidos em 3 meses, 5 inválidos (um por regra de validação) e 2 transações acima de R$ 10.000,00 |
| `relatorio.json` | Relatório final: totais de válidas/inválidas, resumo mensal, transações suspeitas e período analisado |
| `grafico.png` | Gráfico de barras do saldo mensal (crédito − débito) |
| `analise_pandas.py` | Versão alternativa da leitura e do agrupamento com pandas, comparada com a solução nativa |

Além dos arquivos, a **Célula 9 (Execução Principal)** imprime no terminal:

- o resumo da limpeza (linhas lidas, válidas e inválidas);
- o período analisado (data mais antiga → mais recente e os dias entre elas);
- o relatório mensal com quantidade, total de crédito, total de débito, saldo, média, maior e menor
  valor de cada mês, em formato brasileiro (`R$ 1.234,56`);
- a lista de transações suspeitas (acima de `LIMITE_SUSPEITO = 10000.00`).

## Estrutura do repositório

```
clearbank-analise/
├── desafio-final.ipynb    # notebook principal, com as saídas salvas
├── transacoes.csv         # base de entrada (também gerada pela Célula 3)
├── relatorio.json         # saída gerada pelo notebook
├── grafico.png            # saída gerada pelo notebook (opcional RO2)
├── analise_pandas.py      # versão com pandas (opcional RO1)
└── README.md
```

## Organização do código

| Função | Responsabilidade |
|---|---|
| `ler_transacoes()` | Lê o CSV com `csv.DictReader` e devolve as linhas brutas |
| `validar_transacao()` | Valida uma linha e devolve o registro limpo (ou `None`) |
| `gerar_relatorio()` | Agrupa por mês e calcula as métricas |
| `salvar_json()` | Grava o resultado em `relatorio.json` |
| `exibir_relatorio()` | Formata e imprime o relatório no terminal |

Funções auxiliares: `validar_id()`, `validar_data()`, `validar_valor()`, `montar_registro()`,
`processar_transacoes()`, `exibir_resumo_limpeza()`, `acumular_mes()`, `fechar_metricas()`,
`calcular_resumo_mensal()`, `calcular_periodo()`, `resumir_suspeita()`, `formatar_moeda()`,
`exibir_cabecalho()`, `exibir_mes()`, `exibir_suspeitas()` e `executar_analise()`.

## Regras de validação

Uma linha é descartada silenciosamente quando tem `id` vazio ou não numérico, `cliente_id` vazio,
`data` fora do formato `AAAA-MM-DD`, `tipo` diferente de `credito`/`debito`, ou `valor` não numérico
ou menor ou igual a zero. Um dado inválido nunca interrompe a execução: o erro é capturado
(`FileNotFoundError` na abertura do arquivo, `ValueError` nas conversões de `valor` e `data`), a
linha é descartada e o processamento continua.

As decisões tomadas onde o enunciado deixa margem (definição da média, tratamento de duplicados,
limite estritamente "acima" de R$ 10.000,00) estão documentadas na segunda célula do notebook.
