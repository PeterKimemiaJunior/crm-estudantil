from odoo import models, fields

class Opportunity(models.Model):
    _name = "crm.oportunidades"
    _description = "Oportunidades"
    _order = "create_date desc"

    name = fields.Char(
        string="Título",
        required=True
    )

    company_name = fields.Char(
        string="Empresa"
    )

    description = fields.Text(
        string="Descrição"
    )

    opportunity_type = fields.Selection(
        [
            ('estagio', 'Estágio'),
            ('posgraduacao', 'Pós-Graduação'),
            ('evento', 'Evento'),
            ('suporte', 'Suporte')
        ],
        string="Tipo de Oportunidade",
        default='estagio',
        required=True
    )

    deadline = fields.Date(
        string="Prazo"
    )

    active = fields.Boolean(
        string="Ativo",
        default=True
    )