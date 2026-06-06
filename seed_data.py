"""
Script de seed para popular a BD do CRM Estudantil.
Correr dentro do Odoo Shell:
  docker compose exec web odoo shell --addons-path=/mnt/custom_addons,/usr/lib/python3/dist-packages/odoo/addons --db_host=db --db_user=odoo --db_password=odoo -d crm_estudantil
E depois:
  exec(open('/mnt/custom_addons/../seed_data.py').read())
"""

from datetime import date, timedelta

env = env  # noqa - disponível no Odoo Shell

print("=" * 60)
print("🌱 A popular a base de dados do CRM Estudantil...")
print("=" * 60)

# ─────────────────────────────────────────────────
# 1. ESTÁGIOS — garantir que existem
# ─────────────────────────────────────────────────
StageModel = env['crm.stage']
stage_map = {}
for nome, seq, prob, won in [
    ('New',       1,  10, False),
    ('Qualified', 2,  30, False),
    ('Won',       3, 100, True),
    ('Lost',      4,   0, False),
]:
    rec = StageModel.search([('name', '=', nome)], limit=1)
    if not rec:
        rec = StageModel.create({'name': nome, 'sequence': seq, 'probability': prob, 'is_won': won})
        print(f"  ✅ Estágio criado: {nome}")
    else:
        print(f"  ⏭  Estágio já existe: {nome}")
    stage_map[nome] = rec

env.cr.commit()

# ─────────────────────────────────────────────────
# 2. OPORTUNIDADES (crm.oportunidades)
# ─────────────────────────────────────────────────
Opp = env['crm.oportunidades']
hoje = date.today()

oportunidades_data = [
    {
        'name': 'Estágio em Desenvolvimento de Software',
        'company_name': 'Vodacom Moçambique',
        'description': 'Oportunidade de estágio para estudantes de Engenharia Informática com conhecimentos em Python e Django. Trabalharás com uma equipa ágil em projetos reais de transformação digital.',
        'opportunity_type': 'estagio',
        'deadline': hoje + timedelta(days=30),
    },
    {
        'name': 'Estágio em Análise de Dados',
        'company_name': 'Standard Bank Moçambique',
        'description': 'Procuramos estudantes finalistas com experiência em Excel, SQL e ferramentas de BI para apoiar a equipa de analytics do banco.',
        'opportunity_type': 'estagio',
        'deadline': hoje + timedelta(days=20),
    },
    {
        'name': 'Estágio em Marketing Digital',
        'company_name': 'Movitel',
        'description': 'Participa na criação de campanhas digitais, gestão de redes sociais e análise de métricas de marketing para a maior operadora de telecomunicações do país.',
        'opportunity_type': 'estagio',
        'deadline': hoje + timedelta(days=45),
    },
    {
        'name': 'MBA em Gestão Empresarial',
        'company_name': 'UEM Business School',
        'description': 'Programa de pós-graduação para profissionais que pretendem aprofundar competências em liderança estratégica, finanças e gestão de projetos.',
        'opportunity_type': 'posgraduacao',
        'deadline': hoje + timedelta(days=60),
    },
    {
        'name': 'Mestrado em Engenharia de Sistemas',
        'company_name': 'Faculdade de Engenharia — UEM',
        'description': 'Programa de 2 anos com foco em sistemas embebidos, inteligência artificial e redes de computadores. Bolsas parciais disponíveis.',
        'opportunity_type': 'posgraduacao',
        'deadline': hoje + timedelta(days=50),
    },
    {
        'name': 'Hackathon Nacional de Inovação',
        'company_name': 'INAGE — Instituto Nacional de Gestão',
        'description': 'Competição de 48h onde equipas multidisciplinares desenvolvem soluções tecnológicas para desafios reais do governo moçambicano. Prémio de 50.000 MT.',
        'opportunity_type': 'evento',
        'deadline': hoje + timedelta(days=15),
    },
    {
        'name': 'Conferência Internacional de TI',
        'company_name': 'TechMoz 2026',
        'description': 'Evento anual que reúne especialistas, empresas e académicos do setor tecnológico em África. Inscrições gratuitas para estudantes da UEM.',
        'opportunity_type': 'evento',
        'deadline': hoje + timedelta(days=25),
    },
    {
        'name': 'Apoio em Elaboração de CV',
        'company_name': 'Gabinete de Inserção Profissional — UEM',
        'description': 'Sessões individuais de orientação para criação de curricula vitae e preparação para entrevistas de emprego.',
        'opportunity_type': 'suporte',
        'deadline': hoje + timedelta(days=90),
    },
]

