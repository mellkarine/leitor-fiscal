# Leitor Fiscal

*Uma criação **Melia**.*

Extrai dados de **notas fiscais, boletos e recibos em PDF** e entrega uma planilha pronta,
para acabar com a digitação manual no financeiro.

![Capa](docs/imagens/00_capa.png)

> **Status:** em desenvolvimento. Todos os documentos deste repositório são **fictícios**.

## Como funciona

1. `pdfplumber` lê o texto de cada PDF.
2. Um LLM (Groq, via LangChain) preenche os campos de um schema Pydantic. Campo ausente fica vazio, nunca inventado.
3. O código Python **valida**: CNPJ/CPF, campos obrigatórios, soma dos itens contra o total, vencimento.
4. O que não confere vai para revisão humana; o resultado sai em Excel e CSV.

O LLM só lê e organiza; contas e validações ficam no código.

O painel (Streamlit) abre em **Novo lote**: você envia os PDFs, confere a fila (páginas, tamanho e se há texto selecionável) e processa. Depois os resultados ficam em quatro abas: **Visão geral** (indicadores, fila de revisão e gráficos), **Documentos** (busca, filtros e detalhe com a conferência de cada verificação), **Exportar** (Excel formatado com abas documentos, itens e resumo, e CSVs) e **Acerto** (só com extração real, compara com o gabarito).

![Resultados](docs/imagens/02_resultados.png)

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py             # interface; abre em modo demonstração se não houver chave
```

Para extrair de verdade, copie `.env.example` para `.env`, coloque sua `GROQ_API_KEY` e desligue o
"Modo demonstração" na barra lateral. **Nunca suba o `.env` para o GitHub** (já está no `.gitignore`).

Pela linha de comando:

```bash
python -m leitor_fiscal.cli --pasta data/sintetico/pdfs --saida saida          # com Groq
python -m leitor_fiscal.cli --demo                                              # sem API
python -m leitor_fiscal.avaliar --previsto saida/documentos.csv                # acerto vs. gabarito
pytest                                                                          # testes, sem API
```

## Gerar as imagens (README e LinkedIn)

As imagens vêm da execução real, não de texto fixo. Depois de configurar a `GROQ_API_KEY`:

```bash
pip install -r requirements-imagens.txt && playwright install chromium
python -m leitor_fiscal.cli                 # extrai de verdade e grava saida/*.csv
python scripts/gerar_capa.py                # capa com os campos extraídos de nota_001.pdf
python scripts/capturar_telas.py            # prints do app na paleta roxa, em docs/imagens/
```

Gera `00_capa`, `01_inicio`, `02_resultados` (visão geral), `03_detalhe` e, com o gabarito, `04_acerto`
(o acerto real por campo). Confira as imagens antes de publicar: elas mostram o que o modelo
de fato devolveu, inclusive os erros.

## Modo demonstração

Devolve respostas prontas para os 7 PDFs de exemplo, só para ver a interface e o fluxo de
validação sem gastar API. **Não gere imagens de divulgação neste modo.** **Não mede nem prova nada sobre a qualidade da extração.** O acerto real só
aparece com o LLM ligado (aba "Acerto contra o gabarito" do app, ou `leitor_fiscal.avaliar`).

## Modelo do Groq

O padrão é `openai/gpt-oss-120b`. Os modelos `llama-3.x` e `qwen3-32b` foram descontinuados pelo Groq em
2026; a lista atual está em https://console.groq.com/docs/models. Troque em `GROQ_MODEL`. Se o modelo não
aceitar saída estruturada por `json_schema`, use `GROQ_METHOD=function_calling`. A API gratuita tem limites
por modelo, por isso o processamento é em lotes pequenos (`--concorrencia`).

## Dados de teste

`data/sintetico/` tem os modelos em Word, os 7 PDFs e o gabarito em CSV. Quatro dos PDFs são casos
difíceis de propósito (total que não fecha, CNPJ inválido, boleto sem vencimento, valor só por extenso);
os alertas esperados estão em `gabarito/alertas_esperados.csv`.

## Limitações conhecidas

- Só PDFs com texto selecionável (sem OCR).
- Nota fiscal eletrônica já existe em XML; este projeto é para PDFs sem XML.
- Poucos documentos de teste: o número de acerto só vale depois de ampliar o conjunto.

## Marca

Os logotipos da Melia estão em `assets/` (SVG e PNG). O texto do logotipo usa a fonte Poppins Bold (licença OFL), convertida em curvas.

## Licença

MIT.
