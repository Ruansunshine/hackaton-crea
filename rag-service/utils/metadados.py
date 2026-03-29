# Função utilitária para normalizar e extrair metadados relevantes de DadoExtraido
from models.schemas import DadoExtraido

def extrair_metadados_para_ragflow(dado: DadoExtraido) -> dict:
    return {
        "assinaturas": dado.campos_extras.get("assinaturas", []),
        "engenheiro_civil_contratante": dado.campos_extras.get("engenheiro_civil_contratante", False),
        "cpf_contratante": dado.campos_extras.get("cpf_contratante", None),
        "data_atestado": dado.campos_extras.get("data_atestado", None),
        "data_art": dado.campos_extras.get("data_art", None),
        "local_art": dado.local,
        "local_atestado": dado.campos_extras.get("local_atestado", None),
        "endereco_atestado": dado.campos_extras.get("endereco_atestado", None),
        "endereco_art": dado.campos_extras.get("endereco_art", None),
        # Adicione outros campos relevantes conforme necessário
    }
