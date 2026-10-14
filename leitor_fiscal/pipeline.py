"""Fluxo completo: PDF -> texto -> LLM -> validação. Usado pela linha de comando e pelo app."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .pdf_texto import extrair_texto
from .schemas import Documento
from .validacao import validar

Entrada = tuple[str, Union[Path, bytes]]


@dataclass
class Registro:
    arquivo: str
    documento: Optional[Documento] = None
    alertas: list[str] = field(default_factory=list)
    erro: Optional[str] = None
    texto: str = ""  # texto lido do PDF, para conferência na interface

    @property
    def status(self) -> str:
        if self.erro:
            return "erro"
        return "revisar" if self.alertas else "ok"


def nomes_unicos(entradas: list[Entrada]) -> list[Entrada]:
    """Dois arquivos com o mesmo nome (de pastas diferentes) viram 'nome.pdf' e 'nome (2).pdf'."""
    vistos: dict[str, int] = {}
    saida: list[Entrada] = []
    for nome, conteudo in entradas:
        vistos[nome] = vistos.get(nome, 0) + 1
        if vistos[nome] > 1:
            caminho = Path(nome)
            nome = f"{caminho.stem} ({vistos[nome]}){caminho.suffix}"
        saida.append((nome, conteudo))
    return saida


def processar_lote(entradas: list[Entrada], cadeia, max_concorrencia: int = 2) -> list[Registro]:
    """Extrai e valida todos os documentos. Erros em um PDF não derrubam o lote."""
    entradas = nomes_unicos(entradas)
    registros: dict[str, Registro] = {}
    para_llm: list[tuple[str, str]] = []

    for nome, conteudo in entradas:
        try:
            texto = extrair_texto(conteudo)
        except Exception:  # PDF corrompido, por exemplo
            registros[nome] = Registro(nome, erro="Não foi possível abrir o arquivo: está corrompido ou não é um PDF válido.")
            continue
        if not texto:
            registros[nome] = Registro(nome, erro="PDF sem texto selecionável (escaneado?). OCR fica para uma versão futura.")
        else:
            para_llm.append((nome, texto))

    textos = dict(para_llm)
    if para_llm:
        # concorrência baixa para respeitar os limites da API gratuita
        resultados = cadeia.batch(
            [{"texto": t} for _, t in para_llm],
            config={"max_concurrency": max_concorrencia},
            return_exceptions=True,
        )
        for (nome, _), res in zip(para_llm, resultados):
            if isinstance(res, Exception):
                registros[nome] = Registro(nome, erro=f"Falha na extração: {res}")
            else:
                registros[nome] = Registro(nome, documento=res, alertas=validar(res), texto=textos[nome])

    return [registros[nome] for nome, _ in entradas]


def para_dataframes(registros: list[Registro]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Converte os registros em duas tabelas: documentos e itens."""
    docs, itens = [], []
    for r in registros:
        base = {"arquivo": r.arquivo}
        if r.documento is not None:
            docs.append({**base, **r.documento.model_dump(exclude={"itens"}),
                         "status": r.status, "alertas": "; ".join(r.alertas)})
            itens.extend({**base, **i.model_dump()} for i in r.documento.itens)
        else:
            docs.append({**base, "status": r.status, "alertas": r.erro or ""})
    return pd.DataFrame(docs), pd.DataFrame(itens)
