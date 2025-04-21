from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('general_query','General Query')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'general_query': 'cascade'}

    )