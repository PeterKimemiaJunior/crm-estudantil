{
    'name': 'CRM Estudantil UEM',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Sistema de Gestão e Acompanhamento Estudantil',
    'description': """Módulo base.""",
    'author': 'Grupo 1 - Engenharia Informática UEM',
    'depends': ['crm', 'website', 'survey'],
    'data': [
        'views/website_layout.xml',
        'views/website_oportunidades.xml',
        'views/website_candidatura.xml',
        'views/website_faq.xml',
        'views/website_kanban.xml',
        'views/website_dashboard.xml',
        'views/gestao_candidaturas.xml',
        'views/website_criar_oportunidades.xml',
        'views/portal_layout.xml',
        'views/portal_canditatura.xml',
        'views/portal_oportunidades.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'crm_estudantil/static/src/css/custom_theme.scss',
        ],
    },
    'installable': True,
    'application': True,
}
