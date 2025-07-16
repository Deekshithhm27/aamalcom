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
        related='employee_id.bank_account_id.acc_number',
        readonly=True,
        store=False,
        help="Bank Account Number of the Employee associated with this service request."
    )

    employee_bank_id = fields.Many2one(
        'res.bank',
        string="Employee Bank",
        related='employee_id.bank_account_id.bank_id',
        store=False,
        readonly=True
    )

    iban = fields.Char(
    string="IBAN",
    related='employee_bank_id.bic',
    readonly=True,
    store=True
    )

    @api.depends('service_enquiry_id.nature_of_advance', 'service_request_type')
    def _compute_nature_of_advance(self):
        for rec in self:
            if rec.service_request_type == 'salary_advance':
                rec.nature_of_advance = rec.service_enquiry_id.nature_of_advance
            else:
                rec.nature_of_advance = False
