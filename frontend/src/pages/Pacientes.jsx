import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Modal, { Campo } from '../components/Modal'
import {
  getPacientes, criarPaciente,
  getAgendamentos, criarAgendamento, editarAgendamento, excluirAgendamento,
  checkinAgendamento,
} from '../services/api'

const MESES   = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
const DIAS_SW = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb']
const DIAS_LG = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado']
const iniciais = (nome) => nome.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase()

const STATUS_CORES = {
  Confirmado: 'tag-blue',
  Aguardando: 'tag-amber',
  Realizado:  'tag-green',
  Faltou:     'tag-red',
  Cancelado:  'tag-red',
}

const VAZIO_AGD = {
  paciente_nome: '', data: '', horario: '',
  tipo: 'Fisioterapia', profissional: 'Dra. Fernanda Teodoro',
  status: 'Confirmado', observacao: '',
}

const VAZIO_PAC = {
  nome: '', cpf: '', telefone: '', data_nascimento: '', estado_civil: '',
  profissao: '', endereco: '', modalidade: 'Fisioterapia', pagamento_tipo: 'Particular',
  convenio: '', diagnostico_medico: '', queixa_principal: '', diagnostico_fisio: '',
  hs_cirurgia: false, hs_hipertensao: false, hs_diabetes: false, hs_cardiaco: false,
  hs_labirintite: false, hs_fumante: false, hs_perda_peso: false, hs_febre: false,
  hs_vomito: false, hs_trauma: false, hs_osteoporose: false,
  alergia: '', medicacao: '',
}

const HISTORICO = [
  {k:'hs_cirurgia',l:'Cirurgia'},{k:'hs_hipertensao',l:'Hipertensão'},{k:'hs_diabetes',l:'Diabetes'},
  {k:'hs_cardiaco',l:'Prob. cardíaco'},{k:'hs_labirintite',l:'Labirintite'},{k:'hs_fumante',l:'Fumante'},
  {k:'hs_perda_peso',l:'Perda de peso'},{k:'hs_febre',l:'Febre/calafrios'},{k:'hs_vomito',l:'Vômito/náuseas'},
  {k:'hs_trauma',l:'Trauma recente'},{k:'hs_osteoporose',l:'Osteoporose'},
]

