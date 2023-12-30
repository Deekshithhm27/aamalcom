# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'
    
    create_payment_request = fields.Boolean(string="Create Payment Request",store=True,compute="update_create_payment_request")

    @api.depends('self_bill')
    def update_create_payment_request(self):
        for line in self:
            if line.self_bill:
                line.create_payment_request = True
            else:
                line.create_payment_request = False

    def action_create_payment_req(self):
        vals = {
            'client_id': self.client_id.id,
            'client_parent_id':self.client_id.parent_id.id,
            'employee_id':self.employee_id.id,
            'amount':self.total_amount,
            'service_enquiry_id':self.id
        }
        payment_approval_id = self.env['account.payment.approval'].sudo().create(vals)

    draft_invoices_count = fields.Integer(string="Invoices",compute='_compute_payments_count')


    def _compute_payments_count(self):
        for line in self:
            invoice_id = self.env['draft.account.move'].search([('service_enquiry_id', '=', line.id)])
            line.draft_invoices_count = len(invoice_id)



    def action_process_complete(self):
        existing_invoice = self.env['draft.account.move'].search([
            ('service_enquiry_id', '=', self.id)], limit=1)
        if existing_invoice:
            raise ValidationError(_('Invoice is already created for this Service Request'))
        for record in self:
            if record.billable_to_client == True: 

                # Create draft.account.move record
                account_move = self.env['draft.account.move'].create({
                    'client_id': self.client_id.id,
                    'client_parent_id':self.client_id.parent_id.id,
                    'service_enquiry_id': self.id,
                    'move_type':'service_ticket',
                })

                account_move_line = self.env['draft.account.move.line'].create({
                    'move_id': account_move.id,
                    'employee_id': record.employee_id.id,
                    'price_unit': record.total_amount,
                    'quantity':1,
                    'name':f"{record.employee_id.sequence} - {record.service_request_config_id.name}"
                })

        return super(ServiceEnquiry, self).action_process_complete()


        