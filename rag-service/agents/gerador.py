from models.excecoes import ErroGeracaoResposta
from models.schemas import CATSugerida, DadoExtraido, ResultadoBusca, ResultadoValidacaoART
from services.cliente_ai import ClienteAI


class AgenteGerador:
    def __init__(self, cliente_ai: ClienteAI):
        self.cliente_ai = cliente_ai

    def gerar(
        self,
        dados_extraidos: DadoExtraido,
        validacao_art: ResultadoValidacaoART,
        cat_sugerida: CATSugerida,
        status: str,
        motivo: str,
        sugestao: str,
        contexto: list[ResultadoBusca],
        template: ResultadoBusca | None,
    ) -> str:
        contexto_texto = "\n\n".join(item.conteudo for item in contexto)
        template_texto = template.conteudo if template else "Sem template específico."

        prompt = (
            "Você é um avaliador técnico do CREA para análise de elegibilidade da CAT. "
            "Com base nos dados da ART, validação lógica e contexto recuperado, "
            "gere um parecer curto com: decisão, justificativa e próximos passos.\n\n"
            f"Status final: {status}\n"
            f"Motivo: {motivo}\n"
            f"Sugestão: {sugestao}\n\n"
            f"Dados ART: {dados_extraidos.model_dump_json(ensure_ascii=False)}\n\n"
            f"Validação ART: {validacao_art.model_dump_json(ensure_ascii=False)}\n\n"
            f"CAT sugerida: {cat_sugerida.model_dump_json(ensure_ascii=False)}\n\n"
            f"Template sugerido: {template_texto}\n\n"
            f"Contexto recuperado: {contexto_texto}\n"
        )

        resposta = self.cliente_ai.gerar_resposta(prompt)
        if not resposta.strip():
            raise ErroGeracaoResposta("Modelo retornou resposta vazia")
        return resposta