export default function Pacientes() {
  const navigate = useNavigate()
  const [pacientes,    setPacientes]    = useState([])
  const [agendamentos, setAgendamentos] = useState([])
  const [busca,        setBusca]        = useState('')
  const [mesAtual, setMesAtual] = useState(() => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), 1) })
  const [diaSel,   setDiaSel]   = useState(null)
  const [pacDia,   setPacDia]   = useState(null)
  const [modalAgd, setModalAgd] = useState(false)
  const [formAgd,  setFormAgd]  = useState(VAZIO_AGD)
  const [editAgdId,setEditAgdId]= useState(null)
  const [modalPac, setModalPac] = useState(false)
  const [formPac,  setFormPac]  = useState(VAZIO_PAC)
  const [stepPac,  setStepPac]  = useState(1)
  const [sugestoes,setSugestoes]= useState([])
  const [mostrarSug,setMostrarSug]=useState(false)

  const carregar = async (a, m) => {
    const anoAtual = a || mesAtual.getFullYear()
    const mesAtual_ = m || (mesAtual.getMonth() + 1)
    const [ps, as] = await Promise.all([getPacientes(), getAgendamentos(anoAtual, mesAtual_)])
    setPacientes(ps)
    setAgendamentos(as)
  }
  useEffect(() => { carregar() }, [mesAtual])

  const ano = mesAtual.getFullYear()
  const mes = mesAtual.getMonth()
  const primeiroDia = new Date(ano, mes, 1).getDay()
  const diasNoMes   = new Date(ano, mes + 1, 0).getDate()
  const hoje        = new Date()

  const agdPorDia = {}
  agendamentos.forEach(a => {
    if (!agdPorDia[a.data]) agdPorDia[a.data] = []
    agdPorDia[a.data].push(a)
  })

  const filtrados = pacientes.filter(p =>
    p.nome.toLowerCase().includes(busca.toLowerCase()) || (p.cpf || '').includes(busca)
  )

  const fa = (k, v) => setFormAgd(p => ({ ...p, [k]: v }))
  const fp = (k, v) => setFormPac(p => ({ ...p, [k]: v }))

  const abrirNovoAgd = () => {
    setFormAgd({ ...VAZIO_AGD, data: diaSel?.key || new Date().toISOString().slice(0,10) })
    setEditAgdId(null); setModalAgd(true)
  }
  const abrirEditAgd = (a, e) => {
    e?.stopPropagation()
    setFormAgd({ paciente_nome: a.paciente_nome, data: a.data, horario: a.horario?.slice(0,5),
      tipo: a.tipo, profissional: a.profissional, status: a.status, observacao: a.observacao || '' })
    setEditAgdId(a.id); setModalAgd(true)
  }
  const salvarAgd = async () => {
    try {
      if (editAgdId) await editarAgendamento(editAgdId, formAgd)
      else await criarAgendamento(formAgd)
      await carregar(); setModalAgd(false)
    } catch(e) { alert(e.message) }
  }
  const excluirAgd = async () => {
    if (!confirm('Excluir este agendamento?')) return
    try { await excluirAgendamento(editAgdId); await carregar(); setModalAgd(false) }
    catch(e) { alert(e.message) }
  }

  const fazerCheckin = async (agd, novoStatus) => {
    try {
      await checkinAgendamento(agd.id, novoStatus)
      await carregar()
      setPacDia(null)
    } catch(e) { alert(e.message) }
  }

  const salvarPac = async () => {
    try {
      await criarPaciente(formPac)
      await carregar(); setModalPac(false); setFormPac(VAZIO_PAC); setStepPac(1)
    } catch(e) { alert(e.message) }
  }

  const filtrarSug = (v) => {
    fa('paciente_nome', v)
    setSugestoes(pacientes.filter(p => p.nome.toLowerCase().includes(v.toLowerCase())))
    setMostrarSug(true)
  }

  const pacienteDetalhe = pacDia ? pacientes.find(p => p.nome === pacDia.paciente_nome) : null

  return (
    <Layout title="Agenda">
      <div className="max-w-3xl mx-auto w-full">

        {/* Barra superior */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mb-4 md:mb-6">
          <input className="input flex-1" placeholder="Buscar paciente…" value={busca} onChange={e => setBusca(e.target.value)} />
          <button className="btn-primary" onClick={() => { setModalPac(true); setStepPac(1) }}>+ Novo Paciente</button>
        </div>

        {/* Resultado da busca */}
        {busca && (
          <div className="card p-0 overflow-hidden mb-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  {['Nome','CPF','Telefone','Modalidade','Status'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-[10px] font-semibold uppercase tracking-widest text-text-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtrados.length === 0 ? (
                  <tr><td colSpan={5} className="text-center text-text-3 py-8">Nenhum paciente encontrado</td></tr>
                ) : filtrados.map(p => (
                  <tr key={p.id} onClick={() => navigate(`/pacientes/${p.id}`)}
                    className="border-b border-border last:border-0 cursor-pointer hover:bg-accent-light/20">
                    <td className="px-4 py-3 font-medium">{p.nome}</td>
                    <td className="px-4 py-3 text-text-2">{p.cpf || '—'}</td>
                    <td className="px-4 py-3 text-text-2">{p.telefone || '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`tag ${p.modalidade==='Fisioterapia'?'tag-green':p.modalidade==='Pilates'?'tag-blue':'tag-amber'}`}>
                        {p.modalidade || '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`tag ${p.status==='Ativo'?'tag-green':'tag-amber'}`}>{p.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Calendário */}
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-text">{MESES[mes]} {ano}</h2>
          <div className="flex gap-2">
            <button className="btn-outline btn-sm" onClick={() => { setMesAtual(new Date(ano,mes-1,1)); setDiaSel(null); setPacDia(null) }}>←</button>
            <button className="btn-outline btn-sm" onClick={() => { setMesAtual(new Date(ano,mes+1,1)); setDiaSel(null); setPacDia(null) }}>→</button>
          </div>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-1">
          {DIAS_SW.map(d => (
            <div key={d} className="text-center text-[10px] font-semibold uppercase tracking-widest text-text-3 py-2">{d}</div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {Array(primeiroDia).fill(null).map((_,i) => <div key={'e'+i} />)}
          {Array(diasNoMes).fill(null).map((_,i) => {
            const d   = i + 1
            const key = `${ano}-${String(mes+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
            const ap  = agdPorDia[key] || []
            const isHoje = hoje.getFullYear()===ano && hoje.getMonth()===mes && hoje.getDate()===d
            const isSel  = diaSel?.key === key
            return (
              <div key={d} onClick={() => { setDiaSel({ key, d, mes }); setPacDia(null) }}
                className={`min-h-[60px] md:min-h-[80px] border rounded-xl p-1.5 cursor-pointer transition-colors
                  ${isSel?'border-accent bg-accent-light/50':isHoje?'border-accent bg-accent-light/20':'border-border bg-surface hover:bg-accent-light/20'}`}>
                <div className={`text-xs font-medium mb-1 ${isHoje||isSel?'text-accent':'text-text'}`}>{d}</div>
                <div className="flex flex-col gap-0.5">
                  {ap.slice(0,2).map((a,i) => (
                    <div key={i} className={`text-[10px] px-1 py-0.5 rounded truncate
                      ${a.status==='Realizado'?'bg-green-50 text-green-700':
                        a.status==='Faltou'||a.status==='Cancelado'?'bg-red-50 text-red-700':
                        a.tipo==='Pilates'?'bg-blue-50 text-blue-700':'bg-accent-light text-accent'}`}>
                      {a.horario?.slice(0,5)} {a.paciente_nome.split(' ')[0]}
                    </div>
                  ))}
                  {ap.length > 2 && <div className="text-[10px] px-1 text-text-3">+{ap.length-2}</div>}
                </div>
              </div>
            )
          })}
        </div>

        {/* Detalhe do dia */}
        {diaSel && (
          <div className="card mt-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-text">
                {DIAS_LG[new Date(diaSel.key+'T12:00').getDay()]}, {diaSel.d} de {MESES[diaSel.mes]}
              </h3>
              <button className="btn-primary btn-sm" onClick={abrirNovoAgd}>+ Novo agendamento</button>
            </div>

            {(agdPorDia[diaSel.key] || []).length === 0 ? (
              <p className="text-sm text-text-3">Nenhum agendamento para este dia.</p>
            ) : (
              <div className="flex flex-col gap-2">
                {(agdPorDia[diaSel.key] || []).map(a => (
                  <div key={a.id} onClick={() => setPacDia(pacDia?.id===a.id ? null : a)}
                    className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition-colors
                      ${pacDia?.id===a.id?'border-accent bg-accent-light/40':'border-border hover:bg-accent-light/20'}`}>
                    <div className="w-9 h-9 rounded-full bg-accent-light flex items-center justify-center text-accent text-xs font-bold flex-shrink-0">
                      {iniciais(a.paciente_nome)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-text">{a.paciente_nome}</div>
                      <div className="text-xs text-text-3 mt-0.5">{a.tipo} · {a.profissional}</div>
                    </div>
                    <span className="text-sm font-semibold text-accent">{a.horario?.slice(0,5)}</span>
                    <span className={`tag text-[10px] ${STATUS_CORES[a.status] || 'tag-blue'}`}>{a.status}</span>
                    <button onClick={e => abrirEditAgd(a,e)} className="text-xs text-text-3 hover:text-accent ml-1">✏️</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Resumo do paciente + check-in */}
        {pacDia && (
          <div className="card mt-4 border-accent/40">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-full bg-accent-light flex items-center justify-center text-accent font-bold text-sm">
                  {iniciais(pacDia.paciente_nome)}
                </div>
                <div>
                  <h3 className="font-semibold text-text">{pacDia.paciente_nome}</h3>
                  <div className="text-xs text-text-3 mt-0.5">{pacDia.horario?.slice(0,5)} · {pacDia.tipo} · {pacDia.profissional}</div>
                  <span className={`tag text-[10px] mt-1 inline-block ${STATUS_CORES[pacDia.status] || 'tag-blue'}`}>{pacDia.status}</span>
                </div>
              </div>
              <button className="btn-outline btn-sm" onClick={() => setPacDia(null)}>✕</button>
            </div>

            {/* Botões de check-in */}
            {(pacDia.status === 'Confirmado' || pacDia.status === 'Aguardando') && (
              <div className="flex gap-2 mb-4">
                <button onClick={() => fazerCheckin(pacDia, 'Realizado')}
                  className="flex-1 bg-accent text-white text-sm font-medium py-2 rounded-xl hover:bg-accent-hover transition-colors">
                  ✓ Marcar como Realizado
                </button>
                <button onClick={() => fazerCheckin(pacDia, 'Faltou')}
                  className="flex-1 bg-red-50 border border-red-200 text-red-700 text-sm font-medium py-2 rounded-xl hover:bg-red-100 transition-colors">
                  ✗ Marcar Faltou
                </button>
              </div>
            )}

            {pacienteDetalhe && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3">
                {[['CPF',pacienteDetalhe.cpf],['Telefone',pacienteDetalhe.telefone],
                  ['Modalidade',pacienteDetalhe.modalidade],['Pagamento',pacienteDetalhe.pagamento_tipo],
                  ['Diagnóstico',pacienteDetalhe.diagnostico_medico],['Queixa',pacienteDetalhe.queixa_principal]]
                  .filter(([,v])=>v).map(([label,val])=>(
                  <div key={label}>
                    <div className="text-[10px] font-semibold uppercase tracking-widest text-text-3 mb-0.5">{label}</div>
                    <div className="text-sm text-text">{val}</div>
                  </div>
                ))}
              </div>
            )}

            {pacienteDetalhe && (
              <button onClick={() => navigate(`/pacientes/${pacienteDetalhe.id}`)}
                className="btn-primary btn-sm mt-4">Ver ficha completa</button>
            )}
          </div>
        )}
      </div>

      {/* Modal agendamento */}
      <Modal aberto={modalAgd} onFechar={() => setModalAgd(false)}
        titulo={editAgdId ? 'Editar Agendamento' : 'Novo Agendamento'}
        subtitulo="Dra. Fernanda Teodoro"
        rodape={
          <>
            {editAgdId && <button className="btn-danger" onClick={excluirAgd}>Excluir</button>}
            <div className="flex gap-2 ml-auto">
              <button className="btn-outline" onClick={() => setModalAgd(false)}>Cancelar</button>
              <button className="btn-primary" onClick={salvarAgd}>Salvar</button>
            </div>
          </>
        }>
        <Campo label="Paciente">
          <div className="relative">
            <input className="input" value={formAgd.paciente_nome}
              onChange={e => filtrarSug(e.target.value)}
              onFocus={() => { setSugestoes(pacientes); setMostrarSug(true) }}
              onBlur={() => setTimeout(() => setMostrarSug(false), 150)}
              placeholder="Digite ou selecione…" />
            {mostrarSug && sugestoes.length > 0 && (
              <div className="absolute top-full left-0 right-0 bg-surface border border-border rounded-xl shadow-lg z-50 max-h-44 overflow-y-auto mt-1">
                {sugestoes.map(p => (
                  <div key={p.id} onMouseDown={() => { fa('paciente_nome', p.nome); setMostrarSug(false) }}
                    className="px-3 py-2.5 text-sm cursor-pointer hover:bg-accent-light/50">{p.nome}</div>
                ))}
              </div>
            )}
          </div>
        </Campo>
        <div className="grid grid-cols-2 gap-3">
          <Campo label="Data"><input className="input" type="date" value={formAgd.data} onChange={e => fa('data', e.target.value)} /></Campo>
          <Campo label="Horário"><input className="input" type="time" value={formAgd.horario} onChange={e => fa('horario', e.target.value)} /></Campo>
        </div>
        <Campo label="Tipo">
          <select className="input" value={formAgd.tipo} onChange={e => fa('tipo', e.target.value)}>
            <option>Fisioterapia</option><option>Pilates</option>
          </select>
        </Campo>
        <Campo label="Status">
          <select className="input" value={formAgd.status} onChange={e => fa('status', e.target.value)}>
            <option>Confirmado</option><option>Aguardando</option>
            <option>Realizado</option><option>Faltou</option><option>Cancelado</option>
          </select>
        </Campo>
        <Campo label="Observação">
          <input className="input" value={formAgd.observacao} onChange={e => fa('observacao', e.target.value)} placeholder="Opcional" />
        </Campo>
      </Modal>

      {/* Modal novo paciente */}
      <Modal aberto={modalPac} onFechar={() => { setModalPac(false); setStepPac(1) }}
        titulo="Novo Paciente"
        subtitulo={`Passo ${stepPac} de 3 — ${stepPac===1?'Dados pessoais':stepPac===2?'Informações clínicas':'Histórico de saúde'}`}
        rodape={
          <div className="flex gap-2 ml-auto">
            <button className="btn-outline" onClick={() => stepPac===1 ? setModalPac(false) : setStepPac(s=>s-1)}>
              {stepPac===1 ? 'Cancelar' : 'Voltar'}
            </button>
            {stepPac < 3
              ? <button className="btn-primary" onClick={() => setStepPac(s=>s+1)}>Continuar →</button>
              : <button className="btn-primary" onClick={salvarPac}>Salvar paciente</button>
            }
          </div>
        }>
        {stepPac===1 && (<>
          <Campo label="Nome completo *"><input className="input" value={formPac.nome} onChange={e=>fp('nome',e.target.value)} /></Campo>
          <div className="grid grid-cols-2 gap-3">
            <Campo label="CPF"><input className="input" value={formPac.cpf} onChange={e=>fp('cpf',e.target.value)} /></Campo>
            <Campo label="Telefone"><input className="input" value={formPac.telefone} onChange={e=>fp('telefone',e.target.value)} /></Campo>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Campo label="Nascimento"><input className="input" type="date" value={formPac.data_nascimento} onChange={e=>fp('data_nascimento',e.target.value)} /></Campo>
            <Campo label="Estado Civil">
              <select className="input" value={formPac.estado_civil} onChange={e=>fp('estado_civil',e.target.value)}>
                <option value="">Selecione</option>
                {['Solteiro(a)','Casado(a)','Divorciado(a)','Viúvo(a)','União estável'].map(o=><option key={o}>{o}</option>)}
              </select>
            </Campo>
          </div>
          <Campo label="Profissão"><input className="input" value={formPac.profissao} onChange={e=>fp('profissao',e.target.value)} /></Campo>
          <Campo label="Endereço"><input className="input" value={formPac.endereco} onChange={e=>fp('endereco',e.target.value)} /></Campo>
        </>)}
        {stepPac===2 && (<>
          <div className="grid grid-cols-3 gap-3">
            <Campo label="Modalidade">
              <select className="input" value={formPac.modalidade} onChange={e=>fp('modalidade',e.target.value)}>
                <option>Fisioterapia</option><option>Pilates</option><option>Ambos</option>
              </select>
            </Campo>
            <Campo label="Pagamento">
              <select className="input" value={formPac.pagamento_tipo} onChange={e=>fp('pagamento_tipo',e.target.value)}>
                <option>Particular</option><option>Convênio</option><option>Ambos</option>
              </select>
            </Campo>
            <Campo label="Convênio"><input className="input" value={formPac.convenio} onChange={e=>fp('convenio',e.target.value)} /></Campo>
          </div>
          <Campo label="Diagnóstico Médico"><input className="input" value={formPac.diagnostico_medico} onChange={e=>fp('diagnostico_medico',e.target.value)} /></Campo>
          <Campo label="Queixa Principal"><textarea className="input resize-none" rows={2} value={formPac.queixa_principal} onChange={e=>fp('queixa_principal',e.target.value)} /></Campo>
          <Campo label="Diagnóstico Fisioterapêutico"><textarea className="input resize-none" rows={2} value={formPac.diagnostico_fisio} onChange={e=>fp('diagnostico_fisio',e.target.value)} /></Campo>
        </>)}
        {stepPac===3 && (<>
          <div className="grid grid-cols-2 gap-2">
            {HISTORICO.map(({k,l})=>(
              <label key={k} className="flex items-center gap-2 text-sm text-text-2 cursor-pointer">
                <input type="checkbox" checked={!!formPac[k]} onChange={e=>fp(k,e.target.checked)} className="w-4 h-4 accent-accent" />{l}
              </label>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3 mt-2">
            <Campo label="Alergia"><input className="input" value={formPac.alergia} onChange={e=>fp('alergia',e.target.value)} /></Campo>
            <Campo label="Medicação"><input className="input" value={formPac.medicacao} onChange={e=>fp('medicacao',e.target.value)} /></Campo>
          </div>
        </>)}
      </Modal>
    </Layout>
  )
}
