"""Cadeia LCEL: prompt -> LLM (Groq) -> objeto Documento validado pelo Pydantic."""
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from .config import METODO_PADRAO, MODELO_PADRAO
from .schemas import Documento

load_dotenv()

INSTRUCOES = """Você extrai dados de documentos fiscais e financeiros brasileiros \
(nota fiscal, boleto e recibo) a partir do texto de um PDF.

Regras:
- Use somente informações que estão no texto. Se um campo não aparece, deixe-o vazio (null). Nunca invente valores.
- Copie CNPJ, CPF e números exatamente como estão escritos.
- Converta datas para AAAA-MM-DD e valores para número com ponto decimal.
- Boleto: "cedente" é o beneficiário e "sacado" é o pagador.
- Recibo: a data é a do recibo (cidade e data da assinatura), não a data do serviço.
- Nota fiscal: liste todos os itens da tabela em "itens"."""


def criar_cadeia(modelo: str | None = None, metodo: str | None = None):
    """Monta a cadeia de extração. Temperatura 0 para resultados estáveis."""
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Defina GROQ_API_KEY no arquivo .env (veja .env.example).")

    llm = ChatGroq(
        model=modelo or os.getenv("GROQ_MODEL", MODELO_PADRAO),
        temperature=0,
        max_retries=3,
    )
    estruturado = llm.with_structured_output(
        Documento, method=metodo or os.getenv("GROQ_METHOD", METODO_PADRAO)
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", INSTRUCOES), ("human", "Texto do documento:\n\n{texto}")]
    )
    return prompt | estruturado
