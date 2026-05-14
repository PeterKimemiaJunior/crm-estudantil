# crm_estudantil/controllers/main.py
import json
from odoo import http
from odoo.http import request

class CrmEstudantilController(http.Controller):

    @http.route('/crm_estudantil/submit_lead', type='json', auth='public', methods=['POST'])
    def submit_lead(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            params = payload.get('params', {})

            # Validação básica
            if not params.get('name') or not params.get('email'):
                return {'success': False, 'message': 'Nome e email são obrigatórios.'}

            # Preparar valores para o CRM
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
                'type': 'lead'  # Garante que entra como Lead no pipeline
            }

            # Cria o registo (sudo() para permitir acesso público inicial)
            request.env['crm.lead'].sudo().create(vals)
            return {'success': True, 'message': 'Candidatura registada com sucesso!'}

        except Exception as e:
            return {'success': False, 'message': f'Erro interno: {str(e)}'}