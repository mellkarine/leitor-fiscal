"""Mede o acerto da extração contra o gabarito.

Uso:
    python -m leitor_fiscal.avaliar --previsto saida/documentos.csv \
        --gabarito data/sintetico/gabarito/documentos.csv
"""
import argparse
import re
import unicodedata

import pandas as pd

CAMPOS = ["tipo", "emitente", "doc_emitente", "numero", "data", "vencimento", "valor_total", "destinatario"]
NUMERICOS = {"valor_total"}


def _texto(v) -> str:
    if pd.isna(v):
        return ""
    s = unicodedata.normalize("NFKD", str(v)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().casefold()


def _igual(campo: str, previsto, esperado) -> bool:
    if campo in NUMERICOS:
        a = None if pd.isna(previsto) or str(previsto).strip() == "" else float(previsto)
        b = None if pd.isna(esperado) or str(esperado).strip() == "" else float(esperado)
        return (a is None and b is None) or (a is not None and b is not None and abs(a - b) < 0.005)
    return _texto(previsto) == _texto(esperado)


def avaliar(previsto: pd.DataFrame, gabarito: pd.DataFrame) -> pd.DataFrame:
    """Compara campo a campo, só nos arquivos presentes nos dois lados."""
    previsto = previsto.set_index("arquivo")
    gabarito = gabarito.set_index("arquivo")
    comuns = [a for a in gabarito.index if a in previsto.index]
    linhas = []
    for campo in CAMPOS:
        if campo not in previsto.columns or campo not in gabarito.columns:
            continue
        acertos = sum(_igual(campo, previsto.at[a, campo], gabarito.at[a, campo]) for a in comuns)
        linhas.append({"campo": campo, "acertos": acertos, "total": len(comuns),
                       "acerto_%": round(100 * acertos / len(comuns), 1) if comuns else 0.0})
    tabela = pd.DataFrame(linhas)
    if not tabela.empty:
        ac, tot = int(tabela["acertos"].sum()), int(tabela["total"].sum())
        tabela.loc[len(tabela)] = {"campo": "TOTAL", "acertos": ac, "total": tot,
                                   "acerto_%": round(100 * ac / tot, 1) if tot else 0.0}
    return tabela


def main() -> None:
    p = argparse.ArgumentParser(description="Acerto da extração contra o gabarito.")
    p.add_argument("--previsto", default="saida/documentos.csv")
    p.add_argument("--gabarito", default="data/sintetico/gabarito/documentos.csv")
    a = p.parse_args()
    tabela = avaliar(pd.read_csv(a.previsto, dtype=str), pd.read_csv(a.gabarito, dtype=str))
    print(tabela.to_string(index=False))


if __name__ == "__main__":
    main()
