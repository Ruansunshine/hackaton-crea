from sentence_transformers import SentenceTransformer


class ServicoEmbeddings:
    def __init__(self, nome_modelo: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self._modelo = SentenceTransformer(nome_modelo)

    def gerar(self, textos: list[str]) -> list[list[float]]:
        embeddings = self._modelo.encode(textos, normalize_embeddings=True)
        return [vetor.tolist() for vetor in embeddings]
