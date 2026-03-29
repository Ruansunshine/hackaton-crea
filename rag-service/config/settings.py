import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Configuracoes:
    api_ai: str
    model_ai: str
    chroma_host: str
    chroma_port: int
    ambiente: str
    log_level: str
    colecao_base_conhecimento: str = "base_conhecimento"
    colecao_base_respostas: str = "base_respostas"


def _obter_variavel_ambiente(nome: str, padrao: str = "") -> str:
    valor = os.getenv(nome, padrao)
    return valor.strip()


def obter_configuracoes() -> Configuracoes:
    ambiente = _obter_variavel_ambiente("AMBIENTE", "dev").lower()
    log_level = _obter_variavel_ambiente("LOG_LEVEL", "INFO").upper()

    if ambiente not in {"dev", "prod"}:
        ambiente = "dev"

    if log_level not in {"INFO", "DEBUG", "ERROR"}:
        log_level = "INFO"

    porta_chroma_texto = _obter_variavel_ambiente("CHROMA_PORT", "8000")
    porta_chroma = int(porta_chroma_texto)

    return Configuracoes(
        api_ai=_obter_variavel_ambiente("API_AI"),
        model_ai=_obter_variavel_ambiente("MODEL_AI", "gpt-4o-mini"),
        chroma_host=_obter_variavel_ambiente("CHROMA_HOST", "chromadb"),
        chroma_port=porta_chroma,
        ambiente=ambiente,
        log_level=log_level,
    )
