"""Identidade visual da Melia e componentes HTML do painel."""
import base64
import html
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# ---------- paleta ----------
AMEIXA = "#1C0B3F"
ROXO_ESCURO = "#2E1065"
ROXO_PROFUNDO = "#4C1D95"
ROXO = "#5B21B6"
ROXO_VIVO = "#7C3AED"
LILAS = "#A78BFA"
LAVANDA = "#DDD3F7"
ROXO_CLARO = "#F3EEFC"
TEXTO = "#1E1433"
MUDO = "#685C80"
BORDA = "#E4DCF3"
# acentos de status (só em etiquetas e ícones; gráficos e indicadores ficam em roxo)
TEAL = "#2F7A6B"
TERRACOTA = "#B5562F"
VINHO = "#A3253F"

SERIFA = "'Lora', Georgia, 'Times New Roman', serif"
SANS = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"

ESTILOS_STATUS = {
    "ok": ("Sem alertas", "lf-ok", "check"),
    "revisar": ("Revisar", "lf-rev", "alerta"),
    "erro": ("Erro", "lf-erro", "erro"),
}

# ícones de traço fino (viewBox 24x24)
ICONES = {
    "check": '<path d="M5 12.5l4.2 4.2L19 7"/>',
    "alerta": '<path d="M12 4 2.8 19.5h18.4z"/><path d="M12 10v4"/><path d="M12 17h.01"/>',
    "erro": '<circle cx="12" cy="12" r="8.5"/><path d="m9.2 9.2 5.6 5.6M14.8 9.2l-5.6 5.6"/>',
    "arquivo": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
    "pilha": '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
    "moedas": '<ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v5c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/>'
              '<path d="M9 15v2c0 1.7 2.7 3 6 3s6-1.3 6-3v-5c0-1.6-2.4-2.9-5.5-3"/>',
    "escudo": '<path d="M12 3 5 6v5c0 4.4 3 8.3 7 10 4-1.7 7-5.6 7-10V6z"/><path d="m9 12 2 2 4-4"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "faisca": '<path d="M12 3.5 13.8 10 20.5 12l-6.7 2L12 20.5 10.2 14 3.5 12l6.7-2z"/>',
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}


def icone(nome: str, tam: int = 16, traco: float = 1.6) -> str:
    return (f'<svg class="lf-svg" width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{traco}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONES[nome]}</svg>')


# ---------- gráficos ----------
@alt.theme.register("melia", enable=True)
def tema_graficos() -> alt.theme.ThemeConfig:
    """Tema do Altair com a paleta do painel. Use st.altair_chart(..., theme=None) para ele valer."""
    return {
        "config": {
            "background": "transparent",
            "font": "Inter, system-ui, sans-serif",
            "view": {"stroke": None},
            "range": {"category": [ROXO, LILAS, ROXO_ESCURO, ROXO_VIVO, LAVANDA, ROXO_PROFUNDO]},
            "mark": {"color": ROXO},
            "bar": {"color": ROXO},
            "arc": {"stroke": "#FFFFFF", "strokeWidth": 2},
            "text": {"color": ROXO_ESCURO, "font": "Inter, system-ui, sans-serif"},
            "axis": {"labelColor": MUDO, "titleColor": MUDO, "labelFontSize": 12, "titleFontSize": 11.5,
                     "titleFontWeight": 500, "labelPadding": 8, "gridColor": BORDA, "gridDash": [2, 4],
                     "domain": False, "ticks": False},
            "axisY": {"grid": False, "labelColor": TEXTO, "labelFontWeight": 500},
            "legend": {"labelColor": TEXTO, "titleColor": ROXO_ESCURO, "labelFontSize": 12.5,
                       "symbolType": "circle", "symbolSize": 90, "columnPadding": 14},
        }
    }


def gradiente(claro: str = LILAS, escuro: str = ROXO) -> alt.Gradient:
    """Gradiente horizontal suave para barras (do claro, na base, ao escuro, na ponta)."""
    return alt.Gradient(gradient="linear", x1=0, x2=1, y1=0, y2=0,
                        stops=[alt.GradientStop(color=claro, offset=0), alt.GradientStop(color=escuro, offset=1)])


