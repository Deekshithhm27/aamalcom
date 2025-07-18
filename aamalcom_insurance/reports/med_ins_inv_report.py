from odoo import models

class InsuranceSummaryReport(models.AbstractModel):
    _name = 'report.aamalcom_insurance.med_ins_inv_summary'
    _description = 'Insurance Summary Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['medical.insurance.invoice.report.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'medical.insurance.invoice.report.wizard',
            'docs': docs,
            'data': data,  # now available in QWeb as 'data'
        }
