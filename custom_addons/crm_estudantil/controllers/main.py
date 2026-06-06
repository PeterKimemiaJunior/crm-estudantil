# pyrefly: ignore [missing-import]
from odoo import http
# pyrefly: ignore [missing-import]
from odoo.http import request
import json

class CrmEstudantilController(http.Controller):

    @http.route('/oportunidades', type='http', auth='public', website=True)
    def oportunidades(self, **kwargs):
        records = request.env['crm.oportunidades'].sudo().search([('active', '=', True)])
        opportunities = []
        for op in records:
            empresa = op.company_name or 'UEM'
            opportunities.append({
                'id':               op.id,
                'name':             op.name or '',
                'company_name':     empresa,
                'description':      op.description or '',
                'opportunity_type': op.opportunity_type or 'estagio',
                'deadline':         op.deadline.strftime('%d %b %Y') if op.deadline else '—',
                'initials':         empresa[:2].upper(),
                'total_candidaturas': op.total_candidaturas,
            })
        return request.render('crm_estudantil.page_oportunidades', {'opportunities': opportunities})

    @http.route('/candidatura', type='http', auth='public', website=True)
    def candidatura(self, lead_id=None, **kwargs):
        oportunidade = None
        if lead_id:
            oportunidade = request.env['crm.oportunidades'].sudo().browse(int(lead_id))
            if not oportunidade.exists():
                oportunidade = None
        return request.render('crm_estudantil.page_candidatura', {'oportunidade': oportunidade})

    @http.route('/crm_estudantil/submit_lead', type='json', auth='public', methods=['POST'])
    def submit_lead(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            params = payload.get('params', {})

            from .validators import (
                sanitize_text, sanitize_phone, validate_email,
                sanitize_choice, safe_int, safe_id
            )

            # required fields
            campos_obrigatorios = {
                'name': 'Nome', 'email': 'Email',
                'student_number': 'Número de Estudante', 'course': 'Curso',
            }
            for campo, label in campos_obrigatorios.items():
                if not str(params.get(campo, '')).strip():
                    return {'success': False, 'message': f'Campo obrigatório em falta: {label}'}

            nome = sanitize_text(params.get('name'), max_len=120)
            email_raw = params.get('email')
            if not validate_email(email_raw):
                return {'success': False, 'message': 'Email inválido.'}
            email = sanitize_text(email_raw, max_len=120)

            phone = sanitize_phone(params.get('phone'), max_len=32)
            num = sanitize_text(params.get('student_number'), max_len=20)

            allowed_courses = {'informatica', 'gestao', 'direito', 'medicina', 'economia', 'outro'}
            curso = sanitize_choice(params.get('course'), allowed_courses, default='outro')

            ano = safe_int(params.get('year'), default=0, min_value=0, max_value=2100)
            motiv = sanitize_text(params.get('motivation'), max_len=2000)

            # Busca a oportunidade se vier oportunidade_id
            oportunidade = None
            allowed_types = {'estagio', 'posgraduacao', 'evento', 'suporte'}
            tipo = sanitize_choice(params.get('opportunity_type'), allowed_types, default='estagio')
            opp_id = safe_id(params.get('oportunidade_id'))
            if opp_id:
                rec = request.env['crm.oportunidades'].sudo().browse(opp_id)
                if rec.exists():
                    oportunidade = rec
                    tipo = sanitize_choice(rec.opportunity_type, allowed_types, default=tipo)

            stage = request.env['crm.stage'].sudo().search([('name', '=', 'New')], limit=1)

            # CREATE: cria a candidatura e liga à oportunidade
            request.env['crm.lead'].sudo().create({
                'name':             f'Candidatura: {nome}',
                'contact_name':     nome,
                'email_from':       email,
                'phone':            phone,
                'student_number':   num,
                'course':           curso,
                'year':             ano,
                'opportunity_type': tipo,
                'description':      motiv,
                'type':             'lead',
                'stage_id':         stage.id if stage else False,
                'oportunidade_id':  oportunidade.id if oportunidade else False,
            })

            return {'success': True, 'message': 'Candidatura registada com sucesso!'}

        except Exception:
            return {'success': False, 'message': 'Erro interno no servidor.'}

    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, **kwargs):
        return request.render('crm_estudantil.page_faq')

    @http.route('/dashboard', type='http', auth='public', website=True)
    def dashboard(self, **kwargs):
        all_leads = request.env['crm.lead'].sudo().search([('type', '=', 'lead')])
        total = len(all_leads)
        stats = {
            'novo':      len(all_leads.filtered(lambda l: not l.stage_id or l.stage_id.name == 'New')),
            'analise':   len(all_leads.filtered(lambda l: l.stage_id and l.stage_id.name in ['Qualified', 'Proposition'])),
            'aprovado':  len(all_leads.filtered(lambda l: l.stage_id and l.stage_id.name == 'Won')),
            'rejeitado': len(all_leads.filtered(lambda l: l.stage_id and l.stage_id.name == 'Lost')),
        }
        taxa_sucesso = int((stats['aprovado'] / total) * 100) if total > 0 else 0
        return request.render('crm_estudantil.page_dashboard', {
            'stats': stats, 'total': total, 'taxa_sucesso': taxa_sucesso,
        })

    @http.route('/kanban', type='http', auth='public', website=True)
    def kanban(self, **kwargs):
        return request.render('crm_estudantil.page_kanban')

    @http.route('/criar-oportunidade', type='http', auth='public', website=True)
    def criar_oportunidade(self, **kwargs):
        return request.render('crm_estudantil.page_criar_oportunidade')

    @http.route('/api/oportunidades/create', type='json', auth='public', methods=['POST'])
    def submit_oportunidade(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            params = payload.get('params', payload)
            nome = (params.get('name') or '').strip()
            if not nome:
                return {'success': False, 'message': 'Título é obrigatório.'}
            request.env['crm.oportunidades'].sudo().create({
                'name':             nome,
                'company_name':     (params.get('company_name') or '').strip(),
                'description':      (params.get('description') or '').strip(),
                'opportunity_type': params.get('opportunity_type', 'estagio'),
            })
            return {'success': True, 'message': 'Oportunidade criada com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # 7. Rota de Questionários (Inquéritos)
    @http.route('/questionarios', type='http', auth='public', website=True)
    def questionarios(self, **kwargs):
        surveys = request.env['survey.survey'].sudo().search([('active', '=', True)])
        return request.render('crm_estudantil.page_questionarios', {
            'surveys': surveys
        })
