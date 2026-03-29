class ChunkerTexto:
    def __init__(self, tamanho_aproximado_tokens: int = 500):
        self.tamanho_aproximado_tokens = tamanho_aproximado_tokens

    def dividir(self, texto: str) -> list[str]:
        if not texto.strip():
            return []

        palavras = texto.split()
        tamanho_lote = max(50, int(self.tamanho_aproximado_tokens * 0.75))
        chunks: list[str] = []

        indice = 0
        while indice < len(palavras):
            limite = indice + tamanho_lote
            bloco = " ".join(palavras[indice:limite])
            chunks.append(bloco)
            indice = limite

        return chunks
