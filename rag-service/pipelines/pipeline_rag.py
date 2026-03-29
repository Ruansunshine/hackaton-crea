
from loguru import logger
from agents.extrator import AgenteExtrator
from agents.gerador import AgenteGerador
from agents.validador import AgenteValidadorART
from models.excecoes import ErroBuscaVetorial, ErroExtracaoDados, ErroGeracaoResposta, ErroValidacaoART
from models.schemas import CATSugerida, DadoExtraido, RequisicaoRAG, RespostaRAG, ResultadoValidacaoART
from retrieval.buscador import Buscador
from retrieval.buscador_template import BuscadorTemplate
from services.motor_regras_ragflow import MotorRegrasRAGFlow
from utils.metadados import extrair_metadados_para_ragflow
import os


class PipelineRAG:
    def __init__(
        self,
        extrator: AgenteExtrator,
        validador: AgenteValidadorART,
        buscador: Buscador,
        buscador_template: BuscadorTemplate,
        gerador: AgenteGerador,
        caminho_regras: str = None,
    ):
        self.extrator = extrator
        self.validador = validador
        self.buscador = buscador
        self.buscador_template = buscador_template
        self.gerador = gerador
        if caminho_regras is None:
            caminho_regras = os.path.join(os.path.dirname(__file__), '../config/regras_ragflow.yaml')
        self.motor_regras = MotorRegrasRAGFlow(os.path.abspath(caminho_regras))

    def executar(self, requisicao: RequisicaoRAG) -> RespostaRAG:
        dados_extraidos = self._extrair_com_fallback(requisicao.texto_entrada)
        validacao_art = self._validar_art_com_fallback(dados_extraidos)
        status = self._inferir_status(validacao_art)
        cat_sugerida = self._montar_cat_sugerida(dados_extraidos, validacao_art)
        motivo = validacao_art.justificativa
        sugestao = self._gerar_sugestao(validacao_art)

        # --- NOVO: Análise de metadados e regras dinâmicas ---
        metadados = extrair_metadados_para_ragflow(dados_extraidos)
        resultado_analise = self.motor_regras.analisar(metadados)

        contexto = self._buscar_contexto_com_fallback(
            texto_consulta=dados_extraidos.descricao_servico or requisicao.texto_entrada,
            top_k=requisicao.top_k_conhecimento,
            metadados_filtro=requisicao.metadados_filtro,
        )
        template = self._buscar_template_com_fallback(
            texto_consulta=dados_extraidos.descricao_servico or requisicao.texto_entrada,
            top_k=requisicao.top_k_templates,
        )
        resposta = self._gerar_resposta_com_fallback(
            dados_extraidos=dados_extraidos,
            validacao_art=validacao_art,
            cat_sugerida=cat_sugerida,
            status=status,
            motivo=motivo,
            sugestao=sugestao,
            contexto=contexto,
            template=template,
        )

        # --- Fim do bloco de análise de metadados ---

        # A resposta estruturada do motor RAGFlow pode ser retornada junto ou integrada à resposta final
        # Aqui, apenas logando para debug, mas pode ser retornada conforme necessidade
        logger.debug(f"Diagnóstico estruturado RAGFlow: {resultado_analise}")

        return RespostaRAG(
            dados_extraidos=dados_extraidos,
            validacao_art=validacao_art,
            contexto_utilizado=contexto,
            template_utilizado=template,
            status=status,
            motivo=motivo,
            sugestao=sugestao,
            cat_sugerida=cat_sugerida,
            resposta_tecnica=resposta,
            # resultado_analise pode ser adicionado ao modelo se desejar
        )

    def _extrair_com_fallback(self, texto_entrada: str) -> DadoExtraido:
        try:
            return self.extrator.extrair(texto_entrada)
        except ErroExtracaoDados as erro:
            logger.warning("Extração falhou, ativando fallback: {}", str(erro))
            return DadoExtraido(
                numero_art="nao_informado",
                profissional="nao_informado",
                tipo="nao_identificado",
                atividade="",
                contratante="nao_informado",
                local="nao_informado",
                descricao_servico=texto_entrada[:500],
                status_art="nao_informado",
                campos_extras={"fallback": "extracao"},
            )

    def _validar_art_com_fallback(self, dados_extraidos: DadoExtraido) -> ResultadoValidacaoART:
        try:
            return self.validador.validar(dados_extraidos)
        except ErroValidacaoART as erro:
            logger.warning("Validação falhou, classificando como inconsistente: {}", str(erro))
            return ResultadoValidacaoART(
                classificacao="inconsistente",
                pode_gerar_cat=False,
                pendencias=["Não foi possível completar a validação automática da ART."],
                inconsistencias=["Falha técnica na camada de validação."],
                evidencias_encontradas=[],
                justificativa="ART não pôde ser validada automaticamente.",
            )

    def _buscar_contexto_com_fallback(self, texto_consulta: str, top_k: int, metadados_filtro: dict):
        try:
            return self.buscador.buscar(
                texto_consulta=texto_consulta,
                top_k=top_k,
                metadados_filtro=metadados_filtro,
            )
        except ErroBuscaVetorial as erro:
            logger.warning("Busca vetorial falhou, retornando contexto vazio: {}", str(erro))
            return []

    def _buscar_template_com_fallback(self, texto_consulta: str, top_k: int):
        try:
            return self.buscador_template.buscar_melhor_template(texto_consulta=texto_consulta, top_k=top_k)
        except ErroBuscaVetorial as erro:
            logger.warning("Busca de template falhou, seguindo sem template: {}", str(erro))
            return None

    def _gerar_resposta_com_fallback(
        self,
        dados_extraidos: DadoExtraido,
        validacao_art: ResultadoValidacaoART,
        cat_sugerida: CATSugerida,
        status: str,
        motivo: str,
        sugestao: str,
        contexto,
        template,
    ) -> str:
        try:
            return self.gerador.gerar(
                dados_extraidos=dados_extraidos,
                validacao_art=validacao_art,
                cat_sugerida=cat_sugerida,
                status=status,
                motivo=motivo,
                sugestao=sugestao,
                contexto=contexto,
                template=template,
            )
        except ErroGeracaoResposta as erro:
            logger.warning("Geração falhou, ativando fallback textual: {}", str(erro))
            return (
                "Não foi possível gerar resposta técnica completa neste momento. "
                "Dados extraídos e contexto foram preservados para revisão manual."
            )

    def _inferir_status(self, validacao: ResultadoValidacaoART) -> str:
        if validacao.classificacao == "inconsistente":
            return "invalida"
        if validacao.pode_gerar_cat:
            return "pronta"
        return "pendente"

    def _gerar_sugestao(self, validacao: ResultadoValidacaoART) -> str:
        if validacao.classificacao == "valido":
            return "CAT pronta para protocolo no CREA."
        itens = validacao.pendencias + validacao.inconsistencias
        if not itens:
            return "Revisar ART e anexar evidências complementares para análise."
        return "; ".join(itens[:3])

    def _montar_cat_sugerida(self, dados: DadoExtraido, validacao: ResultadoValidacaoART) -> CATSugerida:
        situacao = "Serviço concluído" if validacao.classificacao == "valido" else "Serviço com pendências"
        observacoes = validacao.pendencias + validacao.inconsistencias
        return CATSugerida(
            profissional=dados.profissional,
            atividade=dados.atividade or "nao_informada",
            local=dados.local,
            art_vinculada=dados.numero_art,
            situacao=situacao,
            observacoes=observacoes,
        )
