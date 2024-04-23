# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.account.models.account_move import PAYMENT_STATE_SELECTION

from functools import lru_cache



class CustomReportInvoice(models.AbstractModel):
    _name = 'report.aamalcom.custom_report_invoice'
    _description = 'Account report without payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        qr_code_urls = {}
        for invoice in docs:
            if invoice.display_qr_code:
                new_code_url = invoice.generate_qr_code()
                if new_code_url:
                    qr_code_urls[invoice.id] = new_code_url

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'qr_code_urls': qr_code_urls,
        }
