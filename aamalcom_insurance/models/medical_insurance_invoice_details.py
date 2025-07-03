# File: aamalcom_insurance/models/medical_insurance_deletion.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MedicalInsuranceInvoiceDetails(models.Model):
    _name = 'medical.insurance.invoice.details'
    _description = 'Employee Insurance Invoice Details'

    name = fields.Char(string='Reference', copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoice_created','Invoice Created'),
        ('invoiced', 'Invoiced')
    ], string='Status', default='draft', tracking=True)
    invoice_id = fields.Many2one('account.move')

    client_parent_id = fields.Many2one('res.partner', string='Client',domain="[('is_company','=',True),('parent_id','=',False)]")
    client_emp_sequence = fields.Char(string='Employee Number', required=True)
    iqama_no = fields.Char(string='Iqama')
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Id")
    employee_id = fields.Many2one('hr.employee',string='Employee Name')
    member = fields.Char(string='Member')
    member_id = fields.Char(string='Member ID (Bupa)')
    insurance_activation_date = fields.Date(string='Insurance Activation Date')
    insurance_deactivation_date = fields.Date(string='Insurance De-Activation Date')
    insurance_expiration_date = fields.Date(string='Insurance Expiration Date')
    medical_class = fields.Char(string='Medical Class')
    total_amount = fields.Float(string='Total Amount')
    insurance_type = fields.Selection([
        ('enrollment', 'Enrollment'),
        ('deletion', 'Deletion')
    ], string='Insurance Type', required=True)


    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.insurance.invoice.details')
            if vals.get('member_id'):
                emp = self.env['hr.employee'].search([('member_no', '=', vals['member_id'])], limit=1)
                if emp:
                    vals['iqama_no'] = emp.iqama_no
                    vals['sponsor_id'] = emp.sponsor_id.id
                    vals['employee_id'] = emp.id
                    vals['client_parent_id'] = emp.client_id.partner_id.parent_id.id
        res = super(MedicalInsuranceInvoiceDetails,self).create(vals_list)
        return res

    @api.onchange('member_id')
    def _onchange_member_id(self):
        if self.member_id:
            emp = self.env['hr.employee'].search([('member_no', '=', self.member_id)], limit=1)
            if emp:
                self.iqama_no = emp.iqama_no
                self.sponsor_id = emp.sponsor_id.id
                self.employee_id = emp.id
                self.client_parent_id = emp.client_id.partner_id.parent_id.id
