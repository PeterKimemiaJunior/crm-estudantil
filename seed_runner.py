#!/usr/bin/env python3
"""
Runner autónomo para executar o seed sem precisar do Odoo Shell interactivo.
Usa a API interna do Odoo directamente.
"""
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

# pyrefly: ignore [missing-import]
import odoo
# pyrefly: ignore [missing-import]
from odoo.api import Environment
# pyrefly: ignore [missing-import]
import odoo.modules.registry

# Configurar o Odoo
odoo.tools.config.parse_config([
    '--addons-path=/mnt/custom_addons,/usr/lib/python3/dist-packages/odoo/addons',
    '--db_host=db', '--db_user=odoo', '--db_password=odoo',
    '-d', 'crm_estudantil'
])

db_name = 'crm_estudantil'

from datetime import date, timedelta

registry = odoo.modules.registry.Registry(db_name)
with registry.cursor() as cr:
    env = Environment(cr, odoo.SUPERUSER_ID, {})

    print("=" * 60)
    print("🌱 A popular a base de dados do CRM Estudantil...")
    print("=" * 60)

    # ─── Estágios ───────────────────────────────────────────────
    StageModel = env['crm.stage']
    stage_map = {}
    for nome, seq, won in [
        ('New',       1, False),
        ('Qualified', 2, False),
        ('Won',       3, True),
        ('Lost',      4, False),
    ]:
        rec = StageModel.search([('name', '=', nome)], limit=1)
        if not rec:
            rec = StageModel.create({'name': nome, 'sequence': seq, 'is_won': won})
            print(f"  ✅ Estágio criado: {nome}")
        else:
            print(f"  ⏭  Estágio já existe: {nome}")
        stage_map[nome] = rec

    # ─── Oportunidades ──────────────────────────────────────────
    Opp = env['crm.oportunidades']
    hoje = date.today()

    oportunidades_data = [
        {'name': 'Estágio em Desenvolvimento de Software', 'company_name': 'Vodacom Moçambique',             'description': 'Estágio para estudantes de Engenharia Informática com conhecimentos em Python e Django.', 'opportunity_type': 'estagio',      'deadline': hoje + timedelta(days=30)},
        {'name': 'Estágio em Análise de Dados',            'company_name': 'Standard Bank Moçambique',       'description': 'Procuramos estudantes finalistas com experiência em SQL e ferramentas de BI.',            'opportunity_type': 'estagio',      'deadline': hoje + timedelta(days=20)},
        {'name': 'Estágio em Marketing Digital',           'company_name': 'Movitel',                        'description': 'Participa na criação de campanhas digitais e gestão de redes sociais.',                   'opportunity_type': 'estagio',      'deadline': hoje + timedelta(days=45)},
        {'name': 'MBA em Gestão Empresarial',              'company_name': 'UEM Business School',            'description': 'Programa de pós-graduação em liderança estratégica, finanças e gestão de projetos.',      'opportunity_type': 'posgraduacao', 'deadline': hoje + timedelta(days=60)},
        {'name': 'Mestrado em Engenharia de Sistemas',     'company_name': 'Faculdade de Engenharia — UEM',  'description': 'Programa de 2 anos com IA, sistemas embebidos e redes. Bolsas parciais disponíveis.',       'opportunity_type': 'posgraduacao', 'deadline': hoje + timedelta(days=50)},
        {'name': 'Hackathon Nacional de Inovação',         'company_name': 'INAGE',                          'description': 'Competição de 48h com soluções tecnológicas para desafios do governo. Prémio: 50.000 MT.', 'opportunity_type': 'evento',       'deadline': hoje + timedelta(days=15)},
        {'name': 'Conferência Internacional de TI',        'company_name': 'TechMoz 2026',                   'description': 'Evento anual de tecnologia em África. Inscrições gratuitas para estudantes da UEM.',       'opportunity_type': 'evento',       'deadline': hoje + timedelta(days=25)},
        {'name': 'Apoio em Elaboração de CV',              'company_name': 'Gabinete de Inserção Profissional — UEM', 'description': 'Sessões individuais de orientação para criação de CV e preparação de entrevistas.', 'opportunity_type': 'suporte',      'deadline': hoje + timedelta(days=90)},
    ]

    opps_criadas = []
    for data in oportunidades_data:
        existing = Opp.search([('name', '=', data['name'])], limit=1)
        if existing:
            print(f"  ⏭  Já existe: {data['name']}")
            opps_criadas.append(existing)
        else:
            rec = Opp.create(data)
            opps_criadas.append(rec)
            print(f"  ✅ Oportunidade: {data['name']}")

    # ─── Candidaturas ───────────────────────────────────────────
    Lead = env['crm.lead']
    sn = stage_map['New'].id
    sq = stage_map['Qualified'].id
    sw = stage_map['Won'].id
    sl = stage_map['Lost'].id

    candidaturas = [
        {'name': 'Candidatura — António Machava',   'contact_name': 'António Machava',   'email_from': 'a.machava@uem.ac.mz',    'phone': '+258 84 111 2233', 'student_number': '20231001', 'course': 'informatica', 'year': 4, 'opportunity_type': 'estagio',      'stage_id': sn, 'opp_idx': 0},
        {'name': 'Candidatura — Beatriz Cossa',     'contact_name': 'Beatriz Cossa',     'email_from': 'b.cossa@uem.ac.mz',      'phone': '+258 84 222 3344', 'student_number': '20231002', 'course': 'informatica', 'year': 3, 'opportunity_type': 'estagio',      'stage_id': sq, 'opp_idx': 0},
        {'name': 'Candidatura — Carlos Nhantumbo',  'contact_name': 'Carlos Nhantumbo',  'email_from': 'c.nhantumbo@uem.ac.mz',  'phone': '+258 84 333 4455', 'student_number': '20231003', 'course': 'informatica', 'year': 4, 'opportunity_type': 'estagio',      'stage_id': sw, 'opp_idx': 0},
        {'name': 'Candidatura — Dina Mate',         'contact_name': 'Dina Mate',         'email_from': 'd.mate@uem.ac.mz',        'phone': '+258 82 444 5566', 'student_number': '20231004', 'course': 'gestao',      'year': 5, 'opportunity_type': 'estagio',      'stage_id': sn, 'opp_idx': 1},
        {'name': 'Candidatura — Eduardo Bila',      'contact_name': 'Eduardo Bila',      'email_from': 'e.bila@uem.ac.mz',        'phone': '+258 82 555 6677', 'student_number': '20231005', 'course': 'economia',    'year': 4, 'opportunity_type': 'estagio',      'stage_id': sl, 'opp_idx': 1},
        {'name': 'Candidatura — Fátima Chauque',   'contact_name': 'Fátima Chauque',    'email_from': 'f.chauque@uem.ac.mz',     'phone': '+258 86 666 7788', 'student_number': '20231006', 'course': 'gestao',      'year': 3, 'opportunity_type': 'estagio',      'stage_id': sn, 'opp_idx': 2},
        {'name': 'Candidatura — Gracinda Tembe',    'contact_name': 'Gracinda Tembe',    'email_from': 'g.tembe@uem.ac.mz',       'phone': '+258 86 777 8899', 'student_number': '20231007', 'course': 'gestao',      'year': 4, 'opportunity_type': 'estagio',      'stage_id': sq, 'opp_idx': 2},
        {'name': 'Candidatura — Hélder Sitoe',      'contact_name': 'Hélder Sitoe',      'email_from': 'h.sitoe@uem.ac.mz',       'phone': '+258 84 888 9900', 'student_number': '20221001', 'course': 'gestao',      'year': 5, 'opportunity_type': 'posgraduacao', 'stage_id': sq, 'opp_idx': 3},
        {'name': 'Candidatura — Ilda Marrengula',   'contact_name': 'Ilda Marrengula',   'email_from': 'i.marrengula@uem.ac.mz',  'phone': '+258 82 999 0011', 'student_number': '20221002', 'course': 'informatica', 'year': 5, 'opportunity_type': 'posgraduacao', 'stage_id': sn, 'opp_idx': 4},
        {'name': 'Candidatura — João Mondlane',     'contact_name': 'João Mondlane',     'email_from': 'j.mondlane@uem.ac.mz',    'phone': '+258 84 101 1122', 'student_number': '20231008', 'course': 'informatica', 'year': 3, 'opportunity_type': 'evento',       'stage_id': sw, 'opp_idx': 5},
        {'name': 'Candidatura — Kezia Cumbane',     'contact_name': 'Kezia Cumbane',     'email_from': 'k.cumbane@uem.ac.mz',     'phone': '+258 86 202 2233', 'student_number': '20231009', 'course': 'economia',    'year': 2, 'opportunity_type': 'evento',       'stage_id': sw, 'opp_idx': 5},
        {'name': 'Candidatura — Lúcia Nkavandame', 'contact_name': 'Lúcia Nkavandame',  'email_from': 'l.nkavandame@uem.ac.mz',  'phone': '+258 84 303 3344', 'student_number': '20231010', 'course': 'informatica', 'year': 4, 'opportunity_type': 'evento',       'stage_id': sn, 'opp_idx': 6},
        {'name': 'Candidatura — Manuel Chirindza',  'contact_name': 'Manuel Chirindza',  'email_from': 'm.chirindza@uem.ac.mz',   'phone': '+258 82 404 4455', 'student_number': '20231011', 'course': 'direito',     'year': 3, 'opportunity_type': 'suporte',      'stage_id': sw, 'opp_idx': 7},
    ]

    for cand in candidaturas:
        opp_idx = cand.pop('opp_idx')
        existing = Lead.search([('student_number', '=', cand['student_number'])], limit=1)
        if existing:
            print(f"  ⏭  Candidatura já existe: {cand['contact_name']}")
        else:
            payload = dict(cand)
            if opp_idx < len(opps_criadas):
                payload['oportunidade_id'] = opps_criadas[opp_idx].id
            Lead.create(payload)
            print(f"  ✅ Candidatura: {cand['contact_name']}")

    # ─── Questionários ──────────────────────────────────────────
    Survey = env['survey.survey']
    surveys = [
        {'title': 'Avaliação da Qualidade dos Estágios 2026',         'access_mode': 'public'},
        {'title': 'Satisfação com os Serviços Académicos',             'access_mode': 'public'},
        {'title': 'Perfil de Competências dos Estudantes Finalistas',  'access_mode': 'public'},
    ]
    for s in surveys:
        if not Survey.search([('title', '=', s['title'])], limit=1):
            Survey.create(s)
            print(f"  ✅ Questionário: {s['title']}")
        else:
            print(f"  ⏭  Questionário já existe: {s['title']}")

    # ─── FAQs ──────────────────────────────────────────
    Faq = env['crm.faq']
    faqs = [
        {'question': 'Como me candidato a um estágio?', 'answer': 'Acede à página de Oportunidades, selecciona a vaga desejada e preenche o formulário de candidatura.', 'category': 'estagio'},
        {'question': 'Posso candidatar-me a mais de um estágio?', 'answer': 'Sim, podes submeter candidaturas para múltiplas oportunidades em simultâneo.', 'category': 'estagio'},
        {'question': 'Quais os documentos necessários?', 'answer': 'Necessitas de: CV actualizado em PDF ou Word, carta de motivação e número de estudante activo na UEM.', 'category': 'inscricoes'},
        {'question': 'Os dados são confidenciais?', 'answer': 'Sim. Os teus dados são tratados em conformidade com a política de privacidade da UEM.', 'category': 'regulamentos'},
    ]
    for f in faqs:
        if not Faq.search([('question', '=', f['question'])], limit=1):
            Faq.create(f)
            print(f"  ✅ FAQ: {f['question']}")
        else:
            print(f"  ⏭  FAQ já existe: {f['question']}")

    cr.commit()

    print()
    print("=" * 60)
    print("🎉 Seed concluído com sucesso!")
    print(f"   • {len(opps_criadas)} oportunidades")
    print(f"   • {len(candidaturas)} candidaturas")
    print(f"   • {len(surveys)} questionários")
    print("=" * 60)
