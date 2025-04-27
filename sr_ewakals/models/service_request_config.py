from odoo import models, fields

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('e_wakala', 'E-Wakala'),
            ('cancelled_e_wakala', 'Cancellation E-Wakala'),
            
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={
            'e_wakala': 'cascade',
            'cancelled_e_wakala': 'cascade'
            
        }
    )