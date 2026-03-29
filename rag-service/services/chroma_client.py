import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings as ChromaSettings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from config.settings import Configuracoes
from models.excecoes import ErroConexaoChroma


class ClienteChroma:
    def __init__(self, configuracoes: Configuracoes):
        self.configuracoes = configuracoes
        self._cliente = self._criar_cliente()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def _criar_cliente(self) -> chromadb.HttpClient:
        try:
            cliente = chromadb.HttpClient(
                host=self.configuracoes.chroma_host,
                port=self.configuracoes.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            cliente.heartbeat()
            logger.info(
                "Conectado ao ChromaDB em {}:{}",
                self.configuracoes.chroma_host,
                self.configuracoes.chroma_port,
            )
            return cliente
        except ValueError as erro:
            logger.exception("Falha de configuração ao conectar no ChromaDB")
            raise ErroConexaoChroma("Configuração inválida para ChromaDB") from erro
        except ConnectionError as erro:
            logger.exception("Falha de conexão de rede ao ChromaDB")
            raise ErroConexaoChroma("Não foi possível conectar ao ChromaDB") from erro

    def obter_ou_criar_colecao(self, nome: str) -> Collection:
        try:
            return self._cliente.get_or_create_collection(name=nome)
        except ValueError as erro:
            logger.exception("Erro ao obter/criar coleção {}", nome)
            raise ErroConexaoChroma(f"Falha ao preparar coleção {nome}") from erro
