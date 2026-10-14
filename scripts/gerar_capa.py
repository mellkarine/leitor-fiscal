"""Gera a capa 1200x627 (roxa, com a marca Melia) com os campos REALMENTE extraídos de um PDF.

Antes, rode a extração:   python -m leitor_fiscal.cli
Depois:                   python scripts/gerar_capa.py            # usa nota_001.pdf
                          python scripts/gerar_capa.py --arquivo nota_002.pdf --tag ""

Os valores da direita vêm de saida/documentos.csv e saida/itens.csv, não de texto fixo.
"""
import argparse
from pathlib import Path

import pandas as pd
import pdfplumber
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
BG, INK, MUTED, ACCENT, LINE = "#F7F3FD", "#1F1535", "#665A80", "#6D28D9", "#DDD0F3"
W, H = 1200, 627
FONTES = {
    True: ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
           "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    False: ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}


def fonte(negrito: bool, tamanho: int):
    for caminho in FONTES[negrito]:
        if Path(caminho).exists():
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()


def valor(v) -> str:
    return "(vazio)" if pd.isna(v) or str(v).strip() == "" else str(v)


def brl(v) -> str:
    if pd.isna(v) or str(v).strip() == "":
        return "(vazio)"
    t = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {t}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo", default="nota_001.pdf")
    ap.add_argument("--pasta-pdfs", default=str(RAIZ / "data" / "sintetico" / "pdfs"))
    ap.add_argument("--saida-csv", default=str(RAIZ / "saida"))
    ap.add_argument("--destino", default=str(RAIZ / "docs" / "imagens" / "00_capa.png"))
    ap.add_argument("--tag", default="Em desenvolvimento", help="Etiqueta no canto; use '' para remover")
    a = ap.parse_args()

    docs = pd.read_csv(Path(a.saida_csv) / "documentos.csv", dtype=str)
    linha = docs[docs["arquivo"] == a.arquivo]
    if linha.empty:
        raise SystemExit(f"{a.arquivo} não está em documentos.csv. Rode antes: python -m leitor_fiscal.cli")
    linha = linha.iloc[0]
    itens_csv = Path(a.saida_csv) / "itens.csv"
    n_itens = 0
    if itens_csv.exists() and itens_csv.stat().st_size > 2:
        n_itens = int((pd.read_csv(itens_csv, dtype=str)["arquivo"] == a.arquivo).sum())

    campos = [("tipo", valor(linha.get("tipo")).replace("_", " ")), ("emitente", valor(linha.get("emitente"))),
              ("cnpj/cpf", valor(linha.get("doc_emitente"))), ("número", valor(linha.get("numero"))),
              ("data", valor(linha.get("data"))), ("valor_total", brl(linha.get("valor_total"))),
              ("itens", f"{n_itens} itens" if n_itens else "(nenhum)")]

    with pdfplumber.open(Path(a.pasta_pdfs) / a.arquivo) as pdf:
        pagina = pdf.pages[0].to_image(resolution=150).original.convert("RGB")
    larg, alt = pagina.size
    pagina = pagina.crop((int(larg * .08), int(alt * .05), int(larg * .93), int(alt * .46)))

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "Leitor Fiscal", font=fonte(True, 56), fill=INK)
    d.text((60, 112), "PDFs de notas, boletos e recibos viram planilha, sem digitação", font=fonte(False, 26), fill=MUTED)
    d.rectangle([60, 156, 120, 160], fill=ACCENT)
    if a.tag:
        ft = fonte(True, 18)
        tw = d.textlength(a.tag, font=ft)
        d.rounded_rectangle([W - 60 - tw - 32, 52, W - 60, 90], radius=19, fill=ACCENT)
        d.text((W - 60 - tw - 16, 60), a.tag, font=ft, fill="white")
    stack = "Python · LangChain · Pydantic · Groq"
    d.text((W - 60 - d.textlength(stack, font=fonte(False, 18)), 102), stack, font=fonte(False, 18), fill=MUTED)

    cw = 420
    pagina = pagina.resize((cw, int(pagina.height * cw / pagina.width)), Image.LANCZOS)
    lx, ly = 60, 190
    sombra = Image.new("RGBA", (cw + 40, pagina.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle([20, 24, cw + 20, pagina.height + 24], fill=(0, 0, 0, 55))
    sombra = sombra.filter(ImageFilter.GaussianBlur(10))
    img.paste(sombra, (lx - 20, ly - 20), sombra)
    d.rectangle([lx, ly, lx + cw, ly + pagina.height], fill="white", outline=LINE)
    img.paste(pagina, (lx, ly))
    d.text((lx, ly + pagina.height + 14), "Entrada: PDF (documento fictício)", font=fonte(False, 19), fill=MUTED)

    ax, cy = lx + cw + 28, ly + pagina.height // 2
    d.line([ax, cy, ax + 70, cy], fill=ACCENT, width=5)
    d.polygon([(ax + 70, cy - 14), (ax + 70, cy + 14), (ax + 94, cy)], fill=ACCENT)
    d.text((ax - 4, cy + 22), "LLM +", font=fonte(True, 17), fill=ACCENT)
    d.text((ax - 4, cy + 42), "Pydantic", font=fonte(True, 17), fill=ACCENT)

    rx, ry, rw, linha_h = 600, 190, 540, 38
    rh = 56 + len(campos) * linha_h
    d.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=12, fill="white", outline=LINE, width=2)
    d.rounded_rectangle([rx, ry, rx + rw, ry + 56], radius=12, fill=ACCENT)
    d.rectangle([rx, ry + 30, rx + rw, ry + 56], fill=ACCENT)
    d.text((rx + 24, ry + 14), "Campos extraídos", font=fonte(True, 24), fill="white")
    y = ry + 56
    for i, (k, v) in enumerate(campos):
        if i:
            d.line([rx + 20, y, rx + rw - 20, y], fill=LINE, width=1)
        d.text((rx + 24, y + 8), k, font=fonte(False, 19), fill=MUTED)
        d.text((rx + 170, y + 8), v, font=fonte(True, 20), fill=INK)
        y += linha_h
    d.text((rx, ry + rh + 14), "Saída: planilha (CSV/Excel), com alerta quando algo não confere", font=fonte(False, 19), fill=MUTED)

    x, y0 = 60, 572
    for i, s in enumerate(["PDF", "Texto", "LLM (Groq)", "Validação", "Planilha"]):
        fw = fonte(True, 19)
        tw = d.textlength(s, font=fw)
        d.rounded_rectangle([x, y0, x + tw + 32, y0 + 38], radius=19, fill="white", outline=ACCENT, width=2)
        d.text((x + 16, y0 + 8), s, font=fw, fill=ACCENT)
        x += tw + 32
        if i < 4:
            d.text((x + 8, y0 + 5), "→", font=fonte(True, 24), fill=MUTED)
            x += 40

    # marca Melia no canto inferior direito
    logo = Image.open(RAIZ / "assets" / "melia-logo.png").convert("RGBA")
    alt_logo = 46
    logo = logo.resize((int(logo.width * alt_logo / logo.height), alt_logo), Image.LANCZOS)
    img.paste(logo, (W - 60 - logo.width, 568), logo)

    destino = Path(a.destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino)
    print(f"Capa gravada em {destino}")


if __name__ == "__main__":
    main()
