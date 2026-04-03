from django.db import models


class Usuario(models.Model):
    PERFIL_CHOICES = [
        ('admin',    'Administrador — acesso total'),
        ('clinica',  'Clínica — agenda e pacientes'),
        ('contador', 'Contador — somente financeiro'),
    ]
    usuario = models.CharField(max_length=50, unique=True)
    senha   = models.CharField(max_length=64)
    nome    = models.CharField(max_length=100)
    perfil  = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='clinica')
    ativo   = models.BooleanField(default=True)

    class Meta:
        ordering = ['usuario']
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.usuario


class Paciente(models.Model):
    STATUS_CHOICES      = [('Ativo', 'Ativo'), ('Inativo', 'Inativo')]
    MODALIDADE_CHOICES  = [('Fisioterapia', 'Fisioterapia'), ('Pilates', 'Pilates'), ('Ambos', 'Ambos')]
    PAGAMENTO_CHOICES   = [('Particular', 'Particular'), ('Convênio', 'Convênio'), ('Ambos', 'Ambos')]
    ESTADO_CIVIL_CHOICES = [
        ('Solteiro(a)', 'Solteiro(a)'), ('Casado(a)', 'Casado(a)'),
        ('Divorciado(a)', 'Divorciado(a)'), ('Viúvo(a)', 'Viúvo(a)'),
        ('União estável', 'União estável'),
    ]

    nome                = models.CharField(max_length=200)
    cpf                 = models.CharField(max_length=20, blank=True, unique=True, null=True)
    telefone            = models.CharField(max_length=20, blank=True)
    data_nascimento     = models.DateField(null=True, blank=True)
    idade               = models.IntegerField(null=True, blank=True)
    estado_civil        = models.CharField(max_length=30, blank=True, choices=ESTADO_CIVIL_CHOICES)
    profissao           = models.CharField(max_length=100, blank=True)
    endereco            = models.CharField(max_length=300, blank=True)
    modalidade          = models.CharField(max_length=20, blank=True, choices=MODALIDADE_CHOICES)
    pagamento_tipo      = models.CharField(max_length=20, blank=True, choices=PAGAMENTO_CHOICES)
    convenio            = models.CharField(max_length=100, blank=True)
    diagnostico_medico  = models.CharField(max_length=300, blank=True)
    queixa_principal    = models.TextField(blank=True)
    diagnostico_fisio   = models.TextField(blank=True)
    exame_raio_x        = models.BooleanField(default=False)
    exame_rnm           = models.BooleanField(default=False)
    exame_tomografia    = models.BooleanField(default=False)
    exame_ecografia     = models.BooleanField(default=False)
    obs_exames          = models.TextField(blank=True)
    hs_cirurgia         = models.BooleanField(default=False)
    hs_hipertensao      = models.BooleanField(default=False)
    hs_diabetes         = models.BooleanField(default=False)
    hs_cardiaco         = models.BooleanField(default=False)
    hs_labirintite      = models.BooleanField(default=False)
    hs_fumante          = models.BooleanField(default=False)
    hs_perda_peso       = models.BooleanField(default=False)
    hs_febre            = models.BooleanField(default=False)
    hs_vomito           = models.BooleanField(default=False)
    hs_trauma           = models.BooleanField(default=False)
    hs_osteoporose      = models.BooleanField(default=False)
    alergia             = models.CharField(max_length=200, blank=True)
    outros_problemas    = models.CharField(max_length=200, blank=True)
    medicacao           = models.TextField(blank=True)
    status              = models.CharField(max_length=10, default='Ativo', choices=STATUS_CHOICES)
    data_cadastro       = models.DateField(auto_now_add=True)
    ultimo_atendimento  = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    TIPO_CHOICES   = [('Fisioterapia', 'Fisioterapia'), ('Pilates', 'Pilates')]
    STATUS_CHOICES = [
        ('Confirmado', 'Confirmado'),
        ('Aguardando', 'Aguardando'),
        ('Realizado',  'Realizado'),   # ← novo: check-in
        ('Faltou',     'Faltou'),      # ← novo: ausência registrada
        ('Cancelado',  'Cancelado'),
    ]

    paciente_nome = models.CharField(max_length=200)
    paciente      = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True, related_name='agendamentos')
    data          = models.DateField()
    horario       = models.TimeField()
    tipo          = models.CharField(max_length=20, choices=TIPO_CHOICES)
    profissional  = models.CharField(max_length=100)
    status        = models.CharField(max_length=20, default='Confirmado', choices=STATUS_CHOICES)
    observacao    = models.TextField(blank=True)

    class Meta:
        ordering = ['data', 'horario']
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'

    def __str__(self):
        return f'{self.paciente_nome} — {self.data} {self.horario}'