opps_criadas = []
for data in oportunidades_data:
    existing = Opp.search([('name', '=', data['name'])], limit=1)
    if existing:
        print(f"  ⏭  Oportunidade já existe: {data['name']}")
        opps_criadas.append(existing)
    else:
        rec = Opp.create(data)
        opps_criadas.append(rec)
        print(f"  ✅ Oportunidade criada: {data['name']}")

env.cr.commit()

# ─────────────────────────────────────────────────
# 3. CANDIDATURAS (crm.lead)
# ─────────────────────────────────────────────────
Lead = env['crm.lead']
stage_new       = stage_map['New']
stage_qualified = stage_map['Qualified']
stage_won       = stage_map['Won']
stage_lost      = stage_map['Lost']

candidaturas_data = [
    # Opp 0 — Vodacom Software
    {'name': 'Candidatura — António Machava',         'contact_name': 'António Machava',       'email_from': 'a.machava@uem.ac.mz',     'phone': '+258 84 111 2233', 'student_number': '20231001', 'course': 'informatica', 'year': 4, 'opportunity_type': 'estagio',  'stage_id': stage_new.id,       'opp_idx': 0},
    {'name': 'Candidatura — Beatriz Cossa',           'contact_name': 'Beatriz Cossa',         'email_from': 'b.cossa@uem.ac.mz',       'phone': '+258 84 222 3344', 'student_number': '20231002', 'course': 'informatica', 'year': 3, 'opportunity_type': 'estagio',  'stage_id': stage_qualified.id, 'opp_idx': 0},
    {'name': 'Candidatura — Carlos Nhantumbo',        'contact_name': 'Carlos Nhantumbo',      'email_from': 'c.nhantumbo@uem.ac.mz',   'phone': '+258 84 333 4455', 'student_number': '20231003', 'course': 'informatica', 'year': 4, 'opportunity_type': 'estagio',  'stage_id': stage_won.id,       'opp_idx': 0},
    # Opp 1 — Standard Bank
    {'name': 'Candidatura — Dina Mate',               'contact_name': 'Dina Mate',             'email_from': 'd.mate@uem.ac.mz',        'phone': '+258 82 444 5566', 'student_number': '20231004', 'course': 'gestao',      'year': 5, 'opportunity_type': 'estagio',  'stage_id': stage_new.id,       'opp_idx': 1},
    {'name': 'Candidatura — Eduardo Bila',            'contact_name': 'Eduardo Bila',          'email_from': 'e.bila@uem.ac.mz',        'phone': '+258 82 555 6677', 'student_number': '20231005', 'course': 'economia',    'year': 4, 'opportunity_type': 'estagio',  'stage_id': stage_lost.id,      'opp_idx': 1},
    # Opp 2 — Movitel Marketing
    {'name': 'Candidatura — Fátima Chauque',          'contact_name': 'Fátima Chauque',        'email_from': 'f.chauque@uem.ac.mz',     'phone': '+258 86 666 7788', 'student_number': '20231006', 'course': 'gestao',      'year': 3, 'opportunity_type': 'estagio',  'stage_id': stage_new.id,       'opp_idx': 2},
    {'name': 'Candidatura — Gracinda Tembe',          'contact_name': 'Gracinda Tembe',        'email_from': 'g.tembe@uem.ac.mz',       'phone': '+258 86 777 8899', 'student_number': '20231007', 'course': 'gestao',      'year': 4, 'opportunity_type': 'estagio',  'stage_id': stage_qualified.id, 'opp_idx': 2},
    # Opp 3 — MBA
    {'name': 'Candidatura — Hélder Sitoe',            'contact_name': 'Hélder Sitoe',          'email_from': 'h.sitoe@uem.ac.mz',       'phone': '+258 84 888 9900', 'student_number': '20221001', 'course': 'gestao',      'year': 5, 'opportunity_type': 'posgraduacao', 'stage_id': stage_qualified.id, 'opp_idx': 3},
    # Opp 4 — Mestrado Eng. Sistemas
    {'name': 'Candidatura — Ilda Marrengula',         'contact_name': 'Ilda Marrengula',       'email_from': 'i.marrengula@uem.ac.mz',  'phone': '+258 82 999 0011', 'student_number': '20221002', 'course': 'informatica', 'year': 5, 'opportunity_type': 'posgraduacao', 'stage_id': stage_new.id,       'opp_idx': 4},
    # Opp 5 — Hackathon
    {'name': 'Candidatura — João Mondlane',           'contact_name': 'João Mondlane',         'email_from': 'j.mondlane@uem.ac.mz',    'phone': '+258 84 101 1122', 'student_number': '20231008', 'course': 'informatica', 'year': 3, 'opportunity_type': 'evento',    'stage_id': stage_won.id,       'opp_idx': 5},
    {'name': 'Candidatura — Kezia Cumbane',           'contact_name': 'Kezia Cumbane',         'email_from': 'k.cumbane@uem.ac.mz',     'phone': '+258 86 202 2233', 'student_number': '20231009', 'course': 'economia',    'year': 2, 'opportunity_type': 'evento',    'stage_id': stage_won.id,       'opp_idx': 5},
    # Opp 6 — Conferência TI
    {'name': 'Candidatura — Lúcia Nkavandame',       'contact_name': 'Lúcia Nkavandame',      'email_from': 'l.nkavandame@uem.ac.mz',  'phone': '+258 84 303 3344', 'student_number': '20231010', 'course': 'informatica', 'year': 4, 'opportunity_type': 'evento',    'stage_id': stage_new.id,       'opp_idx': 6},
    # Opp 7 — Suporte CV
    {'name': 'Candidatura — Manuel Chirindza',        'contact_name': 'Manuel Chirindza',      'email_from': 'm.chirindza@uem.ac.mz',   'phone': '+258 82 404 4455', 'student_number': '20231011', 'course': 'direito',     'year': 3, 'opportunity_type': 'suporte',   'stage_id': stage_won.id,       'opp_idx': 7},
]

