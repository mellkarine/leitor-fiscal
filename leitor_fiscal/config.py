"""Valores padrão compartilhados entre o app, a linha de comando e o extrator."""

# Os modelos llama-3.x e qwen3-32b do Groq foram descontinuados em 2026; confira a lista atual
# em https://console.groq.com/docs/models e troque pela variável GROQ_MODEL, se precisar.
MODELO_PADRAO = "openai/gpt-oss-120b"

# json_schema usa a API de saída estruturada do Groq; se o modelo não suportar,
# tente GROQ_METHOD=function_calling no .env.
METODO_PADRAO = "json_schema"
