from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


class MetadadosDocumento(BaseModel):
    tipo: str = Field(default="generico")
    fonte: str = Field(default="nao_informado")
    categoria: str = Field(default="nao_informado")
    extras: dict[str, Any] = Field(default_factory=dict)


class DocumentoIngestao(BaseModel):
    id_documento: str
    texto: str
    metadados: MetadadosDocumento = Field(default_factory=MetadadosDocumento)
    base_destino: str = Field(default="base_conhecimento")


class LoteDocumentosIngestao(BaseModel):
    documentos: list[DocumentoIngestao]


class RequisicaoRAG(BaseModel):
    texto_entrada: str
    top_k_conhecimento: int = Field(default=5, ge=1, le=20)
    top_k_templates: int = Field(default=1, ge=1, le=10)
    metadados_filtro: dict[str, Any] = Field(default_factory=dict)


class DadoExtraido(BaseModel):
    numero_art: str = "nao_informado"
    profissional: str = "nao_informado"
    tipo: str = "nao_identificado"
    atividade: str = ""
    contratante: str = "nao_informado"
    local: str = "nao_informado"
    descricao_servico: str = ""
    status_art: str = "nao_informado"
    indicadores_execucao: list[str] = Field(default_factory=list)
    indicadores_conclusao: list[str] = Field(default_factory=list)
    documentos_comprobatorios: list[str] = Field(default_factory=list)
    campos_extras: dict[str, Any] = Field(default_factory=dict)


class ResultadoValidacaoART(BaseModel):
    classificacao: Literal["valido", "incompleto", "inconsistente"]
    pode_gerar_cat: bool
    pendencias: list[str] = Field(default_factory=list)
    inconsistencias: list[str] = Field(default_factory=list)
    evidencias_encontradas: list[str] = Field(default_factory=list)
    justificativa: str


class CATSugerida(BaseModel):
    profissional: str = "nao_informado"
    atividade: str = "nao_informada"
    local: str = "nao_informado"
    art_vinculada: str = "nao_informada"
    situacao: str = "Serviço com pendências"
    observacoes: list[str] = Field(default_factory=list)


class ResultadoBusca(BaseModel):
    id_documento: str
    conteudo: str
    metadados: dict[str, Any] = Field(default_factory=dict)
    distancia: float | None = None


class RespostaRAG(BaseModel):
    dados_extraidos: DadoExtraido
    validacao_art: ResultadoValidacaoART
    contexto_utilizado: list[ResultadoBusca]
    template_utilizado: ResultadoBusca | None = None
    status: Literal["pronta", "pendente", "invalida"]
    motivo: str
    sugestao: str
    cat_sugerida: CATSugerida
    resposta_tecnica: str