for cand in candidaturas_data:
    opp_idx = cand.pop('opp_idx')
    oportunidade = opps_criadas[opp_idx] if opp_idx < len(opps_criadas) else None
    existing = Lead.search([('student_number', '=', cand['student_number']), ('name', '=', cand['name'])], limit=1)
    if existing:
        print(f"  ⏭  Candidatura já existe: {cand['contact_name']}")
    else:
        payload = dict(cand)
        if oportunidade:
            payload['oportunidade_id'] = oportunidade.id
        Lead.create(payload)
        print(f"  ✅ Candidatura criada: {cand['contact_name']} → {oportunidade.name if oportunidade else 'sem oportunidade'}")

env.cr.commit()

# ─────────────────────────────────────────────────
# 4. QUESTIONÁRIOS (survey.survey)
# ─────────────────────────────────────────────────
Survey = env['survey.survey']
surveys_data = [
    {
        'title': 'Avaliação da Qualidade dos Estágios 2026',
        'description': 'Questionário destinado a estudantes que completaram estágios profissionais em 2026. A tua opinião é fundamental para melhorar os programas de estágio da UEM.',
        'access_mode': 'public',
        'state': 'open',
    },
    {
        'title': 'Satisfação com os Serviços Académicos',
        'description': 'Ajuda-nos a melhorar os serviços prestados pelo Gabinete de Inserção Profissional respondendo a este breve questionário (5 minutos).',
        'access_mode': 'public',
        'state': 'open',
    },
    {
        'title': 'Perfil de Competências dos Estudantes Finalistas',
        'description': 'Levantamento de competências técnicas e transversais dos estudantes em fase final de curso para apoiar o matchmaking com entidades parceiras.',
        'access_mode': 'public',
        'state': 'open',
    },
]

for s in surveys_data:
    existing = Survey.search([('title', '=', s['title'])], limit=1)
    if existing:
        print(f"  ⏭  Questionário já existe: {s['title']}")
    else:
        Survey.create(s)
        print(f"  ✅ Questionário criado: {s['title']}")

env.cr.commit()

print()
print("=" * 60)
print("🎉 Seed concluído com sucesso!")
print(f"   • {len(opps_criadas)} oportunidades")
print(f"   • {len(candidaturas_data)} candidaturas")
print(f"   • {len(surveys_data)} questionários")
print("=" * 60)
