from odoo import models, fields, api

class CrmSurveyWizard(models.TransientModel):
    _name = 'crm.survey.wizard'
    _description = 'Assistente para Envio de Questionários'

    survey_id = fields.Many2one('survey.survey', string='Questionário', required=True, domain=[('active', '=', True)])
    lead_ids = fields.Many2many('crm.lead', string='Candidatos', required=True)
    message = fields.Text(string='Mensagem Adicional')

    @api.model
    def default_get(self, fields_list):
        res = super(CrmSurveyWizard, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['lead_ids'] = [(6, 0, active_ids)]
        return res

    def action_send_email(self):
        for lead in self.lead_ids:
            if not lead.email_from:
                continue

            # Construir URL do questionário
            survey_url = f"/survey/start/{self.survey_id.access_token}"
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            full_url = f"{base_url}{survey_url}"

            # Construir corpo do email
            msg_body = f"""
                <p>Olá {lead.contact_name or lead.name},</p>
                <p>Foi convidado a responder ao questionário: <strong>{self.survey_id.title}</strong>.</p>
                <p>{self.message or ''}</p>
                <br/>
                <a href="{full_url}" style="padding: 8px 16px; background-color: #0F4C81; color: white; text-decoration: none; border-radius: 4px;">
                    Responder ao Questionário
                </a>
                <br/><br/>
                <p>Obrigado,</p>
                <p>Equipa CRM Estudantil UEM</p>
            """

            # Enviar email via Odoo Mail
            mail_values = {
                'subject': f"Questionário: {self.survey_id.title}",
                'body_html': msg_body,
                'email_to': lead.email_from,
                'email_from': self.env.user.email_formatted or self.env.company.email,
            }
            self.env['mail.mail'].create(mail_values).send()

        return {'type': 'ir.actions.act_window_close'}
