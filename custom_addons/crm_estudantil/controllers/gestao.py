# crm_estudantil/controllers/gestao.py
# pyrefly: ignore [missing-import]
from odoo import http
# pyrefly: ignore [missing-import]
from odoo.http import request
import json
from .validators import safe_id, sanitize_choice

class GestaoCandidaturasController(http.Controller):

    @http.route('/gestao/candidaturas', type='http', auth='user', website=True)
    def gestao_candidaturas(self, **kwargs):
        # Ler todas as candidaturas criadas pelo formulário (filtradas por student_number)
        leads = request.env['crm.lead'].sudo().search([
            ('student_number', '!=', False)
        ], order='create_date desc')

        # Agrupar por estágio (mapeamento simplificado)
        stages = {'novo': [], 'analise': [], 'aprovado': [], 'rejeitado': []}
        for lead in leads:
            stage_name = lead.stage_id.name if lead.stage_id else 'New'
            if stage_name == 'New':
                stages['novo'].append(lead)
            elif stage_name in ['Qualified', 'Proposition']:
                stages['analise'].append(lead)
            elif stage_name == 'Won':
                stages['aprovado'].append(lead)
            elif stage_name == 'Lost':
                stages['rejeitado'].append(lead)
            else:
                stages['novo'].append(lead)  # Fallback

        return request.render('crm_estudantil.page_gestao_candidaturas', {
            'stages': stages,
            'total': len(leads)
        })

    @http.route('/api/candidaturas/move', type='json', auth='user')
    def move_candidatura(self, lead_id, target_stage):
        try:
            lead_pk = safe_id(lead_id)
            if not lead_pk:
                return {'success': False, 'message': 'ID de candidatura inválido'}

            lead = request.env['crm.lead'].sudo().browse(lead_pk)
            if not lead.exists():
                return {'success': False, 'message': 'Candidatura não encontrada'}

            # Mapear estados simples para nomes de estágios do Odoo
            stage_map = {
                'novo': 'New',
                'analise': 'Qualified',
                'aprovado': 'Won',
                'rejeitado': 'Lost'
            }

            allowed = set(stage_map.keys())
            stage_key = sanitize_choice(target_stage, allowed, default=None)
            if stage_key is None:
                return {'success': False, 'message': 'Estado de destino inválido'}

            target_name = stage_map.get(stage_key, 'New')
            # Procurar estágio correspondente
            stage = request.env['crm.stage'].sudo().search([
                ('name', '=', target_name),
                ('team_id', '=', False)
            ], limit=1)

            if stage:
                lead.write({'stage_id': stage.id})
                return {'success': True}
            else:
                return {'success': False, 'message': f'Estágio "{target_name}" não encontrado no CRM'}
        except Exception as e:
            return {'success': False, 'message': str(e)}