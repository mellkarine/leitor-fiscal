"""Linha de comando: lê uma pasta de PDFs e grava documentos.csv e itens.csv.

Uso:
    python -m leitor_fiscal.cli --pasta data/sintetico/pdfs --saida saida
    python -m leitor_fiscal.cli --demo        # sem API, só para ver o fluxo funcionando
"""
import argparse
from pathlib import Path

from .pipeline import para_dataframes, processar_lote


def processar(pasta: Path, saida: Path, cadeia=None, max_concorrencia: int = 2) -> dict:
    """Extrai e valida todos os PDFs da pasta. Grava os CSVs e devolve as contagens."""
    pdfs = sorted(Path(pasta).glob("*.pdf"))
    if cadeia is None:
        from .extrator import criar_cadeia

        cadeia = criar_cadeia()

    registros = processar_lote([(p.name, p) for p in pdfs], cadeia, max_concorrencia)
    docs, itens = para_dataframes(registros)

    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    docs.to_csv(saida / "documentos.csv", index=False, encoding="utf-8")
    itens.to_csv(saida / "itens.csv", index=False, encoding="utf-8")

    contagem = {s: sum(r.status == s for r in registros) for s in ("ok", "revisar", "erro")}
    return {"pdfs": len(pdfs), **contagem}


def main() -> None:
    parser = argparse.ArgumentParser(description="Leitor Fiscal: PDFs fiscais para planilha.")
    parser.add_argument("--pasta", default="data/sintetico/pdfs", help="Pasta com os PDFs")
    parser.add_argument("--saida", default="saida", help="Pasta para gravar os CSVs")
    parser.add_argument("--concorrencia", type=int, default=2, help="Chamadas simultâneas ao LLM")
    parser.add_argument("--demo", action="store_true", help="Modo demonstração: respostas prontas, sem API")
    args = parser.parse_args()

    cadeia = None
    if args.demo:
        from .demo import cadeia_demo

        cadeia = cadeia_demo()
        print("[modo demonstração] extração simulada; nenhum LLM foi chamado.")

    r = processar(Path(args.pasta), Path(args.saida), cadeia=cadeia, max_concorrencia=args.concorrencia)
    print(f"PDFs: {r['pdfs']} | ok: {r['ok']} | para revisar: {r['revisar']} | erros: {r['erro']}")
    print(f"Resultados em: {args.saida}/")


if __name__ == "__main__":
    main()
