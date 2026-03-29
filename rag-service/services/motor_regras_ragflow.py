import yaml
from pathlib import Path
from typing import Any

class MotorRegrasRAGFlow:
    def __init__(self, caminho_regras: str):
        self.caminho_regras = caminho_regras
        self.regras = self._carregar_regras()

    def _carregar_regras(self) -> list[dict[str, Any]]:
        with open(self.caminho_regras, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data.get('regras', [])

    def analisar(self, metadados: dict[str, Any]) -> dict:
        analise = []
        status_geral = "pronta"
        confianca = "alta"
        for regra in self.regras:
            resultado = self._aplicar_regra(regra, metadados)
            if resultado:
                analise.append(resultado)
                if resultado['tipo'] == 'pendencia':
                    status_geral = "PENDENTE"
                elif resultado['tipo'] == 'divergencia':
                    status_geral = "DIVERGENTE"
        if not analise:
            status_geral = "pronta"
        return {
            "status_geral": status_geral,
            "analise": analise,
            "confianca": confianca
        }

    def _aplicar_regra(self, regra: dict, metadados: dict[str, Any]) -> dict | None:
        cond = regra['condicao']
        campo = cond['campo']
        tipo = cond['tipo']
        # Exemplo de lógica simplificada para algumas regras
        if tipo == 'ausencia':
            if not metadados.get(campo):
                return {
                    "tipo": regra['acao']['tipo'],
                    "descricao": regra['descricao'],
                    "acao": regra['acao']['mensagem']
                }
            elif 'acao_sanado' in regra:
                return {
                    "tipo": regra['acao_sanado']['tipo'],
                    "descricao": regra['acao_sanado']['mensagem']
                }
        elif tipo == 'divergencia':
            campos = cond.get('campos_relacionados', [])
            valores = [metadados.get(c, None) for c in campos]
            if len(set(valores)) > 1:
                return {
                    "tipo": regra['acao']['tipo'],
                    "categoria": regra['acao'].get('categoria'),
                    "descricao": regra['acao']['mensagem']
                }
            elif 'acao_sanado' in regra:
                return {
                    "tipo": regra['acao_sanado']['tipo'],
                    "descricao": regra['acao_sanado']['mensagem']
                }
        elif tipo == 'incompleto':
            campos = cond.get('campos_relacionados', [])
            valores = [metadados.get(c, None) for c in campos]
            if any(v is None or v == '' for v in valores):
                return {
                    "tipo": regra['acao']['tipo'],
                    "descricao": regra['acao']['mensagem']
                }
        return None
