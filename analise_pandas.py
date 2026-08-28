"""RO1 - Versao alternativa da leitura e do agrupamento usando pandas.

Le o mesmo transacoes.csv, aplica as mesmas regras de validacao, agrupa por mes
com groupby e compara os numeros com os do relatorio.json gerado pelo notebook.

Uso: python analise_pandas.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

ARQUIVO_CSV = "transacoes.csv"
ARQUIVO_JSON = "relatorio.json"
LIMITE_SUSPEITO = 10000.00
TIPOS_VALIDOS = ("credito", "debito")
CAMPOS = ["quantidade", "total_credito", "total_debito", "saldo", "media", "maior_valor", "menor_valor"]


def carregar(caminho=ARQUIVO_CSV):
    """Le o CSV como texto para validar os campos do mesmo jeito que a solucao nativa."""
    try:
        return pd.read_csv(caminho, dtype=str)
    except FileNotFoundError:
        print(f"Arquivo nao encontrado: {caminho}")
        sys.exit(1)


def limpar(bruto):
    """Aplica as 5 regras de validacao e devolve so as linhas validas."""
    dados = bruto.copy()
    dados["id_num"] = pd.to_numeric(dados["id"], errors="coerce")
    dados["data_dt"] = pd.to_datetime(dados["data"], format="%Y-%m-%d", errors="coerce")
    dados["valor_num"] = pd.to_numeric(dados["valor"], errors="coerce")
    dados["tipo"] = dados["tipo"].fillna("").astype(str).str.strip().str.lower()
    dados["cliente_id"] = dados["cliente_id"].fillna("").astype(str).str.strip()

    valido = (
        dados["id_num"].notna()
        & dados["data_dt"].notna()
        & dados["valor_num"].gt(0)
        & dados["cliente_id"].ne("")
        & dados["tipo"].isin(TIPOS_VALIDOS)
    )
    return dados[valido].copy()


def resumir(validas):
    """Agrupa por mes com groupby e calcula as mesmas metricas do relatorio nativo."""
    validas["mes"] = validas["data_dt"].dt.strftime("%Y-%m")
    agregado = validas.groupby("mes")["valor_num"].agg(["count", "mean", "max", "min"])
    credito = validas[validas["tipo"] == "credito"].groupby("mes")["valor_num"].sum()
    debito = validas[validas["tipo"] == "debito"].groupby("mes")["valor_num"].sum()

    resumo = pd.DataFrame({
        "quantidade": agregado["count"],
        "total_credito": credito.reindex(agregado.index, fill_value=0.0),
        "total_debito": debito.reindex(agregado.index, fill_value=0.0),
        "media": agregado["mean"],
        "maior_valor": agregado["max"],
        "menor_valor": agregado["min"],
    })
    resumo["saldo"] = resumo["total_credito"] - resumo["total_debito"]
    return resumo[CAMPOS].round(2).sort_index()


def comparar(resumo, caminho=ARQUIVO_JSON):
    """Compara os numeros do pandas com os do relatorio.json (solucao nativa)."""
    if not Path(caminho).exists():
        print(f"{caminho} nao encontrado - rode o notebook antes para comparar.")
        return
    nativo = json.loads(Path(caminho).read_text(encoding="utf-8"))["resumo_mensal"]

    if set(nativo) != set(resumo.index):
        print(f"Meses diferentes: nativo={sorted(nativo)} pandas={sorted(resumo.index)}")
        return

    divergencias = 0
    for mes, linha in resumo.iterrows():
        for campo in CAMPOS:
            valor_pandas = round(float(linha[campo]), 2)
            valor_nativo = round(float(nativo[mes][campo]), 2)
            if abs(valor_pandas - valor_nativo) > 0.01:
                divergencias += 1
                print(f"DIVERGENCIA {mes}.{campo}: pandas={valor_pandas} nativo={valor_nativo}")

    if divergencias == 0:
        print("OK - todos os valores batem com a solucao nativa (csv + datetime).")
    else:
        print(f"{divergencias} divergencia(s) encontrada(s).")


def main():
    bruto = carregar()
    validas = limpar(bruto)

    print("===== RO1 - ANALISE COM PANDAS =====")
    print(f"Total de linhas lidas: {len(bruto)}")
    print(f"Linhas validas: {len(validas)}")
    print(f"Linhas invalidas: {len(bruto) - len(validas)}")

    resumo = resumir(validas)
    print("\n----- Resumo mensal (groupby) -----")
    print(resumo.to_string())

    suspeitas = validas[validas["valor_num"] > LIMITE_SUSPEITO]
    print(f"\n----- Transacoes suspeitas (acima de {LIMITE_SUSPEITO:.2f}) -----")
    print(suspeitas[["id", "data", "cliente_id", "valor_num"]].to_string(index=False))

    print("\n----- Comparacao com a solucao nativa -----")
    comparar(resumo)


if __name__ == "__main__":
    main()
