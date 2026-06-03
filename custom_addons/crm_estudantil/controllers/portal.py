# crm_estudantil/controllers/portal.py
from odoo import http
from odoo.http import request
from datetime import date

class PortalEstudanteController(http.Controller):
    """
    Rotas públicas para o portal do estudante.
    Separadas do painel admin — sem sidebar, sem auth.
    """

    def _get_opportunities(self):
        """Reutilizável: busca todas as oportunidades activas e devolve lista de dicts."""
        records = request.env['crm.oportunidades'].sudo().search(
            [('active', '=', True)], order='create_date desc'
        )
        hoje = date.today()
        opps = []
        for op in records:
            # Calcular label e cor do prazo
            if op.deadline:
                diff = (op.deadline - hoje).days
                if diff < 0:
                    prazo_label = 'Prazo encerrado'
                    prazo_cor   = '#D85A30'
                elif diff <= 5:
                    prazo_label = f'Fecha em {diff} dia(s)!'
                    prazo_cor   = '#BA7517'
                else:
                    prazo_label = f'{diff} dias restantes'
                    prazo_cor   = '#1D9E75'
                deadline_str = op.deadline.strftime('%d %b %Y')
            else:
                prazo_label  = '—'
                prazo_cor    = '#5A6475'
                deadline_str = '—'

            empresa = op.company_name or 'UEM'
            opps.append({
                'id':               op.id,
                'name':             op.name or '',
                'company_name':     empresa,
                'description':      op.description or '',
                'opportunity_type': op.opportunity_type or 'estagio',
                'deadline':         deadline_str,
                'prazo_label':      prazo_label,
                'prazo_cor':        prazo_cor,
                'initials':         empresa[:2].upper(),
            })
        return opps

    # ------------------------------------------------------------------
    # /portal  — Home do estudante
    # ------------------------------------------------------------------
    @http.route('/portal', type='http', auth='public', website=True)
    def portal_home(self, **kwargs):
        opportunities = self._get_opportunities()
        return request.render('crm_estudantil.portal_home', {
            'opportunities': opportunities,
        })

    # ------------------------------------------------------------------
    # /portal/oportunidades  — Listagem completa
    # ------------------------------------------------------------------
    @http.route('/portal/oportunidades', type='http', auth='public', website=True)
    def portal_oportunidades(self, **kwargs):
        opportunities = self._get_opportunities()
        return request.render('crm_estudantil.portal_oportunidades', {
            'opportunities': opportunities,
        })

    # ------------------------------------------------------------------
    # /portal/candidatura  — Formulário de candidatura
    # Aceita ?opp_id= para pré-preencher o contexto da vaga
    # ------------------------------------------------------------------
    @http.route('/portal/candidatura', type='http', auth='public', website=True)
    def portal_candidatura(self, opp_id=None, **kwargs):
        oportunidade = None
        if opp_id:
            rec = request.env['crm.oportunidades'].sudo().browse(int(opp_id))
            if rec.exists():
                empresa = rec.company_name or 'UEM'
                deadline_str = rec.deadline.strftime('%d %b %Y') if rec.deadline else '—'
                oportunidade = {
                    'id':               rec.id,
                    'name':             rec.name,
                    'company_name':     empresa,
                    'opportunity_type': rec.opportunity_type,
                    'deadline':         deadline_str,
                }
        return request.render('crm_estudantil.portal_candidatura', {
            'oportunidade': oportunidade,
        })

    # ------------------------------------------------------------------
    # /portal/faq  — Suporte
    # ------------------------------------------------------------------
    @http.route('/portal/faq', type='http', auth='public', website=True)
    def portal_faq(self, **kwargs):
        return request.render('crm_estudantil.portal_faq')