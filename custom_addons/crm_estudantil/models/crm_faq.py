from odoo import models, fields

class CrmFaq(models.Model):
    _name = 'crm.faq'
    _description = 'Base de Conhecimento e FAQ'
    _order = 'sequence, id'

    question = fields.Char(string="Pergunta / Tópico", required=True)
    answer = fields.Html(string="Resposta", required=True)
    category = fields.Selection([
        ('estagio', 'Estágios'),
        ('inscricoes', 'Inscrições'),
        ('regulamentos', 'Regulamentos'),
        ('outros', 'Outros')
    ], string="Categoria", required=True, default='estagio')
    active = fields.Boolean(string="Ativo", default=True)
    sequence = fields.Integer(string="Sequência", default=10)
