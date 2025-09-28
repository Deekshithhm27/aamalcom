# In wizard/partner_ledger_xsl.py

from odoo import models, fields

class AccountPartnerLedger(models.TransientModel):
    _name = "account.report.partner.ledger"
    _inherit = "account.common.partner.report"
    
    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on "
                                     "report if the currency differs from "
                                     "the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')

    def _get_report_data(self, data):
        """Prepares report data by updating the form context."""
        data = self.pre_print_report(data)
        data['form'].update({
            'reconciled': self.reconciled,
            'amount_currency': self.amount_currency,
        })
        return data

    def check_report(self):
        """Public method called from the XML button to start the report generation."""
        data = {}
        data['form'] = self.read([
            'date_from', 'date_to', 'journal_ids', 'target_move',
            'company_id', 'partner_ids', 'result_selection',
            'payment_type', 'amount_currency', 'reconciled'
        ])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang'))
        
        # Call the private method that handles the report action
        return self._print_report(data)

    def _print_report(self, data):
        """Private method that triggers the PDF or XLSX report action."""
        data = self._get_report_data(data)
        
        if self.env.context.get('xlsx_report'):
            return self.env.ref('accounting_pdf_reports.action_report_partner_ledger_xlsx').report_action(self, data=data)

        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').with_context(landscape=True).report_action(self, data=data)