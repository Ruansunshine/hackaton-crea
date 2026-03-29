from models.schemas import ResultadoBusca
from retrieval.buscador import Buscador
from services.chroma_client import ClienteChroma
from services.embeddings import ServicoEmbeddings


class BuscadorTemplate(Buscador):
    def __init__(
        self,
        cliente_chroma: ClienteChroma,
        servico_embeddings: ServicoEmbeddings,
        nome_colecao: str,
    ):
        super().__init__(cliente_chroma, servico_embeddings, nome_colecao)

    def buscar_melhor_template(self, texto_consulta: str, top_k: int = 1) -> ResultadoBusca | None:
        resultados = self.buscar(texto_consulta=texto_consulta, top_k=top_k)
        if not resultados:
            return None
        return resultados[0]
