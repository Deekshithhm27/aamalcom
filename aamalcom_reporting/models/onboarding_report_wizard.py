from odoo import models, fields

class OnboardingReportWizard(models.TransientModel):
    _name = 'onboarding.report.wizard'
    _description = 'Onboarding Report Wizard'

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    client_id = fields.Many2one(
    'res.partner',
    string="Client",
    domain="[('is_company', '=', True), ('parent_id', '=', False)]"
    )

    def print_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'client_id': self.client_id.id,
        }
        return self.env.ref('aamalcom_reporting.action_onboarding_report_pdf').report_action(self, data=data)
