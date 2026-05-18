# crm_estudantil/controllers/main.py
import json
# pyrefly: ignore [missing-import]
from odoo import http
# pyrefly: ignore [missing-import]
from odoo.http import request

class CrmEstudantilController(http.Controller):

    # 1. Rota para Submissão do Formulário (Candidatura)
    @http.route('/crm_estudantil/submit_lead', type='json', auth='public', methods=['POST'])
    def submit_lead(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data)
            params = payload.get('params', {})

            if not params.get('name') or not params.get('email'):
                return {'success': False, 'message': 'Nome e email são obrigatórios.'}

            vals = {
                'name': f"Candidatura: {params.get('name')} ({params.get('opportunity_type', 'Geral')})",
                'contact_name': params.get('name'),
                'email_from': params.get('email'),
                'phone': params.get('phone', ''),
                'student_number': params.get('student_number', ''),
                'course': params.get('course', ''),
                'year': int(params.get('year', 0)) if params.get('year') else 0,
                'opportunity_type': params.get('opportunity_type', 'estagio'),
                'description': params.get('motivation', ''),
                'type': 'lead'
            }
            request.env['crm.lead'].sudo().create(vals)
            return {'success': True, 'message': 'Candidatura registada com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': f'Erro interno: {str(e)}'}

    # 2. Rota para a Página de Oportunidades (Dinâmica)
    @http.route('/oportunidades', type='http', auth='public', website=True)
    def oportunidades(self, **kwargs):
        # Lê todos os leads ativos (excluindo os rejeitados/perdidos para não aparecerem no site)
        # Assumimos que leads 'Lost' não são visíveis ou usamos um filtro simples
        leads = request.env['crm.lead'].sudo().search([
            ('type', '=', 'lead'),
            ('active', '=', True)
        ], order='create_date desc')

        # Preparamos uma lista de dicionários para o template
        opportunities = []
        for lead in leads:
            opportunities.append({
                'id': lead.id,
                'name': lead.name,
                'description': lead.description or 'Clique para saber mais detalhes sobre esta oportunidade.',
                'opportunity_type': lead.opportunity_type, # estagio, posgraduacao, evento, suporte
                'company_name': 'UEM - Faculdade de ' + (dict(lead._fields['course'].selection).get(lead.course, 'Geral') or 'Geral'),
                'create_date': lead.create_date.strftime('%d %b %Y'),
                'initials': (lead.contact_name[:2] if lead.contact_name else '??').upper()
            })

        return request.render('crm_estudantil.page_oportunidades', {
            'opportunities': opportunities
        })

    # 3. Rota para a Página de FAQ (Estática com JS)
    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, **kwargs):
        return request.render('crm_estudantil.page_faq')