class Pacote(models.Model):
    """Controle de pacotes de sessões contratados pelo paciente."""
    TIPO_CHOICES   = [('Fisioterapia', 'Fisioterapia'), ('Pilates', 'Pilates')]
    STATUS_CHOICES = [('Ativo', 'Ativo'), ('Encerrado', 'Encerrado'), ('Vencido', 'Vencido')]

    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='pacotes')
    tipo             = models.CharField(max_length=20, choices=TIPO_CHOICES)
    total_sessoes    = models.PositiveIntegerField()
    sessoes_usadas   = models.PositiveIntegerField(default=0)
    valor_total      = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio      = models.DateField()
    data_vencimento  = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, default='Ativo', choices=STATUS_CHOICES)
    observacao       = models.TextField(blank=True)
    data_cadastro    = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-data_cadastro']
        verbose_name = 'Pacote'
        verbose_name_plural = 'Pacotes'

    @property
    def sessoes_restantes(self):
        return max(0, self.total_sessoes - self.sessoes_usadas)

    @property
    def percentual_uso(self):
        if self.total_sessoes == 0:
            return 0
        return round((self.sessoes_usadas / self.total_sessoes) * 100)

    def __str__(self):
        return f'{self.paciente.nome} — {self.tipo} ({self.sessoes_restantes} restantes)'


class Evolucao(models.Model):
    paciente   = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='evolucoes')
    data       = models.DateField()
    descricao  = models.TextField()

    class Meta:
        ordering = ['-data']
        verbose_name = 'Evolução'
        verbose_name_plural = 'Evoluções'

    def __str__(self):
        return f'{self.paciente.nome} — {self.data}'


class Lancamento(models.Model):
    TIPO_CHOICES   = [('Receita', 'Receita'), ('Despesa', 'Despesa')]
    STATUS_CHOICES = [('Pago', 'Pago'), ('Pendente', 'Pendente')]
    CATEGORIA_CHOICES = [
        ('Fisioterapia', 'Fisioterapia'),
        ('Pilates', 'Pilates'),
        ('Infraestrutura', 'Infraestrutura'),
        ('Suprimentos', 'Suprimentos'),
        ('Salário', 'Salário'),
        ('Outros', 'Outros'),
    ]

    descricao  = models.CharField(max_length=300)
    tipo       = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor      = models.DecimalField(max_digits=10, decimal_places=2)
    data       = models.DateField()
    categoria  = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    status     = models.CharField(max_length=10, default='Pago', choices=STATUS_CHOICES)
    paciente   = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos')
    pacote     = models.ForeignKey(Pacote, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos')
    agendamento= models.OneToOneField(Agendamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamento')

    class Meta:
        ordering = ['-data']
        verbose_name = 'Lançamento'
        verbose_name_plural = 'Lançamentos'

    def __str__(self):
        return f'{self.descricao} — R$ {self.valor}'


class ExamePDF(models.Model):
    paciente      = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='exames_pdf')
    nome_original = models.CharField(max_length=255)
    arquivo       = models.FileField(upload_to='exames/')
    data_upload   = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-data_upload']
        verbose_name = 'Exame PDF'
        verbose_name_plural = 'Exames PDF'

    def __str__(self):
        return f'{self.paciente.nome} — {self.nome_original}'
