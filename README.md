# Clínica Fisioterapia & Pilates
### Sistema de Gerenciamento — Dra. Fernanda Rodrigues Teodoro

Sistema web completo para gestão de clínica de fisioterapia e pilates. Desenvolvido com Django + React, roda no navegador e é otimizado para uso no celular.

---

## Funcionalidades

- **Agenda** — Calendário mensal com agendamentos, check-in de presença e registro de faltas
- **Pacientes** — Ficha clínica completa com histórico de saúde, evoluções e exames em PDF
- **Pacotes de sessões** — Controle de sessões contratadas com barra de progresso e alertas automáticos
- **Financeiro** — Lançamentos de receitas e despesas, relatório mensal e controle de pendentes
- **Importar ficha** — Fotografe uma ficha de papel e a IA preenche o cadastro automaticamente
- **Controle de acesso** — Perfis distintos para clínica, financeiro e administrador

---

## Requisitos

- Python 3.10+
- Node.js 18+

---

## Instalação

**1. Clone o repositório e instale as dependências:**
```bash
git clone https://github.com/seu-usuario/clinica-fisioterapia.git
cd clinica-fisioterapia
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

**2. Configure as variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto:
```
SECRET_KEY=sua-secret-key
GEMINI_API_KEY=sua-chave-gemini
```

> A chave do Gemini é necessária apenas para a função de importar fichas. Obtenha gratuitamente em [aistudio.google.com](https://aistudio.google.com).

**3. Inicialize o banco de dados:**
```bash
python manage.py migrate
```

**4. Build do frontend:**
```bash
cd frontend
npm install
npm run build
cd ..
```

**5. Inicie o servidor:**
```bash
python manage.py runserver
```

Acesse em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Perfis de acesso

| Perfil | Agenda | Pacientes | Financeiro | Dashboard | Importar | Configurações |
|--------|:------:|:---------:|:----------:|:---------:|:--------:|:-------------:|
| Administrador | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Clínica | ✅ | ✅ | — | ✅ | ✅ | — |
| Contador | — | — | ✅ | ✅ | — | — |

---

## Stack

- **Backend** — Django 4.2, Django REST Framework
- **Frontend** — React 18, Tailwind CSS, Vite
- **Banco de dados** — SQLite
- **IA** — Google Gemini 1.5 Flash
