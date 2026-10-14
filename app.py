"""Leitor Fiscal by Melia: painel em Streamlit.   Rodar:  streamlit run app.py"""
import io
import os
from pathlib import Path

import altair as alt
import pandas as pd
import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from leitor_fiscal import tema
from leitor_fiscal.avaliar import avaliar
from leitor_fiscal.config import MODELO_PADRAO
from leitor_fiscal.demo import cadeia_demo
from leitor_fiscal.exportar import gerar_excel
from leitor_fiscal.pipeline import nomes_unicos, para_dataframes, processar_lote
from leitor_fiscal.tema import seguro
from leitor_fiscal.validacao import OBRIGATORIOS, conferencias, formatar_brl

load_dotenv()
RAIZ = Path(__file__).parent
PASTA_EXEMPLOS = RAIZ / "data" / "sintetico" / "pdfs"
GABARITO = RAIZ / "data" / "sintetico" / "gabarito" / "documentos.csv"
ROTULO_STATUS = {"ok": "Sem alertas", "revisar": "Revisar", "erro": "Erro"}
CAMPO_ROTULO = {"emitente": "Emitente", "numero": "Número", "data": "Data", "valor_total": "Valor total",
                "vencimento": "Vencimento"}

st.set_page_config(
    page_title="Leitor Fiscal · Melia",
    page_icon=Image.open(RAIZ / "assets" / "melia-icon.png"),
    layout="wide",
)
tema.aplicar()

# ---------------- barra lateral: só configurações ----------------
with st.sidebar:
    st.markdown(tema.logo_lateral(), unsafe_allow_html=True)
    st.markdown("<div class='lf-side-sub'>Leitor Fiscal</div>", unsafe_allow_html=True)

    st.markdown("<div class='lf-side-sec'>Extração</div>", unsafe_allow_html=True)
    tem_chave = bool(os.getenv("GROQ_API_KEY"))
    demo = st.toggle(
        "Modo demonstração",
        value=(not tem_chave) or os.getenv("LEITOR_FISCAL_DEMO") == "1",
        help="Usa respostas prontas, sem chamar o LLM. Só funciona com os PDFs de exemplo.",
    )
    modelo = st.text_input("Modelo do Groq", os.getenv("GROQ_MODEL", MODELO_PADRAO), disabled=demo)
    if not demo and not tem_chave:
        st.caption("Defina a GROQ_API_KEY no arquivo .env para extrair de verdade.")

    st.markdown(
        "<div class='lf-side-rodape'><b>Melia</b><br>Os documentos de exemplo são fictícios.</div>",
        unsafe_allow_html=True,
    )

# ---------------- topo ----------------
chip = tema.chip("Modo demonstração" if demo else f"Groq · {modelo}", demo)
col_tit, col_chip = st.columns([4, 1], vertical_alignment="bottom")
col_tit.markdown("<p class='lf-eyebrow'>Melia · auditoria de documentos</p><h1 class='lf-titulo'>Leitor Fiscal</h1>",
                 unsafe_allow_html=True)
subtitulo = col_tit.empty()  # preenchido no fim, com o estado do lote
col_chip.markdown(f"<div style='text-align:right'>{chip}</div>", unsafe_allow_html=True)
if demo:
    st.markdown(tema.aviso("<b>Modo demonstração:</b> resultados simulados para os PDFs de exemplo, sem chamar o LLM."),
                unsafe_allow_html=True)


@st.cache_data(show_spinner=False, max_entries=500)
def inspecionar_pdf(conteudo: bytes) -> tuple[int | None, bool | None]:
    """Páginas e se há texto selecionável (olha as 3 primeiras páginas). None se o arquivo não abre."""
    try:
        with pdfplumber.open(io.BytesIO(conteudo)) as pdf:
            tem_texto = any((pg.extract_text() or "").strip() for pg in pdf.pages[:3])
            return len(pdf.pages), tem_texto
    except Exception:
        return None, None


