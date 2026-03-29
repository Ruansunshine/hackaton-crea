from fastapi import FastAPI
from loguru import logger

from config.settings import obter_configuracoes
from models.schemas import (
    DocumentoIngestao,
    LoteDocumentosIngestao,
    RequisicaoRAG,
    RespostaRAG,
)
from pipelines.pipeline_rag import PipelineRAG
from services.bootstrap import criar_container_servicos


configuracoes = obter_configuracoes()
app = FastAPI(
    title="RAG Service",
    description="Serviço RAG genérico e extensível para análise técnica.",
    version="0.1.0",
)

container = criar_container_servicos(configuracoes)
pipeline_rag = PipelineRAG(
    extrator=container["extrator"],
    validador=container["validador"],
    buscador=container["buscador"],
    buscador_template=container["buscador_template"],
    gerador=container["gerador"],
)
servico_ingestao = container["servico_ingestao"]


@app.on_event("startup")
def configurar_logs() -> None:
    logger.remove()
    logger.add(
        sink=lambda mensagem: print(mensagem, end=""),
        level=configuracoes.log_level,
    )
    logger.info("RAG Service inicializado em ambiente {}", configuracoes.ambiente)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "servico": "rag-service", "ambiente": configuracoes.ambiente}


@app.get("/")
def raiz() -> dict[str, str]:
    return {
        "servico": "rag-service",
        "status": "ativo",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/rag/processar", response_model=RespostaRAG)
def processar_rag(requisicao: RequisicaoRAG) -> RespostaRAG:
    return pipeline_rag.executar(requisicao)


@app.post("/ingestao/documentos")
def ingerir_documentos(lote: LoteDocumentosIngestao) -> dict[str, int]:
    documentos: list[DocumentoIngestao] = lote.documentos
    total_chunks = servico_ingestao.ingerir_lote(documentos)
    return {"documentos_processados": len(documentos), "chunks_indexados": total_chunks}
