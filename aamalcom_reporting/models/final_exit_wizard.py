# aamalcom_reporting/models/final_exit_issuance_report_wizard.py

from odoo import models, fields, api, _
from datetime import date, timedelta

class FinalExitIssuanceReportWizard(models.TransientModel):
    _name = 'final.exit.issuance.report.wizard'
    _description = 'Final Exit Issuance Report Wizard'

    # New fixed service request type for "Final Exit Issuance"
    service_request_type_fixed = fields.Selection([
        ('final_exit_issuance', 'Final exit Issuance'),
    ], string="Service Request Name", default='final_exit_issuance', readonly=True, store=True)

    # New boolean fields for filtering
    is_inside_ksa = fields.Boolean(string="Inside KSA")
    is_outside_ksa = fields.Boolean(string="Outside KSA")

    from_date = fields.Date(string="From Date", required=True, default=lambda self: date.today() - timedelta(days=30))
    to_date = fields.Date(string="To Date", required=True, default=lambda self: date.today())

    def print_final_exit_issuance_report(self):
        """
        Action to print the Final Exit Issuance Report.
        """
        self.ensure_one()

        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
            'is_inside_ksa': self.is_inside_ksa,
            'is_outside_ksa': self.is_outside_ksa,
        }
        # Reference the new report action
        return self.env.ref('aamalcom_reporting.action_final_exit_issuance_report_pdf').report_action(self, data=data)