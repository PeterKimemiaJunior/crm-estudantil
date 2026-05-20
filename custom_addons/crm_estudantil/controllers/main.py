# crm_estudantil/controllers/main.py
import json
# pyrefly: ignore [missing-import]
from odoo import http
# pyrefly: ignore [missing-import]
from odoo.http import request

class CrmEstudantilController(http.Controller):

    # 1. API para Submissão do Formulário
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

    # 2. Rota de Oportunidades (Dinâmica - já criada anteriormente)
    @http.route('/oportunidades', type='http', auth='public', website=True)
    def oportunidades(self, **kwargs):
        leads = request.env['crm.lead'].sudo().search([
            ('student_number', '!=', False),
            ('type', '=', 'lead')
        ], order='create_date desc')
        
        # Prepara os dados para o template
        opportunities = []
        for lead in leads:
            opportunities.append({
                'id': lead.id,
                'name': lead.name,
                'contact_name': lead.contact_name,
                'company_name': 'UEM', 
                'description': lead.description or 'Clica para ver detalhes.',
                'opportunity_type': lead.opportunity_type,
                'create_date': lead.create_date.strftime('%d %b %Y'),
                'initials': (lead.contact_name[:2] if lead.contact_name else '??').upper()
            })

        return request.render('crm_estudantil.page_oportunidades', {
            'opportunities': opportunities
        })

    # 3. Rota de FAQ (Estática com JS)
    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, **kwargs):
        return request.render('crm_estudantil.page_faq')

    # 4. Rota de Dashboard (DINÂMICA - Lê da Base de Dados)
    @http.route('/dashboard', type='http', auth='public', website=True)
    def dashboard(self, **kwargs):
        # Ler todos os leads
        all_leads = request.env['crm.lead'].sudo().search([('type', '=', 'lead')])
        total = len(all_leads)

        # Contar por estado (Stage)
        # Mapeamento: 'New' -> Novo, 'Qualified' -> Análise, 'Won' -> Ganho/Aprovado, 'Lost' -> Perdido
        stats = {
            'novo': len(all_leads.filtered(lambda l: not l.stage_id or l.stage_id.name == 'New')),
            'analise': len(all_leads.filtered(lambda l: l.stage_id.name in ['Qualified', 'Proposition'])),
            'aprovado': len(all_leads.filtered(lambda l: l.stage_id.name == 'Won')),
            'rejeitado': len(all_leads.filtered(lambda l: l.stage_id.name == 'Lost'))
        }

        # Calcular taxa de sucesso
        taxa_sucesso = 0
        if total > 0:
            taxa_sucesso = int((stats['aprovado'] / total) * 100)

        return request.render('crm_estudantil.page_dashboard', {
            'stats': stats,
            'total': total,
            'taxa_sucesso': taxa_sucesso
        })

    # 5. Rota de Candidatura (Formulário)
    @http.route('/candidatura', type='http', auth='public', website=True)
    def candidatura(self, **kwargs):
        return request.render('crm_estudantil.page_candidatura')

    # 6. Rota de Kanban (Pipeline CRM)
    @http.route('/kanban', type='http', auth='public', website=True)
    def kanban(self, **kwargs):
        return request.render('crm_estudantil.page_kanban')