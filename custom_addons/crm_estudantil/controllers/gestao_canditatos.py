# crm_estudantil/controllers/gestao_candidatos.py
from odoo import http
from odoo.http import request
from datetime import date

class GestaoCandidatosController(http.Controller):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    TIPO_LABELS = {
        'estagio': 'Estágio', 'posgraduacao': 'Pós-Graduação',
        'evento': 'Evento',   'suporte': 'Suporte',
    }
    COURSE_LABELS = {
        'informatica': 'Eng. Informática', 'gestao': 'Gestão',
        'direito': 'Direito', 'medicina': 'Medicina',
        'economia': 'Economia', 'outro': 'Outro',
    }
    STAGE_MAP = {
        'New': ('Novo', 'novo'),
        'Qualified': ('Em Análise', 'analise'),
        'Proposition': ('Em Análise', 'analise'),
        'Won': ('Aprovado', 'aprovado'),
        'Lost': ('Rejeitado', 'rejeitado'),
    }

    def _stage_info(self, lead):
        """Devolve (label, css_class) para o estágio de um lead."""
        name = lead.stage_id.name if lead.stage_id else 'New'
        return self.STAGE_MAP.get(name, ('Novo', 'novo'))

    def _prazo_info(self, deadline):
        """Devolve (str_data, label, css) para um prazo."""
        if not deadline:
            return '—', '', 'ok'
        hoje = date.today()
        diff = (deadline - hoje).days
        str_data = deadline.strftime('%d %b %Y')
        if diff < 0:
            return str_data, 'Encerrado', 'over'
        elif diff <= 5:
            return str_data, f'{diff}d restantes', 'warn'
        return str_data, f'{diff}d restantes', 'ok'

    def _candidato_dict(self, lead):
        """Converte um crm.lead num dict seguro para o template."""
        stage_label, stage_css = self._stage_info(lead)
        nome = lead.contact_name or lead.name or '—'
        return {
            'id':               lead.id,
            'nome':             nome,
            'initials':         nome[:2].upper(),
            'email':            lead.email_from or '—',
            'phone':            lead.phone or '',
            'student_number':   lead.student_number or '',
            'course_label':     self.COURSE_LABELS.get(lead.course, lead.course or '—'),
            'year':             lead.year or 0,
            'motivacao':        lead.description or '',
            'data':             lead.create_date.strftime('%d %b %Y') if lead.create_date else '—',
            'stage_label':      stage_label,
            'stage_css':        stage_css,
            'opportunity_type': lead.opportunity_type or 'estagio',
            'type_label':       self.TIPO_LABELS.get(lead.opportunity_type, ''),
            'oportunidade_id':  lead.oportunidade_id.id if lead.oportunidade_id else 0,
            'oportunidade_nome': lead.oportunidade_id.name if lead.oportunidade_id else '—',
            'oportunidade_empresa': lead.oportunidade_id.company_name if lead.oportunidade_id else '',
        }

    # ------------------------------------------------------------------
    # Rota 1: Lista de oportunidades com contador de candidatos
    # GET /gestao/oportunidades
    # ------------------------------------------------------------------
    @http.route('/gestao/oportunidades', type='http', auth='user', website=True)
    def lista_oportunidades(self, **kwargs):
        records = request.env['crm.oportunidades'].sudo().search(
            [('active', '=', True)], order='create_date desc'
        )
        oportunidades = []
        for op in records:
            str_data, prazo_label, prazo_css = self._prazo_info(op.deadline)
            empresa = op.company_name or 'UEM'
            oportunidades.append({
                'id':                 op.id,
                'name':               op.name,
                'company_name':       empresa,
                'initials':           empresa[:2].upper(),
                'opportunity_type':   op.opportunity_type,
                'type_label':         self.TIPO_LABELS.get(op.opportunity_type, ''),
                'deadline':           str_data,
                'prazo_label':        prazo_label,
                'prazo_css':          prazo_css,
                'active':             op.active,
                'description':        op.description or '',
                # conta directamente na BD via One2many
                'total_candidaturas': len(op.candidaturas_ids),
            })
        return request.render('crm_estudantil.page_gestao_oportunidades', {
            'oportunidades': oportunidades,
        })

    # ------------------------------------------------------------------
    # Rota 2: Detalhe de oportunidade + lista de candidatos
    # GET /gestao/oportunidades/<id>
    # ------------------------------------------------------------------
    @http.route('/gestao/oportunidades/<int:opp_id>', type='http', auth='user', website=True)
    def detalhe_oportunidade(self, opp_id, **kwargs):
        op = request.env['crm.oportunidades'].sudo().browse(opp_id)
        if not op.exists():
            return request.redirect('/gestao/oportunidades')

        str_data, prazo_label, prazo_css = self._prazo_info(op.deadline)
        empresa = op.company_name or 'UEM'

        opp = {
            'id':               op.id,
            'name':             op.name,
            'company_name':     empresa,
            'opportunity_type': op.opportunity_type,
            'type_label':       self.TIPO_LABELS.get(op.opportunity_type, ''),
            'deadline':         str_data,
            'prazo_label':      prazo_label,
            'prazo_css':        prazo_css,
            'description':      op.description or '',
            'active':           op.active,
        }

        # Candidatos ligados via One2many (já filtrados pelo ORM)
        candidatos = [self._candidato_dict(lead) for lead in op.candidaturas_ids]

        return request.render('crm_estudantil.page_gestao_oportunidade_detalhe', {
            'opp':        opp,
            'candidatos': candidatos,
        })

    # ------------------------------------------------------------------
    # Rota 3: Detalhe completo de um candidato individual
    # GET /gestao/candidatos/<id>
    # ------------------------------------------------------------------
    @http.route('/gestao/candidatos/<int:lead_id>', type='http', auth='user', website=True)
    def detalhe_candidato(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.redirect('/gestao/oportunidades')

        return request.render('crm_estudantil.page_gestao_candidato_detalhe', {
            'c': self._candidato_dict(lead),
        })