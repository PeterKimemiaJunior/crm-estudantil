from odoo import http
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

            campos_obrigatorios = {
                'name': 'Nome', 'email': 'Email',
                'student_number': 'Número de Estudante', 'course': 'Curso',
            }
            for campo, label in campos_obrigatorios.items():
                if not params.get(campo, '').strip():
                    return {'success': False, 'message': f'Campo obrigatório em falta: {label}'}

            nome  = params['name'].strip()[:120]
            email = params['email'].strip()[:120]
            phone = params.get('phone', '').strip()[:32]
            num   = params.get('student_number', '').strip()[:20]
            curso = params.get('course', 'outro')
            ano   = int(params['year']) if str(params.get('year', '')).isdigit() else 0
            motiv = params.get('motivation', '').strip()[:2000]

            # Busca a oportunidade se vier oportunidade_id
            oportunidade = None
            tipo = params.get('opportunity_type', 'estagio')
            try:
                opp_id_raw = params.get('oportunidade_id')
                if opp_id_raw and int(opp_id_raw) > 0:
                    rec = request.env['crm.oportunidades'].sudo().browse(int(opp_id_raw))
                    if rec.exists():
                        oportunidade = rec
                        tipo = rec.opportunity_type
            except (ValueError, TypeError):
                pass

            stage = request.env['crm.stage'].sudo().search([('name', '=', 'New')], limit=1)

            # --------------------------------------------------------
            # INSERT: cria a candidatura e liga à oportunidade
            # --------------------------------------------------------
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

        except Exception as e:
            return {'success': False, 'message': f'Erro interno: {str(e)}'}

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