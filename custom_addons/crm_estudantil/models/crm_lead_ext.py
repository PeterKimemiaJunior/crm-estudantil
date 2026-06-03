from odoo import models, fields, api


class CrmLead(models.Model):
  
    _inherit = 'crm.lead'

    student_number = fields.Char(
        string='Número de Estudante',
        index=True,          # cria índice no Postgres para pesquisa rápida
        help='Ex: 20231234' 
    )

    opportunity_type = fields.Selection(
        selection=[
            ('estagio',      'Estágio'),
            ('posgraduacao', 'Pós-Graduação'),
            ('evento',       'Evento'),
            ('suporte',      'Suporte'),
        ],
        string='Tipo de Oportunidade',
        default='estagio',
        required=True,
        index=True,
    )

    course = fields.Selection(
        selection=[
            ('informatica', 'Engenharia Informática'),
            ('gestao',      'Gestão'),
            ('direito',     'Direito'),
            ('medicina',    'Medicina'),
            ('economia',    'Economia'),
            ('outro',       'Outro'),
        ],
        string='Curso',
    )

    year = fields.Integer(
        string='Ano Curricular',
        help='1 a 5'
    )

    # ------------------------------------------------------------------
    # RF-03: Cor do card Kanban — computed, não ocupa coluna no Postgres
    # ------------------------------------------------------------------
    color = fields.Integer(
        compute='_compute_color',
        store=True,      # store=True → guarda no Postgres mesmo sendo computed
        help='Cor do card no Kanban do CRM'
    )

    @api.depends('opportunity_type')
    def _compute_color(self):
        """
        Odoo usa números 0-11 para cores no Kanban.
        Mapeamos cada tipo para uma cor diferente.
        """
        mapa_cores = {
            'estagio':      1,   # azul
            'posgraduacao': 4,   # roxo
            'evento':       3,   # amarelo
            'suporte':      10,  # verde
        }
        for rec in self:
            rec.color = mapa_cores.get(rec.opportunity_type, 0)

    # ------------------------------------------------------------------
    # Método utilitário usado nos templates QWeb
    # ------------------------------------------------------------------
    def get_opportunity_type_label(self):
        """Retorna o label legível do tipo de oportunidade."""
        labels = dict(self._fields['opportunity_type'].selection)
        return labels.get(self.opportunity_type, self.opportunity_type)

    def get_course_label(self):
        """Retorna o label legível do curso."""
        labels = dict(self._fields['course'].selection)
        return labels.get(self.course, self.course or '-')
