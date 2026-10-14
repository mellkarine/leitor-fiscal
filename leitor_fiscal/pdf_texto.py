"""Extração de texto de PDFs com texto selecionável (PDFs escaneados ficam fora do MVP)."""
import io
from pathlib import Path
from typing import BinaryIO, Union

import pdfplumber

Fonte = Union[Path, str, bytes, BinaryIO]


def extrair_texto(fonte: Fonte) -> str:
    """Devolve o texto do PDF, página por página. Retorna string vazia se não houver texto.

    Aceita um caminho, bytes ou um arquivo aberto (como os uploads do Streamlit).
    """
    if isinstance(fonte, bytes):
        fonte = io.BytesIO(fonte)
    with pdfplumber.open(fonte) as pdf:
        paginas = [(pagina.extract_text() or "").strip() for pagina in pdf.pages]
    return "\n\n".join(f"[página {i}]\n{texto}" for i, texto in enumerate(paginas, start=1) if texto)
