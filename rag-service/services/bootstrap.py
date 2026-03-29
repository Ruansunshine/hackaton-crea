from agents.extrator import AgenteExtrator
from agents.gerador import AgenteGerador
from agents.validador import AgenteValidadorART
from config.settings import Configuracoes
from ingestion.servico_ingestao import ServicoIngestao
from retrieval.buscador import Buscador
from retrieval.buscador_template import BuscadorTemplate
from services.chroma_client import ClienteChroma
from services.cliente_ai import ClienteAI
from services.embeddings import ServicoEmbeddings


def criar_container_servicos(configuracoes: Configuracoes) -> dict[str, object]:
    cliente_chroma = ClienteChroma(configuracoes)
    servico_embeddings = ServicoEmbeddings()
    cliente_ai = ClienteAI(configuracoes)

    buscador = Buscador(
        cliente_chroma=cliente_chroma,
        servico_embeddings=servico_embeddings,
        nome_colecao=configuracoes.colecao_base_conhecimento,
    )
    buscador_template = BuscadorTemplate(
        cliente_chroma=cliente_chroma,
        servico_embeddings=servico_embeddings,
        nome_colecao=configuracoes.colecao_base_respostas,
    )

    return {
        "extrator": AgenteExtrator(cliente_ai=cliente_ai),
        "validador": AgenteValidadorART(),
        "gerador": AgenteGerador(cliente_ai=cliente_ai),
        "buscador": buscador,
        "buscador_template": buscador_template,
        "servico_ingestao": ServicoIngestao(
            cliente_chroma=cliente_chroma,
            servico_embeddings=servico_embeddings,
            nome_base_conhecimento=configuracoes.colecao_base_conhecimento,
            nome_base_respostas=configuracoes.colecao_base_respostas,
        ),
    }