# ---------- CSS ----------
_VARS = (
    f"--ameixa:{AMEIXA};--escuro:{ROXO_ESCURO};--profundo:{ROXO_PROFUNDO};--roxo:{ROXO};--vivo:{ROXO_VIVO};"
    f"--lilas:{LILAS};--lavanda:{LAVANDA};--claro:{ROXO_CLARO};--texto:{TEXTO};--mudo:{MUDO};--borda:{BORDA};"
    f"--teal:{TEAL};--teal-bg:#E4F1EC;--terra:{TERRACOTA};--terra-bg:#FBEEE6;--vinho:{VINHO};--vinho-bg:#FBE8EC;"
    f"--serifa:{SERIFA};--sans:{SANS};"
    "--vidro:rgba(255,255,255,.66);--vidro-borda:rgba(124,58,237,.11);"
    "--sombra:0 1px 0 rgba(255,255,255,.85) inset,0 18px 40px -22px rgba(46,16,101,.20),0 2px 8px -4px rgba(46,16,101,.07);"
    "--sombra-alta:0 1px 0 rgba(255,255,255,.9) inset,0 26px 48px -24px rgba(46,16,101,.28),0 4px 12px -6px rgba(46,16,101,.10);"
    "--suave:cubic-bezier(.2,.7,.2,1);"
)

