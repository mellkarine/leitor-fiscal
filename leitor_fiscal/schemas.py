"""Schemas Pydantic do Leitor Fiscal.

As descrições dos campos funcionam como instruções para o LLM: quanto mais claras,
melhor a extração. Campos ausentes no documento ficam vazios (None), nunca inventados.
"""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    descricao: str = Field(description="Descrição do produto ou serviço, como aparece no documento.")
    quantidade: Optional[float] = Field(default=None, description="Quantidade do item.")
    valor_unitario: Optional[float] = Field(
        default=None, description="Valor unitário em reais, com ponto decimal (ex.: 28.90)."
    )
    valor_item: Optional[float] = Field(
        default=None, description="Valor total do item em reais, com ponto decimal (ex.: 289.00)."
    )


class Documento(BaseModel):
    tipo: Literal["nota_fiscal", "boleto", "recibo"] = Field(
        description="Tipo do documento: nota_fiscal, boleto ou recibo."
    )
    emitente: Optional[str] = Field(
        default=None,
        description=(
            "Quem emitiu ou recebe o dinheiro: fornecedor da nota fiscal, beneficiário "
            "(ou cedente) do boleto, ou quem assina o recibo."
        ),
    )
    doc_emitente: Optional[str] = Field(
        default=None, description="CNPJ ou CPF do emitente, exatamente como escrito, com pontuação."
    )
    numero: Optional[str] = Field(
        default=None,
        description="Número da nota, número do documento do boleto ou número do recibo, sem o símbolo 'Nº'.",
    )
    data: Optional[date] = Field(
        default=None,
        description=(
            "Data de emissão da nota, data do documento do boleto ou data do recibo "
            "(a data do recibo, não a do serviço). Formato AAAA-MM-DD."
        ),
    )
    vencimento: Optional[date] = Field(
        default=None, description="Data de vencimento, só para boletos. Formato AAAA-MM-DD."
    )
    valor_total: Optional[float] = Field(
        default=None,
        description=(
            "Valor total em reais, com ponto decimal (ex.: 448.00). Se o valor aparece em número "
            "e por extenso, use o número; se aparece só por extenso, deixe vazio."
        ),
    )
    destinatario: Optional[str] = Field(
        default=None,
        description="Quem recebe a nota (destinatário), paga o boleto (pagador ou sacado) ou paga o recibo.",
    )
    linha_digitavel: Optional[str] = Field(
        default=None, description="Linha digitável do boleto, como escrita. Vazio para outros tipos."
    )
    itens: list[Item] = Field(
        default_factory=list,
        description="Itens da tabela da nota fiscal. Lista vazia para boleto e recibo.",
    )
