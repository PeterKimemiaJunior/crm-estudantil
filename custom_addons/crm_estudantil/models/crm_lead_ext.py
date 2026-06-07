from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
STUDENT_RE = re.compile(r'^[0-9A-Za-z\-]{4,20}$')

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    student_number = fields.Char(string='Número de Estudante', index=True)
    opportunity_type = fields.Selection([
        ('estagio',      'Estágio'),
        ('posgraduacao', 'Pós-Graduação'),
        ('evento',       'Evento'),
        ('suporte',      'Suporte'),
    ], string='Tipo de Oportunidade', default='estagio', required=True, index=True)
    course = fields.Selection([
        ('informatica', 'Engenharia Informática'),
        ('gestao',      'Gestão'),
        ('direito',     'Direito'),
        ('medicina',    'Medicina'),
        ('economia',    'Economia'),
        ('outro',       'Outro'),
    ], string='Curso')
    year = fields.Integer(string='Ano Curricular')

    # ----------------------------------------------------------------
    # RELAÇÃO: cada candidatura pertence a UMA oportunidade
    # Many2one: "o lado muitos" — muitos candidatos para 1 oportunidade
    # ondelete='set null' → se a oportunidade for apagada,
    #                        a candidatura fica mas sem oportunidade ligada
    # ----------------------------------------------------------------
    oportunidade_id = fields.Many2one(
        comodel_name='crm.oportunidades',
        string='Oportunidade',
        ondelete='set null',
        index=True,
        help='A vaga à qual este estudante se candidatou',
    )

    color = fields.Integer(compute='_compute_color', store=True)

    _sql_constraints = [
        ('student_opportunity_uniq', 'UNIQUE(student_number, oportunidade_id)', 'Já existe uma candidatura com este número de estudante para a mesma oportunidade.'),
    ]

    @api.constrains('email_from')
    def _check_email(self):
        for rec in self:
            if rec.email_from:
                if not EMAIL_RE.match(rec.email_from):
                    raise ValidationError('Email inválido: %s' % rec.email_from)

    @api.constrains('year')
    def _check_year(self):
        for rec in self:
            if rec.year is not None and rec.year != 0:
                if rec.year < 0 or rec.year > 2100:
                    raise ValidationError('Ano curricular inválido.')

    @api.constrains('student_number')
    def _check_student_number(self):
        for rec in self:
            if rec.student_number:
                if not STUDENT_RE.match(rec.student_number):
                    raise ValidationError('Número de estudante inválido. Deve conter 4-20 caracteres alfanuméricos ou hífen.')

    @api.depends('opportunity_type')
    def _compute_color(self):
        mapa = {'estagio': 1, 'posgraduacao': 4, 'evento': 3, 'suporte': 10}
        for rec in self:
            rec.color = mapa.get(rec.opportunity_type, 0)

    def get_opportunity_type_label(self):
        labels = dict(self._fields['opportunity_type'].selection)
        return labels.get(self.opportunity_type, self.opportunity_type)

    def get_course_label(self):
        labels = dict(self._fields['course'].selection)
        return labels.get(self.course, self.course or '-')