_REGRAS = """
/* ---------- base ---------- */
html,body,[data-testid="stAppViewContainer"],button,input,textarea,select{font-family:var(--sans);}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(900px 520px at 88% -8%,rgba(167,139,250,.22),transparent 62%),
    radial-gradient(760px 480px at -6% 32%,rgba(221,211,247,.55),transparent 60%),
    radial-gradient(640px 420px at 70% 108%,rgba(124,58,237,.08),transparent 60%),
    #F7F4FC;
  background-attachment:fixed;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.4rem;padding-bottom:3rem;max-width:1280px;}
h1,h2,h3,h4{font-family:var(--serifa);color:var(--escuro);letter-spacing:-.015em;font-weight:600;}
h3{font-size:1.35rem !important;}
p,li,label{line-height:1.55;}
.lf-svg{flex:none;display:inline-block;vertical-align:-3px;}

/* ---------- barra lateral ---------- */
section[data-testid="stSidebar"]{border-right:0;background:linear-gradient(180deg,#2A0F5E 0%,#1C0B3F 100%);}
section[data-testid="stSidebar"] > div{background:transparent;}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"]{display:none;}
section[data-testid="stSidebar"] .block-container,section[data-testid="stSidebarUserContent"]{padding-top:1.4rem;}
.lf-side-logo{display:block;height:36px;margin:10px 0 6px 0;}
.lf-side-sub{font-family:var(--serifa);color:#D9CCF5;font-size:15px;letter-spacing:.01em;margin-bottom:20px;}
.lf-side-sec{margin:24px 0 8px;font-size:10.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#A893DE;}
.lf-side-rodape{margin-top:30px;padding-top:14px;border-top:1px solid rgba(255,255,255,.10);color:#BFB0E6;font-size:12px;line-height:1.6;}
.lf-side-rodape b{color:#fff;font-family:var(--serifa);font-weight:600;font-size:13px;}

/* ---------- topo ---------- */
.lf-eyebrow{font-size:11px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--vivo);margin:0 0 6px;}
.lf-titulo{font-family:var(--serifa);font-size:2.5rem;font-weight:600;color:var(--escuro);letter-spacing:-.025em;line-height:1.05;margin:0;padding:0 !important;}
.lf-sub{color:var(--mudo);font-size:14px;margin:8px 0 4px;}
.lf-sub b{color:var(--texto);font-weight:600;}
.lf-chip{display:inline-flex;align-items:center;gap:7px;padding:7px 14px;border-radius:999px;font-size:12.5px;font-weight:600;
  background:var(--vidro);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border:1px solid var(--vidro-borda);box-shadow:var(--sombra);}
.lf-chip-demo{color:var(--terra);}
.lf-chip-real{color:var(--teal);}
.lf-aviso{display:flex;align-items:center;gap:10px;background:linear-gradient(90deg,var(--terra-bg),rgba(251,238,230,.35));
  border:1px solid rgba(181,86,47,.16);border-radius:14px;padding:10px 16px;color:#7A3519;font-size:13.5px;margin:6px 0 18px;}
.lf-aviso .lf-svg{color:var(--terra);}

/* ---------- cartões de vidro (containers com key card_*) ---------- */
div[class*="st-key-card_"]{background:var(--vidro) !important;backdrop-filter:blur(16px) saturate(150%);-webkit-backdrop-filter:blur(16px) saturate(150%);
  border:1px solid var(--vidro-borda) !important;border-radius:20px !important;box-shadow:var(--sombra);padding:20px 22px !important;
  transition:box-shadow .35s var(--suave),transform .35s var(--suave);}
div[class*="st-key-card_"]:hover{box-shadow:var(--sombra-alta);}
div[data-testid="stMarkdownContainer"] p.lf-card-tit{font-family:var(--serifa);font-weight:600;color:var(--escuro);font-size:18px !important;letter-spacing:-.01em;margin:0 0 2px;}
div[data-testid="stMarkdownContainer"] p.lf-card-leg{color:var(--mudo);font-size:13px !important;margin:0 0 14px;}

/* ---------- indicadores (assimétricos: destaque + grade 2x2) ---------- */
.lf-kpis{display:grid;grid-template-columns:minmax(0,1.45fr) repeat(2,minmax(0,1fr));grid-auto-rows:minmax(118px,auto);gap:16px;margin:6px 0 22px;}
.lf-hero{grid-row:span 2;position:relative;overflow:hidden;border-radius:24px;padding:24px 26px;color:#fff;
  background:radial-gradient(420px 260px at 100% 0%,rgba(167,139,250,.45),transparent 65%),linear-gradient(140deg,#4C1D95 0%,#2E1065 55%,#1C0B3F 100%);
  box-shadow:0 30px 60px -30px rgba(46,16,101,.65),0 1px 0 rgba(255,255,255,.12) inset;display:flex;flex-direction:column;
  transition:transform .35s var(--suave),box-shadow .35s var(--suave);}
.lf-hero:hover{transform:translateY(-2px);box-shadow:0 36px 64px -30px rgba(46,16,101,.75),0 1px 0 rgba(255,255,255,.12) inset;}
.lf-hero::after{content:"";position:absolute;right:-60px;bottom:-60px;width:220px;height:220px;border-radius:50%;border:1px solid rgba(255,255,255,.10);
  box-shadow:0 0 0 28px rgba(255,255,255,.03),0 0 0 56px rgba(255,255,255,.02);}
.lf-hero-rot{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#D9CCF5;}
.lf-hero-val{font-family:var(--serifa);font-size:clamp(2rem,3.4vw,2.8rem);font-weight:600;letter-spacing:-.02em;line-height:1.1;margin:14px 0 4px;
  font-variant-numeric:lining-nums tabular-nums;white-space:nowrap;}
.lf-hero-nota{color:#CBBDF0;font-size:13px;}
.lf-hero-rodape{margin-top:auto;padding-top:22px;}
.lf-barra{height:6px;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden;}
.lf-barra span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#C4B5FD,#fff);}
.lf-hero-leg{display:flex;justify-content:space-between;font-size:12.5px;color:#D9CCF5;margin-top:8px;}
.lf-hero-leg b{color:#fff;font-weight:600;}

.lf-kpi{position:relative;border-radius:20px;padding:18px 20px 16px;background:var(--vidro);backdrop-filter:blur(16px) saturate(150%);
  -webkit-backdrop-filter:blur(16px) saturate(150%);border:1px solid var(--vidro-borda);box-shadow:var(--sombra);
  transition:transform .3s var(--suave),box-shadow .3s var(--suave),border-color .3s var(--suave);}
.lf-kpi:hover{transform:translateY(-2px);box-shadow:var(--sombra-alta);border-color:rgba(124,58,237,.2);}
.lf-kpi-topo{display:flex;align-items:center;justify-content:space-between;gap:8px;}
.lf-kpi-rot{color:var(--mudo);font-size:12.5px;font-weight:500;}
.lf-kpi-ico{width:30px;height:30px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--cor);
  background:color-mix(in srgb,var(--cor) 11%,white);border:1px solid color-mix(in srgb,var(--cor) 16%,transparent);}
.lf-kpi-val{font-family:var(--serifa);color:var(--escuro);font-size:2rem;font-weight:600;letter-spacing:-.02em;line-height:1.15;margin-top:8px;
  font-variant-numeric:lining-nums tabular-nums;}
.lf-kpi-nota{display:flex;align-items:center;gap:6px;color:var(--mudo);font-size:12.5px;margin-top:2px;}
.lf-kpi-nota::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--cor);opacity:.85;}
@media (max-width:900px){.lf-kpis{grid-template-columns:repeat(2,minmax(0,1fr));}.lf-hero{grid-column:1 / -1;grid-row:auto;}}

/* ---------- etiquetas ---------- */
.lf-pill{display:inline-flex;align-items:center;gap:5px;padding:3px 10px 3px 8px;border-radius:999px;font-size:11.5px;font-weight:600;
  letter-spacing:.01em;white-space:nowrap;border:1px solid transparent;line-height:1.5;}
.lf-pill .lf-svg{vertical-align:0;}
.lf-ok{background:var(--teal-bg);color:var(--teal);border-color:rgba(47,122,107,.18);}
.lf-rev{background:var(--terra-bg);color:var(--terra);border-color:rgba(181,86,47,.18);}
.lf-erro{background:var(--vinho-bg);color:var(--vinho);border-color:rgba(163,37,63,.18);}
.lf-tipo{background:rgba(243,238,252,.9);color:var(--roxo);border-color:rgba(91,33,182,.14);text-transform:capitalize;padding-left:10px;}
.lf-tipo::before{content:"";width:5px;height:5px;border-radius:50%;background:currentColor;opacity:.7;}
.lf-contagem{display:inline-flex;min-width:22px;height:22px;padding:0 7px;align-items:center;justify-content:center;border-radius:999px;
  font-size:11.5px;font-weight:600;background:var(--terra-bg);color:var(--terra);}
.lf-traco{color:#B7ADCB;}

/* ---------- fila de revisão ---------- */
.lf-fila{display:flex;flex-direction:column;gap:10px;max-height:440px;overflow-y:auto;padding:2px 6px 2px 2px;}
.lf-item{position:relative;border:1px solid rgba(124,58,237,.10);border-radius:16px;padding:13px 16px 12px 16px;background:rgba(255,255,255,.72);
  transition:transform .25s var(--suave),box-shadow .25s var(--suave),border-color .25s var(--suave);}
.lf-item:hover{transform:translateX(2px);border-color:rgba(124,58,237,.22);box-shadow:0 10px 24px -16px rgba(46,16,101,.35);}
.lf-item-topo{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;}
.lf-item-ico{width:30px;height:30px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:var(--claro);color:var(--roxo);}
.lf-item-nome{font-weight:600;color:var(--texto);font-size:14px;flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.lf-item-tags{display:flex;gap:6px;}
.lf-alertas{list-style:none;margin:0;padding:0 0 0 40px;display:flex;flex-direction:column;gap:4px;}
.lf-alertas li{display:flex;gap:8px;align-items:flex-start;color:var(--texto);font-size:13px;line-height:1.5;}
.lf-alertas li .lf-svg{margin-top:2px;color:var(--terra);}
.lf-item-erro .lf-alertas li .lf-svg{color:var(--vinho);}
.lf-vazio{display:flex;align-items:center;gap:12px;background:var(--teal-bg);color:var(--teal);border:1px solid rgba(47,122,107,.16);
  border-radius:16px;padding:16px 18px;font-weight:500;}

/* ---------- tabelas ---------- */
.lf-tabela-wrap{max-height:460px;overflow:auto;border-radius:16px;border:1px solid rgba(124,58,237,.10);background:rgba(255,255,255,.7);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-shadow:var(--sombra);}
.lf-tabela{width:100%;border-collapse:separate;border-spacing:0;font-size:13.5px;color:var(--texto);}
.lf-tabela th{position:sticky;top:0;z-index:1;background:rgba(246,242,253,.96);backdrop-filter:blur(8px);text-align:left;
  font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mudo);padding:12px 16px;border-bottom:1px solid var(--borda);white-space:nowrap;}
.lf-tabela td{padding:13px 16px;border-bottom:1px solid #F0EBF9;vertical-align:middle;transition:background .2s var(--suave);}
.lf-tabela tbody tr:last-child td{border-bottom:0;}
.lf-tabela tbody tr{transition:background .2s var(--suave);}
.lf-tabela tbody tr:hover td{background:rgba(124,58,237,.045);}
.lf-tabela tbody tr:hover td:first-child{box-shadow:inset 2px 0 0 var(--vivo);}
.lf-tabela .num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}
.lf-tabela th.num{text-align:right;}
.lf-tabela .forte{font-weight:600;color:var(--escuro);}
.lf-tabela .fraco{color:var(--mudo);}
.lf-tabela-vazia{padding:28px;text-align:center;color:var(--mudo);font-size:14px;}

/* ---------- detalhe: auditoria em painéis sobrepostos ---------- */
.lf-det-topo{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:4px 0 16px;}
.lf-det-nome{font-family:var(--serifa);font-size:1.3rem;font-weight:600;color:var(--escuro);letter-spacing:-.01em;}
.lf-audit{display:grid;grid-template-columns:minmax(0,1.15fr) 56px minmax(0,1fr);align-items:stretch;margin:6px 0 18px;}
.lf-camada{position:relative;isolation:isolate;}
.lf-camada::before{content:"";position:absolute;inset:10px -8px -10px 8px;z-index:-1;border-radius:22px;
  background:linear-gradient(160deg,rgba(221,211,247,.75),rgba(243,238,252,.45));border:1px solid rgba(124,58,237,.08);}
.lf-painel{position:relative;height:100%;box-sizing:border-box;border-radius:22px;padding:20px 22px;background:rgba(255,255,255,.78);
  backdrop-filter:blur(16px) saturate(150%);-webkit-backdrop-filter:blur(16px) saturate(150%);border:1px solid var(--vidro-borda);box-shadow:var(--sombra);}
.lf-painel-cab{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
.lf-etapa{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:var(--serifa);font-weight:600;
  font-size:14px;color:#fff;background:linear-gradient(140deg,var(--vivo),var(--escuro));box-shadow:0 6px 14px -6px rgba(91,33,182,.6);}
.lf-painel-tit{font-family:var(--serifa);font-size:17px;font-weight:600;color:var(--escuro);line-height:1.2;}
.lf-painel-leg{font-size:12.5px;color:var(--mudo);}
.lf-campos{display:flex;flex-direction:column;}
.lf-campo{display:grid;grid-template-columns:14px 150px minmax(0,1fr) auto;gap:10px;align-items:center;padding:9px 6px;border-radius:10px;
  border-bottom:1px solid #F0EBF9;transition:background .2s var(--suave);}
.lf-campo:last-child{border-bottom:0;}
.lf-campo:hover{background:rgba(124,58,237,.04);}
.lf-marca{width:8px;height:8px;border-radius:50%;background:var(--vivo);box-shadow:0 0 0 3px rgba(124,58,237,.12);}
.lf-campo.vazio .lf-marca{background:transparent;border:1.5px solid #C9BDE4;box-shadow:none;}
.lf-campo .k{color:var(--mudo);font-size:13px;font-weight:500;}
.lf-campo .v{color:var(--texto);font-size:14px;font-weight:600;word-break:break-word;}
.lf-campo.vazio .v{color:#A79CBF;font-style:italic;font-weight:400;}
.lf-refs{display:flex;gap:4px;}
.lf-ref{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10.5px;font-weight:600;
  color:var(--roxo);background:var(--claro);border:1px solid rgba(91,33,182,.14);}
.lf-ref.av{color:var(--terra);background:var(--terra-bg);border-color:rgba(181,86,47,.2);}
.lf-ponte{position:relative;display:flex;align-items:center;justify-content:center;}
.lf-ponte::before{content:"";position:absolute;top:24px;bottom:24px;left:50%;border-left:1.5px dashed rgba(124,58,237,.28);}
.lf-ponte span{position:relative;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;
  background:linear-gradient(140deg,var(--vivo),var(--roxo));box-shadow:0 0 0 6px rgba(243,238,252,.9),0 10px 20px -8px rgba(91,33,182,.6);}
.lf-linha{list-style:none;margin:0;padding:0;position:relative;}
.lf-linha::before{content:"";position:absolute;left:14px;top:14px;bottom:20px;width:1.5px;background:linear-gradient(180deg,rgba(124,58,237,.35),rgba(124,58,237,.08));}
.lf-passo{position:relative;display:flex;gap:14px;padding:0 0 16px 0;}
.lf-no{position:relative;z-index:1;flex:0 0 30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#fff;
  border:1.5px solid currentColor;box-shadow:0 0 0 4px rgba(255,255,255,.9);}
.lf-passo.ok .lf-no{color:var(--teal);background:var(--teal-bg);}
.lf-passo.av .lf-no{color:var(--terra);background:var(--terra-bg);}
.lf-passo-rot{display:flex;align-items:center;gap:8px;font-weight:600;color:var(--escuro);font-size:14px;}
.lf-passo-rot .lf-ref{flex:none;}
.lf-passo-campos{font-size:11.5px;color:var(--mudo);margin-top:1px;}
.lf-passo-msg{color:var(--texto);font-size:13px;line-height:1.5;margin-top:4px;}
.lf-passo.ok .lf-passo-msg{color:var(--teal);}
.lf-passo.fim{padding-bottom:0;}
.lf-passo.fim .lf-no{color:#fff;background:linear-gradient(140deg,var(--vivo),var(--escuro));border-color:transparent;}
@media (max-width:900px){.lf-audit{grid-template-columns:1fr;gap:0;}.lf-ponte{height:56px;}.lf-ponte::before{top:0;bottom:0;}
  .lf-ponte span{transform:rotate(90deg);}.lf-campo{grid-template-columns:14px 110px minmax(0,1fr) auto;}}

/* ---------- envio de lote ---------- */
[data-testid="stFileUploaderDropzone"]{background:rgba(255,255,255,.55);border:1.5px dashed #CDBEF0;border-radius:18px;padding:24px 22px;
  transition:border-color .25s var(--suave),background .25s var(--suave),box-shadow .25s var(--suave);}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--vivo);background:rgba(243,238,252,.85);box-shadow:0 0 0 5px rgba(124,58,237,.07);}
[data-testid="stFileUploaderDropzoneInstructions"]{display:flex;flex-direction:column;gap:2px;}
[data-testid="stFileUploaderDropzoneInstructions"] > div{display:none;}
[data-testid="stFileUploaderDropzoneInstructions"]::before{content:"Arraste os PDFs aqui";font-family:var(--serifa);font-size:16px;font-weight:600;color:var(--escuro);}
[data-testid="stFileUploaderDropzoneInstructions"]::after{content:"PDF · até 200 MB por arquivo";font-size:12.5px;color:var(--mudo);}
[data-testid="stFileUploaderDropzone"] button [data-testid="stMarkdownContainer"] p{font-size:0 !important;line-height:0;}
[data-testid="stFileUploaderDropzone"] button [data-testid="stMarkdownContainer"] p::after{content:"Escolher arquivos";font-size:14px;line-height:1.4;}
.lf-fila-vazia{border:1px dashed var(--borda);border-radius:16px;padding:20px;text-align:center;color:var(--mudo);font-size:14px;background:rgba(255,255,255,.45);}
[data-testid="stExpander"] details{border:1px solid var(--vidro-borda);border-radius:18px;background:var(--vidro);backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);box-shadow:var(--sombra);transition:box-shadow .3s var(--suave);}
[data-testid="stExpander"] details:hover{box-shadow:var(--sombra-alta);}
[data-testid="stExpander"] summary p{font-family:var(--serifa);font-weight:600;color:var(--escuro);font-size:16px;}

/* ---------- botões ---------- */
[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,var(--vivo) 0%,var(--roxo) 60%,var(--profundo) 100%) !important;border:0 !important;
  color:#fff !important;font-weight:600;letter-spacing:.01em;box-shadow:0 10px 22px -12px rgba(91,33,182,.75),0 1px 0 rgba(255,255,255,.18) inset;
  transition:transform .2s var(--suave),box-shadow .2s var(--suave),filter .2s var(--suave);}
[data-testid="stBaseButton-primary"]:hover{transform:translateY(-1px);filter:brightness(1.06);box-shadow:0 14px 28px -12px rgba(91,33,182,.85),0 1px 0 rgba(255,255,255,.18) inset;}
[data-testid="stBaseButton-primary"]:active{transform:translateY(0);}
[data-testid="stBaseButton-secondary"]{background:rgba(255,255,255,.7) !important;border:1px solid var(--borda) !important;color:var(--escuro) !important;
  font-weight:500;transition:border-color .2s var(--suave),color .2s var(--suave),background .2s var(--suave),transform .2s var(--suave);}
[data-testid="stBaseButton-secondary"]:hover{border-color:var(--lilas) !important;color:var(--roxo) !important;background:#fff !important;transform:translateY(-1px);}
button:focus-visible{outline:none !important;box-shadow:0 0 0 4px rgba(124,58,237,.18) !important;}

/* ---------- campos, seletores e filtros ---------- */
[data-testid="stTextInput"] [data-baseweb="input"],[data-baseweb="select"] > div{background:rgba(255,255,255,.75) !important;
  border:1px solid var(--borda) !important;border-radius:12px !important;
  transition:border-color .2s var(--suave),box-shadow .2s var(--suave),background .2s var(--suave);}
[data-testid="stTextInput"] [data-baseweb="input"]:hover,[data-baseweb="select"] > div:hover{border-color:#CDBEF0 !important;}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,[data-baseweb="select"] > div:focus-within{background:#fff !important;
  border-color:var(--vivo) !important;box-shadow:0 0 0 4px rgba(124,58,237,.12) !important;}
[data-testid="stTextInput"] input{background:transparent !important;font-size:14px;}
[data-testid="stTextInput"] input::placeholder{color:#9D92B6;}
[data-baseweb="tag"]{background:var(--claro) !important;color:var(--roxo) !important;border-radius:999px !important;}
[data-testid="stButtonGroup"] button{background:rgba(255,255,255,.7);border-color:var(--borda);color:var(--mudo);font-weight:500;
  transition:background .2s var(--suave),color .2s var(--suave),border-color .2s var(--suave);}
[data-testid="stButtonGroup"] button:hover{color:var(--roxo);border-color:var(--lilas);}
[data-testid="stBaseButton-segmented_controlActive"]{background:var(--escuro) !important;border-color:var(--escuro) !important;color:#fff !important;}
[data-testid="stBaseButton-segmented_controlActive"] p{color:#fff !important;}

/* ---------- abas ---------- */
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:6px;}
button[data-baseweb="tab"]{font-weight:500;font-size:14.5px;color:var(--mudo);padding:8px 14px;margin-right:0;border-radius:10px 10px 0 0;
  transition:color .2s var(--suave),background .2s var(--suave);}
button[data-baseweb="tab"]:hover{color:var(--roxo);background:rgba(124,58,237,.05);}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--escuro);font-weight:600;}
[data-baseweb="tab-highlight"]{background:linear-gradient(90deg,var(--vivo),var(--roxo)) !important;height:2px !important;border-radius:2px;}
[data-baseweb="tab-border"]{background:var(--borda) !important;height:1px !important;}
"""

