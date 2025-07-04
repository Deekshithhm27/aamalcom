# models/muqeem_report_wizard.py

from odoo import models, fields, api, _

class MuqeemReportWizard(models.TransientModel):
    _name = 'muqeem.report.wizard'
    _description = 'Muqeem Report Wizard'

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    service_request = fields.Selection([
        ('hr_card','Issuance for HR card'),
        ('final_exit_issuance','Final exit Issuance'),
        ('muqeem_dropout', 'Muqeem Dropout'),
        ('iqama_card_req','New Physical Iqama Card Request'),
        ('iqama_renewal','Iqama Renewal')
        
    ], string="Service Requests", required=True)

    def print_muqeem_report(self):
        """
        Action to print the Muqeem report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request': self.service_request, # Pass the new service_request field
        }
        # The 'action_muqeem_report_pdf' will be defined in XML later
        return self.env.ref('aamalcom_reporting.action_muqeem_report_pdf').report_action(self, data=data)