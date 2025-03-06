from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('passport_info_update', 'Passport Information Update')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'passport_info_update': 'cascade'}
    )