CSS = (
    "<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
    "&family=Lora:wght@500;600;700&display=swap');"
    f":root{{{_VARS}}}{_REGRAS}</style>"
)


def aplicar() -> None:
    """Injeta o CSS do painel."""
    st.markdown(CSS, unsafe_allow_html=True)


def seguro(texto) -> str:
    """Escapa HTML e o cifrão (que o Streamlit trataria como fórmula matemática)."""
    return html.escape("" if texto is None else str(texto)).replace("$", "&#36;")


def _data_uri(arquivo: str) -> str:
    dados = (ASSETS / arquivo).read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(dados).decode()


def logo_lateral() -> str:
    return f'<img class="lf-side-logo" src="{_data_uri("melia-logo-branco.svg")}" alt="Melia">'


# ---------- componentes ----------
def chip(texto: str, demo: bool) -> str:
    classe, ico = ("lf-chip-demo", "faisca") if demo else ("lf-chip-real", "escudo")
    return f'<span class="lf-chip {classe}">{icone(ico, 14)}{seguro(texto)}</span>'


def aviso(texto_html: str) -> str:
    return f'<div class="lf-aviso">{icone("faisca", 16)}<span>{texto_html}</span></div>'


def pill_status(status: str) -> str:
    rotulo, classe, ico = ESTILOS_STATUS[status]
    return f'<span class="lf-pill {classe}">{icone(ico, 12, 2)}{rotulo}</span>'


