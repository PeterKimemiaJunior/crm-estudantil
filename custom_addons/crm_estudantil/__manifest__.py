{
    'name': 'CRM Estudantil UEM',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Sistema de Gestão e Acompanhamento Estudantil',
    'description': """
        Módulo base para o projeto de Programação Web e CMS.
        Transforma o CRM padrão num gestor de oportunidades académicas.
    """,
    'author': 'Grupo 1 - Engenharia Informática UEM',
    'depends': ['crm', 'website', 'survey'], # Indica que precisa destes módulos instalados primeiro
    'data': [
        # Aqui vão entrar os vossos ficheiros XML no futuro
    ],
    'installable': True,
    'application': True,
}