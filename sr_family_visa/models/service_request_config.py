from odoo import models, fields

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('family_resident', 'Family Resident Visa Application'),
            ('family_visa_letter', 'Family Visa Letter'),
            ('istiqdam_form','Istiqdam Form(Family Visa Letter)'),
            ('family_visit_visa', 'Family Visit Visa')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={
            'family_resident': 'cascade',
            'family_visa_letter': 'cascade',
            'istiqdam_form': 'cascade',
            'family_visit_visa': 'cascade',
        }
    )
