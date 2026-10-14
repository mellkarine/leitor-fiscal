"""Modo demonstração: respostas prontas no lugar do LLM, para mostrar a interface sem API.

ATENÇÃO: aqui NÃO há extração real. Os valores são fixos e só valem para os PDFs de exemplo
de data/sintetico/pdfs. O app avisa isso na tela quando este modo está ligado.
"""
from langchain_core.runnables import RunnableLambda

from .schemas import Documento, Item


# (trecho que identifica o PDF no texto, resposta pronta)
RESPOSTAS = [
    ("VENDA Nº 001245", Documento(
        tipo="nota_fiscal", emitente="Distribuidora Aurora de Papéis Ltda", doc_emitente="45.012.367/0001-63",
        numero="001245", data="2026-09-14", valor_total=448.00, destinatario="Padaria Pão Nosso Ltda",
        itens=[Item(descricao="Papel sulfite A4 (resma)", quantidade=10, valor_unitario=28.90, valor_item=289.00),
               Item(descricao="Caneta esferográfica azul", quantidade=50, valor_unitario=1.80, valor_item=90.00),
               Item(descricao="Grampeador de mesa", quantidade=2, valor_unitario=34.50, valor_item=69.00)])),
    ("Nota Fiscal nº 000873", Documento(
        tipo="nota_fiscal", emitente="Comercial Serra Verde Atacado Ltda", doc_emitente="54.021.889/0001-12",
        numero="000873", data="2026-09-15", valor_total=458.00, destinatario="Padaria Pão Nosso Ltda",
        itens=[Item(descricao="Farinha de trigo 25kg", quantidade=4, valor_unitario=92.00, valor_item=368.00),
               Item(descricao="Fermento biológico 500g", quantidade=8, valor_unitario=10.00, valor_item=80.00)])),
    ("Nota Fiscal nº 002310", Documento(
        tipo="nota_fiscal", emitente="Mercado Central Hortifruti Ltda", doc_emitente="92.033.415/0001-81",
        numero="002310", data="2026-09-20", valor_total=321.00, destinatario="Padaria Pão Nosso Ltda",
        itens=[Item(descricao="Açúcar refinado 5kg", quantidade=6, valor_unitario=24.50, valor_item=147.00),
               Item(descricao="Leite integral caixa c/12", quantidade=3, valor_unitario=58.00, valor_item=174.00)])),
    ("20261045", Documento(
        tipo="boleto", emitente="Internet Conecta Telecom Ltda", doc_emitente="33.098.765/0001-65",
        numero="20261045", data="2026-10-01", vencimento="2026-10-10", valor_total=129.90,
        destinatario="Maria Souza Almeida", linha_digitavel="99990.12345 67890.123456 78901.234563 1 94180000012990")),
    ("55012", Documento(
        tipo="boleto", emitente="Academia Corpo Ativo Ltda", doc_emitente="62.011.148/0001-89",
        numero="55012", data="2026-10-03", valor_total=87.50, destinatario="Carlos Eduardo Nunes",
        linha_digitavel="99990.54321 09876.543210 12345.678904 2 94330000008750")),
    ("RECIBO Nº 0032", Documento(
        tipo="recibo", emitente="João da Silva", doc_emitente="529.982.247-25", numero="0032",
        data="2026-09-21", valor_total=350.00, destinatario="Padaria Pão Nosso Ltda")),
    ("RECIBO Nº 0047", Documento(
        tipo="recibo", emitente="Limpeza Total Serviços ME", doc_emitente="11.222.333/0001-81", numero="0047",
        data="2026-09-28", destinatario="Padaria Pão Nosso Ltda")),
]


def _responder(entrada: dict) -> Documento:
    texto = entrada["texto"]
    for trecho, resposta in RESPOSTAS:
        if trecho in texto:
            return resposta.model_copy(deep=True)
    raise ValueError("Modo demonstração: só reconhece os PDFs de exemplo do projeto.")


def cadeia_demo():
    """Mesma interface da cadeia real (usa .batch), mas sem chamar nenhum LLM."""
    return RunnableLambda(_responder)
