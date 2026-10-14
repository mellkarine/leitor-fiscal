"""Validações determinísticas em Python: o LLM extrai, o código confere."""
import re
from dataclasses import dataclass, field
from typing import Optional

from .schemas import Documento

OBRIGATORIOS = {
    "nota_fiscal": ["emitente", "numero", "data", "valor_total"],
    "boleto": ["emitente", "valor_total", "vencimento"],
    "recibo": ["emitente", "data", "valor_total"],
}
ROTULOS = {
    "emitente": "emitente", "numero": "número", "data": "data",
    "valor_total": "valor total", "vencimento": "vencimento",
}


def formatar_brl(valor: Optional[float]) -> str:
    """1234.5 -> 'R$ 1.234,50'."""
    if valor is None:
        return ""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def cnpj_valido(valor: str) -> bool:
    n = _digitos(valor)
    if len(n) != 14 or len(set(n)) == 1:
        return False
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for tamanho in (12, 13):
        soma = sum(int(d) * p for d, p in zip(n[:tamanho], ([6] + pesos) if tamanho == 13 else pesos))
        resto = soma % 11
        dv = 0 if resto < 2 else 11 - resto
        if int(n[tamanho]) != dv:
            return False
    return True


def cpf_valido(valor: str) -> bool:
    n = _digitos(valor)
    if len(n) != 11 or len(set(n)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(d) * p for d, p in zip(n[:tamanho], range(tamanho + 1, 1, -1)))
        dv = (soma * 10) % 11
        dv = 0 if dv == 10 else dv
        if int(n[tamanho]) != dv:
            return False
    return True


@dataclass
class Conferencia:
    """Resultado de uma verificação: sem alertas = passou."""

    rotulo: str
    alertas: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.alertas


def _valor_do_item(item) -> Optional[float]:
    """Valor do item; se faltar o subtotal, usa quantidade x valor unitário."""
    if item.valor_item is not None:
        return item.valor_item
    if None not in (item.quantidade, item.valor_unitario):
        return round(item.quantidade * item.valor_unitario, 2)
    return None


def conferencias(doc: Documento) -> list[Conferencia]:
    """Todas as verificações aplicáveis ao documento, na ordem de exibição (inclui as que passaram)."""
    campos = Conferencia("Campos obrigatórios")
    for campo in OBRIGATORIOS.get(doc.tipo, []):
        if getattr(doc, campo) in (None, ""):
            campos.alertas.append(f"Campo ausente: {ROTULOS[campo]}")

    emitente = Conferencia("CNPJ/CPF do emitente")
    if doc.doc_emitente:
        n = _digitos(doc.doc_emitente)
        if len(n) == 14 and not cnpj_valido(doc.doc_emitente):
            emitente.alertas.append(f"CNPJ do emitente inválido ({doc.doc_emitente})")
        elif len(n) == 11 and not cpf_valido(doc.doc_emitente):
            emitente.alertas.append(f"CPF do emitente inválido ({doc.doc_emitente})")
        elif len(n) not in (11, 14):
            emitente.alertas.append(f"Documento do emitente com tamanho inválido ({doc.doc_emitente})")
    else:
        emitente.alertas.append("CNPJ ou CPF do emitente ausente")

    resultado = [campos, emitente]

    if doc.itens:
        itens = Conferencia("Itens e total")
        valores = [_valor_do_item(i) for i in doc.itens]
        for item, valor in zip(doc.itens, valores):
            if valor is None:
                itens.alertas.append(f"Item '{item.descricao}' sem valor")
        if None not in valores and doc.valor_total is not None:
            soma = round(sum(valores), 2)
            if abs(soma - doc.valor_total) > 0.01:
                itens.alertas.append(
                    f"Total ({formatar_brl(doc.valor_total)}) diverge da soma dos itens ({formatar_brl(soma)})"
                )
        for item in doc.itens:
            if None not in (item.quantidade, item.valor_unitario, item.valor_item):
                if abs(item.quantidade * item.valor_unitario - item.valor_item) > 0.01:
                    itens.alertas.append(f"Item '{item.descricao}': quantidade x valor unitário não bate com o subtotal")
        resultado.append(itens)

    if doc.tipo == "boleto":
        datas = Conferencia("Datas")
        if doc.vencimento and doc.data and doc.vencimento < doc.data:
            datas.alertas.append("Vencimento anterior à data do documento")
        resultado.append(datas)

    return resultado


def validar(doc: Documento) -> list[str]:
    """Devolve a lista de alertas de revisão (vazia se está tudo certo)."""
    return [alerta for conf in conferencias(doc) for alerta in conf.alertas]
