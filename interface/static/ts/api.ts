import { AnalisePayload, AnaliseResposta } from './types';



// Endpoint configurável via variável global (window.ENV_API_URL)
declare global {
  interface Window { ENV_API_URL?: string }
}

export async function enviarAnalise(payload: AnalisePayload): Promise<AnaliseResposta> {
  const endpoint = window.ENV_API_URL || '/analisar';
  const resp = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!resp.ok) throw new Error('Erro ao comunicar com o motor RAGFlow');
  return await resp.json();
}

export function montarPayload(): AnalisePayload {
  return {
    numero_art: (document.getElementById('art_num') as HTMLInputElement).value,
    data_art: (document.getElementById('art_data') as HTMLInputElement).value,
    profissional: (document.getElementById('profissional') as HTMLInputElement).value,
    cpf_prof: (document.getElementById('cpf_prof') as HTMLInputElement).value,
    tipo_servico: (document.getElementById('tipo_servico') as HTMLSelectElement).value,
    endereco_art: (document.getElementById('end_art') as HTMLInputElement).value,
    assinatura: (document.getElementById('assinatura') as HTMLSelectElement).value,
    cpf_contratante: (document.getElementById('cpf_contratante') as HTMLSelectElement).value,
    data_atestado: (document.getElementById('atestado_data') as HTMLInputElement).value,
    cpf_atestado: (document.getElementById('cpf_atestado') as HTMLSelectElement).value,
    endereco_atestado: (document.getElementById('end_atestado') as HTMLInputElement).value
  };
}