def pill(texto: str, classe: str, ico: str | None = None) -> str:
    return f'<span class="lf-pill {classe}">{icone(ico, 12, 2) if ico else ""}{seguro(texto)}</span>'


def pill_tipo(tipo: str) -> str:
    return f'<span class="lf-pill lf-tipo">{seguro(tipo.replace("_", " "))}</span>'


def kpis(valor: str, n_docs: int, pct_ok: int, cartoes: list[tuple]) -> str:
    """Bloco de indicadores: cartão de destaque (valor extraído) + grade 2x2. cartoes = (rótulo, valor, nota, cor, ícone)."""
    hero = (
        f'<div class="lf-hero"><div class="lf-hero-rot">{icone("moedas", 16)}Valor extraído</div>'
        f'<div class="lf-hero-val">{seguro(valor)}</div>'
        f'<div class="lf-hero-nota">soma dos totais de {n_docs} documento(s)</div>'
        f'<div class="lf-hero-rodape"><div class="lf-barra"><span style="width:{pct_ok}%"></span></div>'
        f'<div class="lf-hero-leg"><span>Conferidos sem alertas</span><b>{pct_ok}%</b></div></div></div>'
    )
    pequenos = "".join(
        f'<div class="lf-kpi" style="--cor:{cor}"><div class="lf-kpi-topo"><span class="lf-kpi-rot">{seguro(rotulo)}</span>'
        f'<span class="lf-kpi-ico">{icone(ico, 16)}</span></div><div class="lf-kpi-val">{seguro(v)}</div>'
        f'<div class="lf-kpi-nota">{seguro(nota)}</div></div>'
        for rotulo, v, nota, cor, ico in cartoes
    )
    return f'<div class="lf-kpis">{hero}{pequenos}</div>'


