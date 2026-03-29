from chromadb.api.models.Collection import Collection
from loguru import logger

from ingestion.chunker import ChunkerTexto
from models.schemas import DocumentoIngestao
from services.chroma_client import ClienteChroma
from services.embeddings import ServicoEmbeddings


class ServicoIngestao:
    def __init__(
        self,
        cliente_chroma: ClienteChroma,
        servico_embeddings: ServicoEmbeddings,
        nome_base_conhecimento: str,
        nome_base_respostas: str,
    ):
        self._servico_embeddings = servico_embeddings
        self._chunker = ChunkerTexto(tamanho_aproximado_tokens=500)
        self._colecao_conhecimento = cliente_chroma.obter_ou_criar_colecao(nome_base_conhecimento)
        self._colecao_respostas = cliente_chroma.obter_ou_criar_colecao(nome_base_respostas)

    def ingerir_lote(self, documentos: list[DocumentoIngestao]) -> int:
        total_chunks = 0
        for documento in documentos:
            total_chunks += self._ingerir_documento(documento)
        return total_chunks

    def _ingerir_documento(self, documento: DocumentoIngestao) -> int:
        chunks = self._chunker.dividir(documento.texto)
        if not chunks:
            return 0

        embeddings = self._servico_embeddings.gerar(chunks)
        ids = [f"{documento.id_documento}_chunk_{indice}" for indice in range(len(chunks))]

        metadados_base = documento.metadados.model_dump()
        metadados = []
        for indice, _ in enumerate(chunks):
            metadado_item = {
                "id_documento": documento.id_documento,
                "chunk_indice": indice,
                "tipo": metadados_base.get("tipo", "generico"),
                "fonte": metadados_base.get("fonte", "nao_informado"),
                "categoria": metadados_base.get("categoria", "nao_informado"),
            }
            metadados.append(metadado_item)

        colecao = self._resolver_colecao(documento.base_destino)
        colecao.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadados,
            embeddings=embeddings,
        )
        logger.info(
            "Documento {} ingerido em {} com {} chunks",
            documento.id_documento,
            documento.base_destino,
            len(chunks),
        )
        return len(chunks)

    def _resolver_colecao(self, base_destino: str) -> Collection:
        if base_destino == "base_respostas":
            return self._colecao_respostas
        return self._colecao_conhecimento
