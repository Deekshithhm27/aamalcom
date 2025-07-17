from odoo import models, fields, api

class DraftAccountMove(models.Model):
    _inherit = 'draft.account.move'

    nature_of_advance = fields.Text(
        string="Nature of Advance",
        compute='_compute_nature_of_advance',
        store=True,
        readonly=False,
    )

    service_request_type = fields.Selection(
        related='service_enquiry_id.service_request',
        store=True,
        readonly=True,
    )

    employee_bank_account_number = fields.Char(
        string="Employee Bank Account ID",
        compute='_compute_employee_bank_details',
        store=False
    )

    employee_bank_id = fields.Many2one(
        'res.bank',
        string="Employee Bank",
        compute='_compute_employee_bank_details',
        store=False
    )

    

    @api.depends('employee_id')
    def _compute_employee_bank_details(self):
        for rec in self:
            bank_account = rec.employee_id.bank_ids[:1]  # take first bank account
            rec.employee_bank_account_number = bank_account.acc_number if bank_account else False
            rec.employee_bank_id = bank_account.bank_id if bank_account else False


    @api.depends('service_enquiry_id.nature_of_advance', 'service_request_type')
    def _compute_nature_of_advance(self):
        for rec in self:
            if rec.service_request_type == 'salary_advance':
                rec.nature_of_advance = rec.service_enquiry_id.nature_of_advance
            else:
                rec.nature_of_advance = False