def item_fila(arquivo: str, tipo: str | None, status: str, mensagens: list[str]) -> str:
    tags = (pill_tipo(tipo) if tipo else "") + pill_status(status)
    ico_msg = icone("erro" if status == "erro" else "alerta", 14)
    lista = "".join(f"<li>{ico_msg}<span>{seguro(m)}</span></li>" for m in mensagens if m)
    return (f'<div class="lf-item lf-item-{status}"><div class="lf-item-topo"><span class="lf-item-ico">{icone("arquivo", 16)}</span>'
            f'<span class="lf-item-nome" title="{seguro(arquivo)}">{seguro(arquivo)}</span><span class="lf-item-tags">{tags}</span></div>'
            f'<ul class="lf-alertas">{lista}</ul></div>')


def fila_revisao(itens: list[str]) -> str:
    if not itens:
        return f'<div class="lf-vazio">{icone("escudo", 20)}Nenhum documento precisa de revisão.</div>'
    return f'<div class="lf-fila">{"".join(itens)}</div>'


def tabela(df: pd.DataFrame, html_cols=(), num_cols=(), forte_cols=(), fraco_cols=(), altura: int = 460) -> str:
    """Tabela HTML leve: só linhas horizontais, hover e cabeçalho fixo. Colunas em html_cols já vêm em HTML."""
    if df.empty:
        return '<div class="lf-tabela-wrap"><div class="lf-tabela-vazia">Nenhum documento com esses filtros.</div></div>'

    def classe(c):
        nomes = [n for n, cols in (("num", num_cols), ("forte", forte_cols), ("fraco", fraco_cols)) if c in cols]
        return f' class="{" ".join(nomes)}"' if nomes else ""

    cab = "".join(f"<th{classe(c) if c in num_cols else ''}>{seguro(c)}</th>" for c in df.columns)
    linhas = "".join(
        "<tr>" + "".join(f"<td{classe(c)}>{v if c in html_cols else seguro(v)}</td>" for c, v in zip(df.columns, linha)) + "</tr>"
        for linha in df.itertuples(index=False, name=None)
    )
    return (f'<div class="lf-tabela-wrap" style="max-height:{altura}px"><table class="lf-tabela"><thead><tr>{cab}</tr></thead>'
            f'<tbody>{linhas}</tbody></table></div>')


