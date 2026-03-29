from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import Configuracoes
from models.excecoes import ErroExtracaoDados, ErroGeracaoResposta


class ClienteAI:
    def __init__(self, configuracoes: Configuracoes):
        self.configuracoes = configuracoes
        self._cliente = OpenAI(api_key=configuracoes.api_ai) if configuracoes.api_ai else None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def extrair_estruturado(self, texto: str) -> str:
        if not self._cliente:
            return self._fallback_extracao(texto)

        try:
            resposta = self._cliente.responses.create(
                model=self.configuracoes.model_ai,
                input=(
                    "Você é um extrator de dados para ART/CAT do CREA. "
                    "Retorne APENAS JSON válido com as chaves: "
                    "numero_art, profissional, tipo, atividade, contratante, local, descricao_servico, "
                    "status_art, indicadores_execucao, indicadores_conclusao, documentos_comprobatorios, campos_extras. "
                    "Use listas de strings para indicadores_execucao, indicadores_conclusao e documentos_comprobatorios. "
                    f"Texto: {texto}"
                ),
            )
            return resposta.output_text
        except AuthenticationError as erro:
            logger.exception("Falha de autenticação na extração estruturada")
            raise ErroExtracaoDados("Credenciais inválidas para extração") from erro
        except RateLimitError as erro:
            logger.exception("Rate limit durante extração estruturada")
            raise ErroExtracaoDados("Limite de requisições excedido na extração") from erro
        except APIConnectionError as erro:
            logger.exception("Falha de conexão com provedor de IA na extração")
            raise ErroExtracaoDados("Falha de conexão durante extração") from erro

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    def gerar_resposta(self, prompt: str) -> str:
        if not self._cliente:
            return self._fallback_geracao(prompt)

        try:
            resposta = self._cliente.responses.create(
                model=self.configuracoes.model_ai,
                input=prompt,
            )
            return resposta.output_text
        except AuthenticationError as erro:
            logger.exception("Falha de autenticação na geração")
            raise ErroGeracaoResposta("Credenciais inválidas para geração") from erro
        except RateLimitError as erro:
            logger.exception("Rate limit durante geração")
            raise ErroGeracaoResposta("Limite de requisições excedido na geração") from erro
        except APIConnectionError as erro:
            logger.exception("Falha de conexão com provedor de IA na geração")
            raise ErroGeracaoResposta("Falha de conexão durante geração") from erro

    def _fallback_extracao(self, texto: str) -> str:
        resumo = texto[:500]
        return (
            '{"numero_art":"nao_informado",'
            '"profissional":"nao_informado",'
            '"tipo":"nao_identificado",'
            '"atividade":"",'
            '"contratante":"nao_informado",'
            '"local":"nao_informado",'
            f'"descricao_servico":"{resumo}",'
            '"status_art":"nao_informado",'
            '"indicadores_execucao":[],'
            '"indicadores_conclusao":[],'
            '"documentos_comprobatorios":[],'
            '"campos_extras":{"modo":"fallback"}}'
        )

    def _fallback_geracao(self, prompt: str) -> str:
        return (
            "Resposta gerada em modo fallback. "
            "Contexto técnico analisado e pronto para revisão profissional.\n\n"
            f"Trecho-base:\n{prompt[:1000]}"
        )
