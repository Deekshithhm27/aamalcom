# models/transfer_report_wizard.py

from odoo import models, fields, api, _

class TransferReportWizard(models.TransientModel):
    _name = 'transfer.report.wizard'
    _description = 'Transfer Request Report Wizard'

    service_request_type_fixed = fields.Selection([
        ('transfer_req', 'Transfer Request Initiation')
    ], string="Service Request Name", default='transfer_req', readonly=True, store=True)

    transfer_type = fields.Selection([
        ('to_aamalcom','To Aamalcom'),
        ('to_another_establishment','To another Establishment')
    ], string="Transfer Type", required=True)
    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)

    def print_transfer_report(self):
        """
        Action to print the Transfer Request report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'transfer_type': self.transfer_type,
            'service_request_type_fixed': self.service_request_type_fixed,
        }
        return self.env.ref('aamalcom_reporting.action_transfer_report_pdf').report_action(self, data=data)