def tamanho(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def area_de_envio() -> tuple[list[tuple[str, bytes | Path]], bool]:
    """Envio dos PDFs, fila do lote e botão de processar. Devolve (entradas, clicou)."""
    enviados = st.file_uploader("PDFs", type="pdf", accept_multiple_files=True,
                                label_visibility="collapsed", key="uploads")
    usar_exemplos = st.checkbox("Usar os documentos de exemplo", value=True, key="exemplos",
                                disabled=bool(enviados),
                                help="Notas, boletos e recibos fictícios que acompanham o projeto.")

    entradas: list[tuple[str, bytes | Path]] = []
    if enviados:
        entradas = [(f.name, f.getvalue()) for f in enviados]
    elif usar_exemplos:
        entradas = [(p.name, p) for p in sorted(PASTA_EXEMPLOS.glob("*.pdf"))]
    entradas = nomes_unicos(entradas)

    if not entradas:
        st.markdown("<div class='lf-fila-vazia'>Nenhum documento na fila. Envie PDFs acima.</div>",
                    unsafe_allow_html=True)
        return entradas, False

    linhas = []
    prontos = 0
    for nome, conteudo in entradas:
        dados = conteudo if isinstance(conteudo, bytes) else Path(conteudo).read_bytes()
        paginas, tem_texto = inspecionar_pdf(dados)
        if paginas is None:
            situacao = tema.pill("Arquivo ilegível", "lf-erro", "erro")
        elif tem_texto:
            situacao = tema.pill("Pronto", "lf-ok", "check")
            prontos += 1
        else:
            situacao = tema.pill("Sem texto (escaneado)", "lf-rev", "alerta")
        linhas.append({"Arquivo": nome, "Páginas": "—" if paginas is None else str(paginas),
                       "Tamanho": tamanho(len(dados)), "Situação": situacao})
    fila = pd.DataFrame(linhas)

    st.markdown(tema.tabela(fila, html_cols={"Situação"}, num_cols={"Páginas", "Tamanho"}, forte_cols={"Arquivo"}, altura=320),
                unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    resumo = f"{len(fila)} documento(s) na fila · {prontos} pronto(s)"
    if prontos < len(fila):
        resumo += f" · {len(fila) - prontos} sem texto ou ilegível(is), vão aparecer como erro"
    c1.caption(resumo)
    clicou = c2.button("Processar documentos", type="primary", width="stretch")
    return entradas, clicou


registros = st.session_state.get("registros")

# ---------------- lote ----------------
if registros:
    with st.expander("Novo lote", expanded=False):
        entradas, processar = area_de_envio()
else:
    with st.container(border=True, key="card_lote"):
        st.markdown("<p class='lf-card-tit'>Novo lote</p>"
                    "<p class='lf-card-leg'>Notas fiscais, boletos e recibos em PDF com texto selecionável.</p>",
                    unsafe_allow_html=True)
        entradas, processar = area_de_envio()
assinatura = tuple(nome for nome, _ in entradas)

if processar and entradas:
    try:
        if demo:
            cadeia = cadeia_demo()
        else:
            from leitor_fiscal.extrator import criar_cadeia

            cadeia = criar_cadeia(modelo=modelo)
        with st.spinner(f"Processando {len(entradas)} documento(s)..."):
            st.session_state["registros"] = processar_lote(entradas, cadeia)
            st.session_state["demo_usado"] = demo
            st.session_state["assinatura"] = assinatura
        st.rerun()  # redesenha a tela já no modo de resultados
    except Exception as exc:
        st.error(f"Não foi possível processar: {exc}")

if not registros:
    subtitulo.markdown("<div class='lf-sub'>Nenhum lote processado ainda.</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- dados ----------------
docs, itens = para_dataframes(registros)
n_ok = sum(r.status == "ok" for r in registros)
n_rev = sum(r.status == "revisar" for r in registros)
n_erro = sum(r.status == "erro" for r in registros)


def col(nome: str) -> pd.Series:
    """Coluna da tabela de documentos, ou vazia se nenhum documento foi extraído."""
    return docs[nome] if nome in docs.columns else pd.Series([None] * len(docs), dtype=object)


valores = pd.to_numeric(col("valor_total"), errors="coerce")
tipos = col("tipo").fillna("").astype(str).str.replace("_", " ")
pct_conferido = round(100 * n_ok / len(registros)) if registros else 0
subtitulo.markdown(
    f"<div class='lf-sub'>Último lote: <b>{len(registros)}</b> documento(s) · <b>{n_ok}</b> sem alertas · "
    f"<b>{n_rev}</b> para revisão · <b>{n_erro}</b> com erro</div>",
    unsafe_allow_html=True,
)

if st.session_state.get("assinatura") != assinatura:
    st.info("A fila mudou desde o último processamento. Abra “Novo lote” e clique em “Processar documentos” para atualizar.")

mostrar_acerto = (
    not st.session_state.get("demo_usado") and GABARITO.exists()
    and bool(set(docs["arquivo"]) & set(pd.read_csv(GABARITO, dtype=str)["arquivo"]))
)
abas = st.tabs(["Visão geral", "Documentos", "Exportar"] + (["Acerto"] if mostrar_acerto else []))

# ---------------- visão geral ----------------
with abas[0]:
    cartoes = [
        ("Documentos lidos", len(registros), "no último lote", tema.ROXO_VIVO, "pilha"),
        ("Sem alertas", n_ok, "prontos para exportar", tema.ROXO, "check"),
        ("Para revisão", n_rev, "conferir antes", tema.LILAS, "alerta"),
        ("Erros", n_erro, "falha na leitura", tema.ROXO_ESCURO, "erro"),
    ]
    total = formatar_brl(valores.sum()) if valores.notna().any() else "—"
    st.markdown(tema.kpis(total, len(registros), pct_conferido, cartoes), unsafe_allow_html=True)

    esq, dir_ = st.columns([3, 2], gap="medium")
    with esq:
        with st.container(border=True, key="card_fila"):
            st.markdown("<p class='lf-card-tit'>Fila de revisão</p>"
                        "<p class='lf-card-leg'>Documentos que precisam de conferência humana antes de exportar.</p>",
                        unsafe_allow_html=True)
            itens_fila = [
                tema.item_fila(r.arquivo, r.documento.tipo if r.documento else None, r.status,
                               r.alertas if r.alertas else [r.erro or ""])
                for r in registros if r.status != "ok"
            ]
            st.markdown(tema.fila_revisao(itens_fila), unsafe_allow_html=True)
    with dir_:
        with st.container(border=True, key="card_situacao"):
            st.markdown("<p class='lf-card-tit'>Situação dos documentos</p>"
                        "<p class='lf-card-leg'>Quanto já está conferido.</p>", unsafe_allow_html=True)
            dados = pd.DataFrame({"Situação": ["Sem alertas", "Para revisão", "Erros"], "Qtd": [n_ok, n_rev, n_erro]})
            dados = dados[dados["Qtd"] > 0]
            cores = {"Sem alertas": tema.ROXO, "Para revisão": tema.LILAS, "Erros": tema.ROXO_ESCURO}
            cores = {k: v for k, v in cores.items() if k in set(dados["Situação"])}
            arco = alt.Chart(dados).mark_arc(innerRadius=70, outerRadius=104, cornerRadius=6, padAngle=0.025).encode(
                theta=alt.Theta("Qtd:Q", stack=True),
                color=alt.Color("Situação:N", scale=alt.Scale(domain=list(cores), range=list(cores.values())),
                                legend=alt.Legend(orient="bottom", title=None)),
                tooltip=["Situação", "Qtd"],
            )
            centro = alt.Chart(pd.DataFrame({"t": [f"{pct_conferido}%"]})).mark_text(
                size=30, font="Lora, Georgia, serif", fontWeight=600, color=tema.ROXO_ESCURO, dy=-6).encode(text="t:N")
            legenda = alt.Chart(pd.DataFrame({"t": ["sem alertas"]})).mark_text(
                size=11.5, color=tema.MUDO, dy=18).encode(text="t:N")
            st.altair_chart((arco + centro + legenda).properties(height=260), width="stretch", theme=None)

    g1, g2 = st.columns([5, 4], gap="medium")
    por_tipo = (pd.DataFrame({"Tipo": tipos, "Valor": valores}).query("Tipo != ''")
                .groupby("Tipo", as_index=False)["Valor"].sum())
    with g1:
        with st.container(border=True, key="card_tipo"):
            st.markdown("<p class='lf-card-tit'>Valor por tipo de documento</p>"
                        "<p class='lf-card-leg'>Soma dos totais extraídos, em reais.</p>", unsafe_allow_html=True)
            if por_tipo.empty:
                st.caption("Sem valores extraídos.")
            else:
                st.altair_chart(
                    alt.Chart(por_tipo).mark_bar(size=20, cornerRadiusEnd=8, cornerRadiusTopLeft=3, cornerRadiusBottomLeft=3,
                                                 color=tema.gradiente(tema.LILAS, tema.ROXO)).encode(
                        y=alt.Y("Tipo:N", sort="-x", title=None),
                        x=alt.X("Valor:Q", title="R$", axis=alt.Axis(format=",.0f", tickCount=5)),
                        tooltip=["Tipo", alt.Tooltip("Valor:Q", format=",.2f")],
                    ).properties(height=alt.Step(42)), width="stretch", theme=None)
    with g2:
        with st.container(border=True, key="card_emitentes"):
            st.markdown("<p class='lf-card-tit'>Maiores emitentes</p>"
                        "<p class='lf-card-leg'>Quem mais aparece em valor nos documentos lidos.</p>", unsafe_allow_html=True)
            por_emitente = (pd.DataFrame({"Emitente": col("emitente"), "Valor": valores}).dropna()
                            .groupby("Emitente", as_index=False)["Valor"].sum().nlargest(6, "Valor"))
            if por_emitente.empty:
                st.caption("Sem valores extraídos.")
            else:
                st.altair_chart(
                    alt.Chart(por_emitente).mark_bar(size=20, cornerRadiusEnd=8, cornerRadiusTopLeft=3, cornerRadiusBottomLeft=3,
                                                     color=tema.gradiente(tema.LAVANDA, tema.ROXO_VIVO)).encode(
                        y=alt.Y("Emitente:N", sort="-x", title=None, axis=alt.Axis(labelLimit=170, labelOverlap=False)),
                        x=alt.X("Valor:Q", title="R$", axis=alt.Axis(format=",.0f", tickCount=4)),
                        tooltip=["Emitente", alt.Tooltip("Valor:Q", format=",.2f")],
                    ).properties(height=alt.Step(42)), width="stretch", theme=None)

# ---------------- documentos ----------------
with abas[1]:
    f1, f2, f3 = st.columns([3, 4, 3])
    busca = f1.text_input("Buscar", placeholder="Buscar arquivo, emitente ou nº", label_visibility="collapsed")
    situacao = f2.segmented_control(
        "Situação", ["Todos", "Sem alertas", "Revisar", "Erro"], default="Todos", label_visibility="collapsed"
    ) or "Todos"
    tipos_escolhidos = f3.multiselect(
        "Tipo", sorted(t for t in tipos.unique() if t), placeholder="Todos os tipos", label_visibility="collapsed"
    )

    exibir = pd.DataFrame({
        "Arquivo": docs["arquivo"],
        "Tipo": tipos,
        "Emitente": col("emitente").fillna(""),
        "Número": col("numero").fillna(""),
        "Data": pd.to_datetime(col("data"), errors="coerce").dt.strftime("%d/%m/%Y").fillna(""),
        "Vencimento": pd.to_datetime(col("vencimento"), errors="coerce").dt.strftime("%d/%m/%Y").fillna(""),
        "Valor total": valores.map(lambda v: "" if pd.isna(v) else formatar_brl(v)),
        "Alertas": [len(r.alertas) for r in registros],
        "Status": docs["status"].map(ROTULO_STATUS),
    })
    mascara = pd.Series(True, index=exibir.index)
    if busca:
        alvo = (exibir["Arquivo"] + " " + exibir["Emitente"] + " " + exibir["Número"]).str.casefold()
        mascara &= alvo.str.contains(busca.strip().casefold(), regex=False)
    if situacao != "Todos":
        mascara &= exibir["Status"] == situacao
    if tipos_escolhidos:
        mascara &= exibir["Tipo"].isin(tipos_escolhidos)
    filtrado = exibir[mascara].copy()

    traco = "<span class='lf-traco'>—</span>"
    filtrado["Tipo"] = filtrado["Tipo"].map(lambda t: tema.pill_tipo(t) if t else traco)
    filtrado["Alertas"] = filtrado["Alertas"].map(lambda n: f"<span class='lf-contagem'>{n}</span>" if n else traco)
    filtrado["Status"] = docs.loc[filtrado.index, "status"].map(tema.pill_status)
    for nome in ("Emitente", "Número", "Data", "Vencimento", "Valor total"):
        filtrado[nome] = filtrado[nome].map(lambda v: seguro(v) if v else traco)

    st.caption(f"{len(filtrado)} de {len(exibir)} documento(s)")
    st.markdown(tema.tabela(filtrado, html_cols=set(filtrado.columns) - {"Arquivo"}, num_cols={"Valor total", "Alertas"},
                            forte_cols={"Arquivo", "Valor total"}, fraco_cols={"Número", "Vencimento"}),
                unsafe_allow_html=True)

    st.markdown("### Detalhe do documento")
    escolhido = st.selectbox("Documento", [r.arquivo for r in registros], label_visibility="collapsed")
    reg = next(r for r in registros if r.arquivo == escolhido)
    tipo_html = tema.pill_tipo(reg.documento.tipo) if reg.documento else ""
    st.markdown(
        f"<div class='lf-det-topo'><span class='lf-det-nome'>{seguro(reg.arquivo)}</span>{tipo_html}"
        f"{tema.pill_status(reg.status)}</div>", unsafe_allow_html=True)
    if reg.erro:
        st.error(reg.erro)
    if reg.documento:
        d = reg.documento
        campos = {
            "Tipo": d.tipo.replace("_", " "), "Emitente": d.emitente, "CNPJ/CPF do emitente": d.doc_emitente,
            "Número": d.numero, "Data": d.data.strftime("%d/%m/%Y") if d.data else None,
            "Vencimento": d.vencimento.strftime("%d/%m/%Y") if d.vencimento else None,
            "Valor total": formatar_brl(d.valor_total) if d.valor_total is not None else None,
            "Destinatário/pagador": d.destinatario,
            "Linha digitável": d.linha_digitavel,
        }
        if d.tipo != "boleto":
            campos.pop("Linha digitável")
            campos.pop("Vencimento")
        # liga cada campo às conferências que o usaram (rastreabilidade da auditoria)
        confs = conferencias(d)
        usa = {
            "Campos obrigatórios": [CAMPO_ROTULO[c] for c in OBRIGATORIOS.get(d.tipo, [])],
            "CNPJ/CPF do emitente": ["CNPJ/CPF do emitente"],
            "Itens e total": ["Valor total"],
            "Datas": ["Data", "Vencimento"],
        }
        refs: dict[str, list[int]] = {}
        for n, conf in enumerate(confs, 1):
            for campo in usa.get(conf.rotulo, []):
                if campo in campos:
                    refs.setdefault(campo, []).append(n)
        st.markdown(tema.auditoria(campos, refs, confs, reg.status), unsafe_allow_html=True)

        if d.itens:
            st.markdown("<p class='lf-card-tit'>Itens</p>", unsafe_allow_html=True)
            st.markdown(tema.tabela(pd.DataFrame([{
                "Descrição": i.descricao, "Qtd": "" if i.quantidade is None else f"{i.quantidade:g}",
                "Valor unit.": formatar_brl(i.valor_unitario), "Valor": formatar_brl(i.valor_item)} for i in d.itens]),
                num_cols={"Qtd", "Valor unit.", "Valor"}, forte_cols={"Valor"}, altura=320), unsafe_allow_html=True)
    if reg.texto:
        with st.expander("Ver o texto lido do PDF"):
            st.code(reg.texto, language=None)

# ---------------- exportar ----------------
with abas[2], st.container(border=True, key="card_exportar"):
    st.markdown("<p class='lf-card-tit'>Exportar resultados</p>"
                "<p class='lf-card-leg'>O Excel já vem formatado, com datas e valores de verdade. "
                "As abas são: documentos, itens e resumo.</p>", unsafe_allow_html=True)
    if n_rev or n_erro:
        st.markdown(tema.aviso(f"<b>{n_rev + n_erro} documento(s)</b> estão com status Revisar ou Erro e saem assim na planilha."),
                    unsafe_allow_html=True)
    b1, b2, b3, _ = st.columns([1.2, 1.8, 1.5, 2])
    b1.download_button("Baixar Excel", gerar_excel(docs, itens), "leitor_fiscal.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", width="stretch")
    b2.download_button("CSV dos documentos", docs.to_csv(index=False).encode("utf-8"), "documentos.csv", "text/csv",
                       width="stretch")
    b3.download_button("CSV dos itens", itens.to_csv(index=False).encode("utf-8"), "itens.csv", "text/csv",
                       width="stretch", disabled=itens.empty)

# ---------------- acerto (só com extração real) ----------------
if mostrar_acerto:
    with abas[3]:
        st.markdown("### Acerto contra o gabarito")
        st.caption("Compara campo a campo o que o modelo extraiu com o gabarito dos documentos de teste.")
        tabela = avaliar(docs.where(docs.notna(), "").astype(str), pd.read_csv(GABARITO, dtype=str))
        st.dataframe(
            tabela, hide_index=True, width="stretch",
            column_config={"acerto_%": st.column_config.ProgressColumn("acerto_%", min_value=0, max_value=100, format="%.1f%%")},
        )