def auditoria(campos: dict, refs: dict[str, list[int]], confs: list, status: str) -> str:
    """Painéis sobrepostos: dados extraídos (1) -> conferência em linha do tempo (2) -> resultado.

    refs liga cada campo aos números das conferências que o usaram; confs são objetos com rotulo, ok e alertas.
    """
    falhas = {i for i, c in enumerate(confs, 1) if not c.ok}
    preenchidos = sum(1 for v in campos.values() if v)
    linhas = []
    for k, v in campos.items():
        marcas = "".join(f'<span class="lf-ref{" av" if n in falhas else ""}" title="Conferência {n}">{n}</span>'
                         for n in refs.get(k, []))
        linhas.append(f'<div class="lf-campo{"" if v else " vazio"}"><span class="lf-marca"></span><span class="k">{seguro(k)}</span>'
                      f'<span class="v">{seguro(v) if v else "(vazio)"}</span><span class="lf-refs">{marcas}</span></div>')
    dados = (f'<div class="lf-camada"><div class="lf-painel"><div class="lf-painel-cab"><span class="lf-etapa">1</span><div>'
             f'<div class="lf-painel-tit">Dados extraídos</div><div class="lf-painel-leg">{preenchidos} de {len(campos)} campos preenchidos'
             f'</div></div></div><div class="lf-campos">{"".join(linhas)}</div></div></div>')

    usados = {n: [k for k, ns in refs.items() if n in ns] for n in range(1, len(confs) + 1)}
    passos = []
    for n, conf in enumerate(confs, 1):
        cls, ico = ("ok", "check") if conf.ok else ("av", "alerta")
        msg = "Tudo certo." if conf.ok else "<br>".join(seguro(a) for a in conf.alertas)
        origem = f'<div class="lf-passo-campos">usa: {seguro(" · ".join(usados[n]))}</div>' if usados[n] else ""
        passos.append(f'<li class="lf-passo {cls}"><span class="lf-no">{icone(ico, 14, 2)}</span><div>'
                      f'<div class="lf-passo-rot"><span class="lf-ref{" av" if not conf.ok else ""}">{n}</span>{seguro(conf.rotulo)}</div>'
                      f'{origem}<div class="lf-passo-msg">{msg}</div></div></li>')
    passos.append(f'<li class="lf-passo fim"><span class="lf-no">{icone("escudo", 14, 2)}</span><div>'
                  f'<div class="lf-passo-rot">Resultado {pill_status(status)}</div></div></li>')
    ok = len(confs) - len(falhas)
    conferencia = (f'<div class="lf-camada"><div class="lf-painel"><div class="lf-painel-cab"><span class="lf-etapa">2</span><div>'
                   f'<div class="lf-painel-tit">Conferência</div><div class="lf-painel-leg">{ok} de {len(confs)} verificações sem alerta'
                   f'</div></div></div><ol class="lf-linha">{"".join(passos)}</ol></div></div>')
    ponte = f'<div class="lf-ponte"><span>{icone("seta", 16, 2)}</span></div>'
    return f'<div class="lf-audit">{dados}{ponte}{conferencia}</div>'
