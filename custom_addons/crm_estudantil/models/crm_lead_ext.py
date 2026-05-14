# crm_estudantil/models/crm_lead_ext.py
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    student_number = fields.Char(string='Número de Estudante', index=True)
    opportunity_type = fields.Selection([
        ('estagio', 'Estágio'),
        ('posgraduacao', 'Pós-Graduação'),
        ('evento', 'Evento'),
        ('suporte', 'Suporte')
    ], string='Tipo de Oportunidade', default='estagio', required=True)
    course = fields.Selection([
        ('informatica', 'Engenharia Informática'),
        ('gestao', 'Gestão'),
        ('direito', 'Direito'),
        ('medicina', 'Medicina'),
        ('economia', 'Economia'),
        ('outro', 'Outro')
    ], string='Curso')
    year = fields.Integer(string='Ano Curricular')