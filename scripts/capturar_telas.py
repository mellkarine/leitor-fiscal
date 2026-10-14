"""Captura as telas do painel Leitor Fiscal (marca Melia), com a extração REAL (Groq).

Pré-requisitos:
    pip install playwright && playwright install chromium
    GROQ_API_KEY no arquivo .env

Uso (na raiz do projeto):
    python scripts/capturar_telas.py                 # extração real, grava em docs/imagens/
    python scripts/capturar_telas.py --demo --saida /tmp/teste   # só para testar o script, sem API

As imagens geradas com --demo mostram respostas simuladas: NÃO publique.
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent


def esperar_servidor(url: str, tentativas: int = 40) -> None:
    for _ in range(tentativas):
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("O Streamlit não subiu a tempo.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--porta", type=int, default=8599)
    ap.add_argument("--saida", default=str(RAIZ / "docs" / "imagens"))
    ap.add_argument("--demo", action="store_true", help="Só para testar: usa respostas simuladas")
    ap.add_argument("--espera", type=int, default=180, help="Segundos para aguardar a extração")
    a = ap.parse_args()

    load_dotenv(RAIZ / ".env")
    env = os.environ.copy()
    if a.demo:
        env["LEITOR_FISCAL_DEMO"] = "1"
        print("[aviso] modo demonstração: não publique estas imagens.")
    elif not env.get("GROQ_API_KEY"):
        sys.exit("Defina GROQ_API_KEY no .env para capturar com a extração real.")

    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    url = f"http://localhost:{a.porta}"
    servidor = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true",
         "--server.port", str(a.porta)], cwd=RAIZ, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        esperar_servidor(url)
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            pg = navegador.new_page(viewport={"width": 1360, "height": 900}, device_scale_factor=2)
            pg.goto(url)
            pg.wait_for_selector("text=Novo lote", timeout=30000)
            pg.wait_for_timeout(1200)
            pg.screenshot(path=str(saida / "01_inicio.png"))

            pg.get_by_role("button", name="Processar documentos").click()
            pg.wait_for_selector("text=Documentos lidos", timeout=a.espera * 1000)
            pg.wait_for_timeout(2000)
            pg.set_viewport_size({"width": 1360, "height": 1200})
            pg.wait_for_timeout(800)
            pg.screenshot(path=str(saida / "02_resultados.png"))

            # aba Documentos: tabela e detalhe de um documento (nota_002 se existir, senão o segundo)
            pg.set_viewport_size({"width": 1360, "height": 900})
            pg.get_by_role("tab", name="Documentos").click()
            pg.wait_for_timeout(1000)
            caixa = pg.locator('[data-testid="stSelectbox"]')
            caixa.scroll_into_view_if_needed()
            caixa.click()
            pg.wait_for_timeout(400)
            opcoes = pg.get_by_role("option")
            alvo = pg.get_by_role("option", name="nota_002.pdf")
            (alvo if alvo.count() else opcoes.nth(1)).click()
            pg.wait_for_timeout(1500)
            pg.evaluate("""() => {
                const h = [...document.querySelectorAll('h2,h3')].find(e => e.textContent.includes('Detalhe do documento'));
                const sc = document.querySelector('[data-testid="stMain"]') || document.scrollingElement;
                sc.scrollTo(0, h.getBoundingClientRect().top + sc.scrollTop - 24);
            }""")
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(saida / "03_detalhe.png"))

            # aba Acerto (só existe com extração real e gabarito)
            aba_acerto = pg.get_by_role("tab", name="Acerto")
            if aba_acerto.count():
                aba_acerto.click()
                pg.wait_for_selector("text=Acerto contra o gabarito", timeout=15000)
                pg.wait_for_timeout(1200)
                pg.screenshot(path=str(saida / "04_acerto.png"))
            navegador.close()
    finally:
        servidor.terminate()
    print(f"Imagens gravadas em {saida}")


if __name__ == "__main__":
    main()
