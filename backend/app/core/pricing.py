from __future__ import annotations

# Listaár USD / 1M tokenre, a bemenet cache nélküli ára.
# Forrás: https://opencode.ai/docs/go/ (az opencode Go modelltáblája, "DeepSeek V4.1 Flash")
# és https://api-docs.deepseek.com/quick_start/pricing, lekérdezve 2026-10-07.
# A DeepSeek saját oldalán a modell "deepseek-flash" néven szerepel (a régi
# "deepseek-v4-flash" név ugyanazt az árat kapja); az opencode oldal a
# "DeepSeek V4.1 Flash" nevet listázza azonos árral. Az ár idősávos:
# csúcsidőben (hétköznap 01-04 és 06-10 UTC) 0,30 / 1,20, egyébként 0,15 / 0,60.
# A kijelző becslés, ezért a csúcsidős (felső) listaár szerepel itt.
INPUT_PRICE_PER_MILLION_USD = 0.30
OUTPUT_PRICE_PER_MILLION_USD = 1.20
PRICE_SOURCE = (
    "https://opencode.ai/docs/go/ és "
    "https://api-docs.deepseek.com/quick_start/pricing, 2026-10-07 "
    "(DeepSeek V4.1 Flash, csúcsidős listaár)"
)


def price_payload() -> dict[str, float]:
    return {
        "input_per_million_usd": INPUT_PRICE_PER_MILLION_USD,
        "output_per_million_usd": OUTPUT_PRICE_PER_MILLION_USD,
    }
