import json

from loguru import logger

from models.excecoes import ErroExtracaoDados
from models.schemas import DadoExtraido
from services.cliente_ai import ClienteAI


class AgenteExtrator:
    def __init__(self, cliente_ai: ClienteAI):
        self.cliente_ai = cliente_ai

    def extrair(self, texto_bruto: str) -> DadoExtraido:
        if not texto_bruto.strip():
            raise ErroExtracaoDados("Texto de entrada vazio para extração")

        conteudo = self.cliente_ai.extrair_estruturado(texto_bruto)
        try:
            dados = json.loads(conteudo)
            return DadoExtraido(**self._normalizar_payload(dados, texto_bruto))
        except json.JSONDecodeError as erro:
            logger.exception("Falha ao converter extração em JSON")
            raise ErroExtracaoDados("Modelo retornou conteúdo inválido para extração") from erro
        except ValueError as erro:
            logger.exception("Falha de validação no dado estruturado extraído")
            raise ErroExtracaoDados("Estrutura extraída não corresponde ao schema") from erro

    def _normalizar_payload(self, dados: dict, texto_bruto: str) -> dict:
        if not isinstance(dados, dict):
            raise ErroExtracaoDados("JSON de extração fora do formato de objeto")

        descricao_legada = str(dados.get("descricao", "") or "")
        entidade_legada = str(dados.get("entidade_relacionada", "") or "")
        tipo_legado = str(dados.get("tipo_ocorrencia", "") or "")

        return {
            "numero_art": str(dados.get("numero_art", "nao_informado") or "nao_informado"),
            "profissional": str(dados.get("profissional", "nao_informado") or "nao_informado"),
            "tipo": str(dados.get("tipo", tipo_legado or "nao_identificado") or "nao_identificado"),
            "atividade": str(dados.get("atividade", "") or ""),
            "contratante": str(dados.get("contratante", entidade_legada or "nao_informado") or "nao_informado"),
            "local": str(dados.get("local", "nao_informado") or "nao_informado"),
            "descricao_servico": str(dados.get("descricao_servico", descricao_legada or texto_bruto[:500]) or texto_bruto[:500]),
            "status_art": str(dados.get("status_art", "nao_informado") or "nao_informado"),
            "indicadores_execucao": self._normalizar_lista(dados.get("indicadores_execucao")),
            "indicadores_conclusao": self._normalizar_lista(dados.get("indicadores_conclusao")),
            "documentos_comprobatorios": self._normalizar_lista(dados.get("documentos_comprobatorios")),
            "campos_extras": dados.get("campos_extras", {}) if isinstance(dados.get("campos_extras", {}), dict) else {},
        }

    def _normalizar_lista(self, valor: object) -> list[str]:
        if isinstance(valor, list):
            return [str(item).strip() for item in valor if str(item).strip()]
        if isinstance(valor, str) and valor.strip():
            return [valor.strip()]
        return []
