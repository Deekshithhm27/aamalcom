# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class ClientPayslipDocument(models.Model):
    _name = 'client.payslip.document'
    _description = 'Payslip Document'
    
    name = fields.Char(string='Document Name', required=True)
    document_file = fields.Binary(string='File', required=True)
    
    # Replace the document_filename with a date field
    upload_date = fields.Date(string='Upload Date', default=fields.Date.today, readonly=True)
    
    # This is the many2one field linking back to the main record
    payslip_approval_id = fields.Many2one('client.payslip.approval', string='Payslip Approval', ondelete='cascade')
    document_filename=fields.Char(string="Filename")