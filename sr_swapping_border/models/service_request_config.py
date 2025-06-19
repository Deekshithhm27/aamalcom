from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('swapping_border_to_iqama', 'Swapping from border to Iqama Number')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'swapping_border_to_iqama': 'cascade'}
    )