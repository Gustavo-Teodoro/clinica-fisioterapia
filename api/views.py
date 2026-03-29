from datetime import date
from decimal import Decimal
import hashlib
import base64
import json

from django.db.models import Sum, Q
from django.conf import settings

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Paciente, Agendamento, Evolucao, Lancamento, ExamePDF, Usuario, Pacote
from .serializers import (
    PacienteListSerializer, PacienteDetalheSerializer,
    AgendamentoSerializer, LancamentoSerializer,
    EvolucaoSerializer, ExamePDFSerializer, UsuarioSerializer, PacoteSerializer,
)


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def _parse_int(valor, default):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return default


# ── AUTH ─────────────────────────────────────────────────────────────────

@api_view(['POST'])
def login(request):
    usuario = request.data.get('usuario', '').strip()
    senha   = request.data.get('senha', '')
    try:
        u = Usuario.objects.get(usuario=usuario, ativo=True)
        if u.senha == hash_senha(senha) or u.senha == senha:
            if u.senha == senha:
                u.senha = hash_senha(senha)
                u.save()
            return Response({'success': True, 'usuario': u.usuario, 'nome': u.nome, 'perfil': u.perfil})
    except Usuario.DoesNotExist:
        pass
    return Response({'success': False, 'message': 'Usuário ou senha incorretos.'}, status=401)


# ── USUÁRIOS ──────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def usuarios_list(request):
    if request.method == 'GET':
        return Response(UsuarioSerializer(Usuario.objects.all(), many=True).data)

    data = request.data.copy()
    if 'senha' in data and data['senha']:
        data['senha'] = hash_senha(data['senha'])

    serializer = UsuarioSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
