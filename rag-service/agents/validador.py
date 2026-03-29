from models.excecoes import ErroValidacaoART
from models.schemas import DadoExtraido, ResultadoValidacaoART


class AgenteValidadorART:
    _TIPOS_VALIDOS = {
        "obra",
        "serviço",
        "servico",
        "obra/serviço",
        "obra/servico",
        "obra-serviço",
        "obra-servico",
    }

    _STATUS_CONCLUSAO = {
        "baixada",
        "baixa",
        "finalizada",
        "finalizado",
        "concluída",
        "concluida",
        "concluído",
        "concluido",
        "encerrada",
        "encerrado",
    }

    def validar(self, dados_art: DadoExtraido) -> ResultadoValidacaoART:
        if not isinstance(dados_art, DadoExtraido):
            raise ErroValidacaoART("Dados da ART em formato inválido")

        pendencias: list[str] = []
        inconsistencias: list[str] = []
        evidencias: list[str] = []

        tipo_normalizado = dados_art.tipo.strip().lower()
        atividade_informada = bool(dados_art.atividade.strip())
        local_informado = bool(dados_art.local.strip() and dados_art.local.strip().lower() != "nao_informado")

        if tipo_normalizado not in self._TIPOS_VALIDOS:
            inconsistencias.append("Tipo de ART inválido ou não reconhecido para emissão de CAT.")

        if not atividade_informada:
            inconsistencias.append("Atividade técnica não informada.")

        if not local_informado:
            pendencias.append("Local de execução não informado.")

        if dados_art.indicadores_execucao:
            evidencias.extend(dados_art.indicadores_execucao)
        elif dados_art.descricao_servico.strip():
            evidencias.append("Descrição de execução presente na ART.")
        else:
            pendencias.append("Não há evidência de execução do serviço técnico.")

        texto_status = dados_art.status_art.strip().lower()
        ha_conclusao = any(palavra in texto_status for palavra in self._STATUS_CONCLUSAO) or bool(
            dados_art.indicadores_conclusao
        )

        if dados_art.indicadores_conclusao:
            evidencias.extend(dados_art.indicadores_conclusao)

        if not ha_conclusao:
            pendencias.append("Ausência de indicação de conclusão/baixa da ART.")

        if dados_art.documentos_comprobatorios:
            evidencias.extend(dados_art.documentos_comprobatorios)
        else:
            pendencias.append("Ausência de documentos comprobatórios (laudo, contrato ou declaração).")

        if inconsistencias:
            return ResultadoValidacaoART(
                classificacao="inconsistente",
                pode_gerar_cat=False,
                pendencias=pendencias,
                inconsistencias=inconsistencias,
                evidencias_encontradas=evidencias,
                justificativa="ART inconsistente para análise automática de CAT.",
            )

        if pendencias:
            return ResultadoValidacaoART(
                classificacao="incompleto",
                pode_gerar_cat=False,
                pendencias=pendencias,
                inconsistencias=[],
                evidencias_encontradas=evidencias,
                justificativa="ART parcialmente válida, mas com pendências para emissão da CAT.",
            )

        return ResultadoValidacaoART(
            classificacao="valido",
            pode_gerar_cat=True,
            pendencias=[],
            inconsistencias=[],
            evidencias_encontradas=evidencias,
            justificativa="ART válida, concluída e com evidências suficientes para CAT.",
        )
