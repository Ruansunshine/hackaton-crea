// types.ts
export interface AnalisePayload {
  numero_art: string;
  data_art: string;
  profissional: string;
  cpf_prof: string;
  tipo_servico: string;
  endereco_art: string;
  assinatura: string;
  cpf_contratante: string;
  data_atestado: string;
  cpf_atestado: string;
  endereco_atestado: string;
}

export interface AnaliseResposta {
  status_geral: string;
  art?: string;
  analise: Array<{
    tipo: string;
    categoria?: string;
    descricao: string;
    acao?: string;
  }>;
  confianca: string;
  [key: string]: any;
}
