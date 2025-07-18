from odoo import models

class LifeInsuranceSummaryReport(models.AbstractModel):
    _name = 'report.aamalcom_insurance.life_ins_inv_summary'
    _description = 'Life Insurance Summary Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['life.insurance.invoice.report.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'life.insurance.invoice.report.wizard',
            'docs': docs,
            'data': data,  # now available in QWeb as 'data'
        }
