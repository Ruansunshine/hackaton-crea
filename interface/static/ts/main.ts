import { montarPayload, enviarAnalise } from './api';
import { AnaliseResposta } from './types';

function set(id: string, val: string) {
  (document.getElementById(id) as HTMLInputElement | HTMLSelectElement).value = val;
}

(window as any).loadPreset = function(tipo: string, el: HTMLElement) {
  document.querySelectorAll('.preset').forEach(p => p.classList.remove('active'));
  if (el) el.classList.add('active');
  if (tipo === 'pendente') {
    set('assinatura', 'nao');
    set('cpf_contratante', 'sim');
    set('art_data', '2025-10-30');
    set('atestado_data', '2025-10-30');
    set('end_art', 'Zona Rural, Lote 14, Município de São Domingos do Maranhão – MA');
    set('end_atestado', 'Zona Rural, Lote 14, Município de São Domingos do Maranhão – MA');
    set('cpf_atestado', 'sim');
  } else if (tipo === 'divergencia') {
    set('assinatura', 'sim');
    set('cpf_contratante', 'sim');
    set('art_data', '2025-10-30');
    set('atestado_data', '2025-12-19');
    set('end_art', 'Zona Rural, Lote 14, Município de São Domingos do Maranhão – MA');
    set('end_atestado', 'Rua Central, s/n, São Domingos – MA');
    set('cpf_atestado', 'sim');
  } else {
    set('assinatura', 'sim');
    set('cpf_contratante', 'sim');
    set('art_data', '2025-10-30');
    set('atestado_data', '2025-10-30');
    set('end_art', 'Zona Rural, Lote 14, Município de São Domingos do Maranhão – MA');
    set('end_atestado', 'Zona Rural, Lote 14, Município de São Domingos do Maranhão – MA');
    set('cpf_atestado', 'sim');
  }
};

(window as any).enviarAnalise = async function() {
  document.getElementById('empty-state')!.style.display = 'none';
  const ra = document.getElementById('result-area')!;
  ra.style.display = 'block';
  ra.innerHTML = `<div class="processing-msg" id="proc-msg"><div class="spinner"></div>Enviando para o motor RAGFlow...</div>`;
  try {
    const payload = montarPayload();
    const resposta: AnaliseResposta = await enviarAnalise(payload);
    document.getElementById('proc-msg')!.style.display = 'none';
    ra.innerHTML += `<div class="json-wrap"><div class="json-header"><div class="json-title">Saída do motor RAGFlow</div></div><div class="json-body">${JSON.stringify(resposta, null, 2)}</div></div>`;
  } catch (e: any) {
    document.getElementById('proc-msg')!.style.display = 'none';
    ra.innerHTML += `<div style='color:var(--red);margin-top:20px;'>Erro ao comunicar com o motor: ${e.message || e}</div>`;
  }
};
