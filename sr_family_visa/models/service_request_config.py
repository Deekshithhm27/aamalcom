from odoo import models, fields

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            
            ('family_visit_visa', 'Family Visit Visa')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={
            'family_visit_visa': 'cascade',
        }
    )
