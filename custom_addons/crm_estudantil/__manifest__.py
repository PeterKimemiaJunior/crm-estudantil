{
    'name': 'CRM Estudantil UEM',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Sistema de Gestão e Acompanhamento Estudantil',
    'description': """Módulo base.""",
    'author': 'Grupo 1 - Engenharia Informática UEM',
    'depends': ['crm', 'website', 'survey'],
    'data': [],
    'assets': {
        'web.assets_frontend': [
            'crm_estudantil/static/src/css/custom_theme.scss',
        ],
    },
    'installable': True,
    'application': True,
}
