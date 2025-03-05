from odoo import models, fields, api, _


class ServiceRequestConfig(models.Model):
    _inherit = "service.request.config"

    service_request = fields.Selection(
        selection_add=[('exit_reentry_issuance','Exit Rentry issuance'),('exit_reentry_issuance_ext', 'Exit Re-entry (Extension)')], string="Requests", required=True,
        ondelete={'exit_reentry_issuance_ext': 'cascade','exit_reentry_issuance': 'cascade'})
