from odoo import models, fields, api

class Opportunity(models.Model):
    _name = "crm.oportunidades"
    _description = "Oportunidades"
    _order = "create_date desc"

    name = fields.Char(string="Título", required=True)
    company_name = fields.Char(string="Empresa")
    description = fields.Text(string="Descrição")
    opportunity_type = fields.Selection([
        ('estagio',      'Estágio'),
        ('posgraduacao', 'Pós-Graduação'),
        ('evento',       'Evento'),
        ('suporte',      'Suporte'),
    ], string="Tipo de Oportunidade", default='estagio', required=True)
    deadline = fields.Date(string="Prazo")
    active = fields.Boolean(string="Ativo", default=True)

    # ----------------------------------------------------------------
    # RELAÇÃO: uma oportunidade tem MUITOS candidatos (crm.lead)
    # One2many: "o lado 1" fica aqui
    # Many2one: "o lado muitos" fica no crm.lead (campo oportunidade_id)
    # ----------------------------------------------------------------
    candidaturas_ids = fields.One2many(
        comodel_name='crm.lead',       # modelo do outro lado
        inverse_name='oportunidade_id', # campo Many2one no crm.lead
        string='Candidaturas',
    )

    # Contador — útil para mostrar no kanban/lista
    total_candidaturas = fields.Integer(
        string='Nº Candidaturas',
        compute='_compute_total_candidaturas',
        store=True,
    )

    @api.depends('candidaturas_ids')
    def _compute_total_candidaturas(self):
        for rec in self:
            rec.total_candidaturas = len(rec.candidaturas_ids)