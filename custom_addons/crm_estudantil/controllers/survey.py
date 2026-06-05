from odoo import http
from odoo.http import request

class SurveyController(http.Controller):

    @http.route(
        '/questionarios',
        type='http',
        auth='user',
        website=True
    )
    def questionarios(self, **kwargs):

        surveys = request.env[
            'survey.survey'
        ].sudo().search([
            ('active', '=', True)
        ])

        return request.render(
            'crm_estudantil.page_questionarios',
            {
                'surveys': surveys
            }
        )