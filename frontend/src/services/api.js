const BASE = '/api'

async function request(url, options = {}) {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok && res.status !== 204) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.message || `Erro ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

// Auth
export const login = (usuario, senha) =>
  request('/login/', { method: 'POST', body: JSON.stringify({ usuario, senha }) })

// Dashboard
export const getDashboard = () => request('/dashboard/')

// Pacientes
export const getPacientes    = (q = '')       => request(`/pacientes/${q ? `?q=${encodeURIComponent(q)}` : ''}`)
export const getPaciente     = (id)           => request(`/pacientes/${id}/`)
export const criarPaciente   = (data)         => request('/pacientes/', { method: 'POST', body: JSON.stringify(data) })
export const editarPaciente  = (id, data)     => request(`/pacientes/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
export const excluirPaciente = (id)           => request(`/pacientes/${id}/`, { method: 'DELETE' })

// Agendamentos
export const getAgendamentos    = (ano, mes) => request(`/agendamentos/${ano && mes ? `?ano=${ano}&mes=${mes}` : ''}`)
export const criarAgendamento   = (data)      => request('/agendamentos/', { method: 'POST', body: JSON.stringify(data) })
export const editarAgendamento  = (id, data)  => request(`/agendamentos/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
export const excluirAgendamento = (id)        => request(`/agendamentos/${id}/`, { method: 'DELETE' })
export const checkinAgendamento = (id, status) =>
  request(`/agendamentos/${id}/checkin/`, { method: 'PUT', body: JSON.stringify({ status }) })

// Pacotes
export const getPacotes    = (pacienteId)     => request(`/pacotes/${pacienteId ? `?paciente_id=${pacienteId}` : ''}`)
export const criarPacote   = (data)           => request('/pacotes/', { method: 'POST', body: JSON.stringify(data) })
export const editarPacote  = (id, data)       => request(`/pacotes/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
export const excluirPacote = (id)             => request(`/pacotes/${id}/`, { method: 'DELETE' })

// Lançamentos
export const getLancamentos = (params = {}) => {
  const p = {}
  if (params.ano)    p.ano    = String(parseInt(params.ano,    10))
  if (params.mes)    p.mes    = String(parseInt(params.mes,    10))
  if (params.tipo)   p.tipo   = params.tipo
  if (params.status) p.status = params.status
  const q = new URLSearchParams(p).toString()
  return request(`/lancamentos/${q ? '?' + q : ''}`)
}
export const criarLancamento   = (data)       => request('/lancamentos/', { method: 'POST', body: JSON.stringify(data) })
export const editarLancamento  = (id, data)   => request(`/lancamentos/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
export const excluirLancamento = (id)         => request(`/lancamentos/${id}/`, { method: 'DELETE' })
export const marcarPago        = (id)         => request(`/lancamentos/${id}/pagar/`, { method: 'PUT' })

// Evoluções
export const criarEvolucao  = (data)          => request('/evolucoes/', { method: 'POST', body: JSON.stringify(data) })
export const excluirEvolucao= (id)            => request(`/evolucoes/${id}/`, { method: 'DELETE' })

// Exames PDF
export const uploadExame  = (formData) =>
  fetch(BASE + '/exames/upload/', { method: 'POST', body: formData }).then(r => r.json())
export const excluirExame = (id)              => request(`/exames/${id}/`, { method: 'DELETE' })

// Usuários
export const getUsuarios    = ()              => request('/usuarios/')
export const criarUsuario   = (data)          => request('/usuarios/', { method: 'POST', body: JSON.stringify(data) })
export const editarUsuario  = (id, data)      => request(`/usuarios/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
export const excluirUsuario = (id)            => request(`/usuarios/${id}/`, { method: 'DELETE' })

// Importar ficha com IA
export const importarFicha = (formData) =>
  fetch(BASE + '/importar-ficha/', { method: 'POST', body: formData }).then(async r => {
    const data = await r.json()
    if (!r.ok) throw new Error(data.message || `Erro ${r.status}`)
    return data
  })
