from typing import Any

from loguru import logger

from models.excecoes import ErroBuscaVetorial
from models.schemas import ResultadoBusca
from services.chroma_client import ClienteChroma
from services.embeddings import ServicoEmbeddings


class Buscador:
    def __init__(
        self,
        cliente_chroma: ClienteChroma,
        servico_embeddings: ServicoEmbeddings,
        nome_colecao: str,
    ):
        self._colecao = cliente_chroma.obter_ou_criar_colecao(nome_colecao)
        self._servico_embeddings = servico_embeddings

    def buscar(
        self,
        texto_consulta: str,
        top_k: int = 5,
        metadados_filtro: dict[str, Any] | None = None,
    ) -> list[ResultadoBusca]:
        if not texto_consulta.strip():
            return []

        embeddings = self._servico_embeddings.gerar([texto_consulta])
        try:
            resposta = self._colecao.query(
                query_embeddings=embeddings,
                n_results=top_k,
                where=metadados_filtro or None,
            )
        except ValueError as erro:
            logger.exception("Erro ao executar busca vetorial")
            raise ErroBuscaVetorial("Consulta vetorial inválida") from erro

        ids = resposta.get("ids", [[]])[0]
        documentos = resposta.get("documents", [[]])[0]
        metadados_lista = resposta.get("metadatas", [[]])[0]
        distancias = resposta.get("distances", [[]])[0]

        resultados: list[ResultadoBusca] = []
        for indice, id_documento in enumerate(ids):
            distancia = distancias[indice] if indice < len(distancias) else None
            metadados = metadados_lista[indice] if indice < len(metadados_lista) else {}
            conteudo = documentos[indice] if indice < len(documentos) else ""
            resultados.append(
                ResultadoBusca(
                    id_documento=id_documento,
                    conteudo=conteudo,
                    metadados=metadados or {},
                    distancia=distancia,
                )
            )

        return resultados