def usuario_detail(request, pk):
    try:
        u = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response({'message': 'Usuário não encontrado.'}, status=404)

    if request.method == 'PUT':
        data = request.data.copy()
        if 'senha' in data and data['senha']:
            data['senha'] = hash_senha(data['senha'])
        else:
            data.pop('senha', None)
        serializer = UsuarioSerializer(u, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if u.perfil == 'admin' and Usuario.objects.filter(perfil='admin', ativo=True).count() <= 1:
        return Response({'message': 'Não é possível excluir o único administrador.'}, status=400)
    u.delete()
    return Response(status=204)


# ── DASHBOARD ────────────────────────────────────────────────────────────

@api_view(['GET'])
def dashboard(request):
    hoje = date.today()

    total_pacientes = Paciente.objects.count()
    consultas_hoje  = Agendamento.objects.filter(data=hoje).count()
    fisio_hoje      = Agendamento.objects.filter(data=hoje, tipo='Fisioterapia').count()
    pilates_hoje    = Agendamento.objects.filter(data=hoje, tipo='Pilates').count()
    pendentes_fin   = Lancamento.objects.filter(status='Pendente').count()

    receita_mes = Lancamento.objects.filter(
        tipo='Receita', data__year=hoje.year, data__month=hoje.month
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    despesa_mes = Lancamento.objects.filter(
        tipo='Despesa', data__year=hoje.year, data__month=hoje.month
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    agendamentos_hoje = Agendamento.objects.filter(data=hoje).order_by('horario')

    # Alertas inteligentes
    alertas = []

    # Pacotes com menos de 20% de sessões restantes
    pacotes_criticos = Pacote.objects.filter(status='Ativo').select_related('paciente')
    for p in pacotes_criticos:
        if p.total_sessoes > 0 and p.sessoes_restantes <= max(1, p.total_sessoes * 0.2):
            alertas.append({
                'tipo': 'pacote',
                'nivel': 'aviso',
                'mensagem': f'{p.paciente.nome} — apenas {p.sessoes_restantes} sessão(ões) restante(s) no pacote de {p.tipo}',
                'paciente_id': p.paciente.id,
            })

    # Pacotes vencidos
    pacotes_vencidos = Pacote.objects.filter(status='Ativo', data_vencimento__lt=hoje).select_related('paciente')
    for p in pacotes_vencidos:
        alertas.append({
            'tipo': 'pacote_vencido',
            'nivel': 'urgente',
            'mensagem': f'{p.paciente.nome} — pacote de {p.tipo} vencido desde {p.data_vencimento.strftime("%d/%m/%Y")}',
            'paciente_id': p.paciente.id,
        })

    # Lançamentos pendentes há mais de 7 dias
    from datetime import timedelta
    data_limite = hoje - timedelta(days=7)
    pendentes_antigos = Lancamento.objects.filter(status='Pendente', data__lte=data_limite).count()
    if pendentes_antigos > 0:
        alertas.append({
            'tipo': 'financeiro',
            'nivel': 'aviso',
            'mensagem': f'{pendentes_antigos} pagamento(s) pendente(s) há mais de 7 dias',
        })

    return Response({
        'total_pacientes':   total_pacientes,
        'consultas_hoje':    consultas_hoje,
        'fisio_hoje':        fisio_hoje,
        'pilates_hoje':      pilates_hoje,
        'pendentes_fin':     pendentes_fin,
        'receita_mes':       float(receita_mes),
        'despesa_mes':       float(despesa_mes),
        'saldo_mes':         float(receita_mes - despesa_mes),
        'agendamentos_hoje': AgendamentoSerializer(agendamentos_hoje, many=True).data,
        'alertas':           alertas,
    })


# ── PACIENTES ────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def pacientes_list(request):
    if request.method == 'GET':
        q  = request.query_params.get('q', '')
        qs = Paciente.objects.all()
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(cpf__icontains=q))
        return Response(PacienteListSerializer(qs, many=True).data)

    serializer = PacienteDetalheSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def paciente_detail(request, pk):
    try:
        paciente = Paciente.objects.get(pk=pk)
    except Paciente.DoesNotExist:
        return Response({'message': 'Paciente não encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(PacienteDetalheSerializer(paciente, context={'request': request}).data)

    if request.method == 'PUT':
        serializer = PacienteDetalheSerializer(paciente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    paciente.delete()
    return Response(status=204)


# ── AGENDAMENTOS ─────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def agendamentos_list(request):
    if request.method == 'GET':
        hoje = date.today()
        ano = _parse_int(request.query_params.get('ano'), hoje.year)
        mes = _parse_int(request.query_params.get('mes'), hoje.month)
        import calendar
        from datetime import timedelta
        primeiro_dia = date(ano, mes, 1)
        ultimo_dia   = date(ano, mes, calendar.monthrange(ano, mes)[1])
        inicio = primeiro_dia - timedelta(days=35)
        fim    = ultimo_dia   + timedelta(days=35)
        qs = Agendamento.objects.filter(data__range=[inicio, fim]).order_by('data', 'horario')
        return Response(AgendamentoSerializer(qs, many=True).data)

    serializer = AgendamentoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def agendamento_detail(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({'message': 'Agendamento não encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(AgendamentoSerializer(agendamento).data)

    if request.method == 'PUT':
        serializer = AgendamentoSerializer(agendamento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    agendamento.delete()
    return Response(status=204)


@api_view(['PUT'])
def checkin_agendamento(request, pk):
    """
    Marca agendamento como Realizado.
    Se o paciente tiver pacote ativo, desconta uma sessão.
    Atualiza ultimo_atendimento do paciente.
    """
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({'message': 'Agendamento não encontrado.'}, status=404)

    novo_status = request.data.get('status', 'Realizado')
    agendamento.status = novo_status
    agendamento.save()

    # Atualiza ultimo_atendimento do paciente
    if agendamento.paciente and novo_status == 'Realizado':
        pac = agendamento.paciente
        if not pac.ultimo_atendimento or agendamento.data > pac.ultimo_atendimento:
            pac.ultimo_atendimento = agendamento.data
            pac.save()

        # Desconta sessão do pacote ativo correspondente
        pacote = Pacote.objects.filter(
            paciente=pac,
            tipo=agendamento.tipo,
            status='Ativo',
        ).order_by('data_vencimento').first()

        if pacote:
            pacote.sessoes_usadas += 1
            if pacote.sessoes_usadas >= pacote.total_sessoes:
                pacote.status = 'Encerrado'
            pacote.save()

    return Response(AgendamentoSerializer(agendamento).data)


# ── PACOTES ──────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def pacotes_list(request):
    if request.method == 'GET':
        paciente_id = request.query_params.get('paciente_id')
        qs = Pacote.objects.select_related('paciente').all()
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)
        return Response(PacoteSerializer(qs, many=True).data)

    serializer = PacoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def pacote_detail(request, pk):
    try:
        pacote = Pacote.objects.get(pk=pk)
    except Pacote.DoesNotExist:
        return Response({'message': 'Pacote não encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(PacoteSerializer(pacote).data)

    if request.method == 'PUT':
        serializer = PacoteSerializer(pacote, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    pacote.delete()
    return Response(status=204)


# ── FINANCEIRO ───────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def lancamentos_list(request):
    if request.method == 'GET':
        hoje     = date.today()
        ano      = _parse_int(request.query_params.get('ano'), hoje.year)
        mes      = _parse_int(request.query_params.get('mes'), hoje.month)
        tipo     = request.query_params.get('tipo', '')
        status_f = request.query_params.get('status', '')

        if not (1 <= mes <= 12):
            mes = hoje.month
        if not (2000 <= ano <= 2100):
            ano = hoje.year

        qs = Lancamento.objects.filter(data__year=ano, data__month=mes)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if status_f:
            qs = qs.filter(status=status_f)

        qs_mes      = Lancamento.objects.filter(data__year=ano, data__month=mes)
        receita_mes = qs_mes.filter(tipo='Receita').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        despesa_mes = qs_mes.filter(tipo='Despesa').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        pendentes   = qs_mes.filter(status='Pendente').aggregate(total=Sum('valor'))['total'] or Decimal('0')

        cats_receita = (
            qs_mes.filter(tipo='Receita')
            .values('categoria')
            .annotate(total=Sum('valor'))
            .order_by('-total')
        )

        # Relatório: atendimentos realizados vs recebidos no mês
        atendimentos_realizados = Agendamento.objects.filter(
            data__year=ano, data__month=mes, status='Realizado'
        ).count()

        return Response({
            'lancamentos':            LancamentoSerializer(qs, many=True).data,
            'receita_mes':            float(receita_mes),
            'despesa_mes':            float(despesa_mes),
            'saldo_mes':              float(receita_mes - despesa_mes),
            'pendentes':              float(pendentes),
            'cats_receita':           list(cats_receita),
            'atendimentos_realizados': atendimentos_realizados,
        })

    serializer = LancamentoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response({'errors': serializer.errors}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def lancamento_detail(request, pk):
    try:
        lancamento = Lancamento.objects.get(pk=pk)
    except Lancamento.DoesNotExist:
        return Response({'message': 'Lançamento não encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(LancamentoSerializer(lancamento).data)

    if request.method == 'PUT':
        serializer = LancamentoSerializer(lancamento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    lancamento.delete()
    return Response(status=204)


@api_view(['PUT'])
def marcar_pago(request, pk):
    try:
        lancamento = Lancamento.objects.get(pk=pk)
        lancamento.status = 'Pago'
        lancamento.save()
        return Response(LancamentoSerializer(lancamento).data)
    except Lancamento.DoesNotExist:
        return Response(status=404)


# ── EVOLUÇÕES ────────────────────────────────────────────────────────────

@api_view(['POST'])
def criar_evolucao(request):
    serializer = EvolucaoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
def deletar_evolucao(request, pk):
    try:
        evolucao = Evolucao.objects.get(pk=pk)
        evolucao.delete()
        return Response(status=204)
    except Evolucao.DoesNotExist:
        return Response(status=404)


# ── EXAMES PDF ───────────────────────────────────────────────────────────

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_exame(request):
    paciente_id = request.data.get('paciente_id')
    try:
        paciente = Paciente.objects.get(pk=paciente_id)
    except Paciente.DoesNotExist:
        return Response({'message': 'Paciente não encontrado.'}, status=404)

    arquivos_salvos = []
    for arquivo in request.FILES.getlist('pdfs'):
        exame = ExamePDF.objects.create(
            paciente=paciente,
            nome_original=arquivo.name,
            arquivo=arquivo,
        )
        arquivos_salvos.append(ExamePDFSerializer(exame, context={'request': request}).data)

    return Response({'success': True, 'arquivos': arquivos_salvos}, status=201)


@api_view(['DELETE'])
def deletar_exame(request, pk):
    try:
        exame = ExamePDF.objects.get(pk=pk)
        exame.arquivo.delete(save=False)
        exame.delete()
        return Response(status=204)
    except ExamePDF.DoesNotExist:
        return Response(status=404)


# ── IMPORTAR FICHA COM IA ────────────────────────────────────────────────

PROMPT_EXTRACAO = """
Você é um assistente especializado em digitalização de fichas de clínicas de fisioterapia.
Analise a imagem da ficha em papel e extraia os dados do paciente.

Retorne SOMENTE um JSON válido com os campos abaixo.
Use string vazia "" para campos não encontrados ou ilegíveis.
Para datas use o formato YYYY-MM-DD.
Para estado_civil use exatamente: Solteiro(a), Casado(a), Divorciado(a), Viúvo(a), União estável, ou "".
Para modalidade use exatamente: Fisioterapia, Pilates, Ambos, ou "".
Para pagamento_tipo use exatamente: Particular, Convênio, Ambos, ou "".

{
  "nome": "",
  "cpf": "",
  "telefone": "",
  "data_nascimento": "",
  "estado_civil": "",
  "profissao": "",
  "endereco": "",
  "modalidade": "",
  "pagamento_tipo": "",
  "convenio": "",
  "diagnostico_medico": "",
  "queixa_principal": "",
  "diagnostico_fisio": "",
  "alergia": "",
  "medicacao": "",
  "outros_problemas": ""
}

Retorne apenas o JSON, sem explicações, sem markdown, sem blocos de código.
"""


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def importar_ficha(request):
    imagem = request.FILES.get('imagem')
    if not imagem:
        return Response({'message': 'Nenhuma imagem enviada.'}, status=400)

    tipos_validos = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if imagem.content_type not in tipos_validos:
        return Response({'message': 'Formato inválido. Use JPG, PNG ou WEBP.'}, status=400)

    if imagem.size > 10 * 1024 * 1024:
        return Response({'message': 'Imagem muito grande. Máximo 10MB.'}, status=400)

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return Response({'message': 'Chave do Gemini não configurada no settings.py.'}, status=500)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        imagem_bytes = imagem.read()
        imagem_part = {
            'mime_type': imagem.content_type,
            'data': imagem_bytes,
        }

        response = model.generate_content([PROMPT_EXTRACAO, imagem_part])
        texto = response.text.strip()

        if texto.startswith('```'):
            texto = texto.split('```')[1]
            if texto.startswith('json'):
                texto = texto[4:]
        texto = texto.strip()

        dados = json.loads(texto)
        campos = [
            'nome', 'cpf', 'telefone', 'data_nascimento', 'estado_civil',
            'profissao', 'endereco', 'modalidade', 'pagamento_tipo', 'convenio',
            'diagnostico_medico', 'queixa_principal', 'diagnostico_fisio',
            'alergia', 'medicacao', 'outros_problemas',
        ]
        resultado = {c: str(dados.get(c, '') or '') for c in campos}
        return Response(resultado)

    except json.JSONDecodeError:
        return Response({'message': 'A IA não conseguiu extrair os dados. Tente com uma foto mais nítida.'}, status=422)
    except Exception as e:
        return Response({'message': f'Erro: {str(e)}'}, status=500)
