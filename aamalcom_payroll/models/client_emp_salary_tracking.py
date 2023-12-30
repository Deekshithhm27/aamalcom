# -*- coding:utf-8 -*-

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ClientEmployeeSalaryTracking(models.Model):
    _name = 'client.emp.salary.tracking'
    _description = 'Client Employee Monthly Salary Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="Sequence",required=True, index=True, copy=False, default='New',help="The Unique Sequence no")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True, readonly=True)

    client_emp_sequence = fields.Char(string="Employee id",help="Employee Id as per client's record")
    employee_id = fields.Many2one('hr.employee',string="Employee",store=True,domain=[('custom_employee_type', '=', 'external')])
    client_id = fields.Many2one('res.users',string="Client",related="employee_id.client_id")
    client_parent_id = fields.Many2one('res.partner',string="Client Parent",compute="update_payroll_data",store=True)
    custom_employee_type = fields.Selection([('external','External'),('internal','Internal')],string="Employee Type",compute="update_payroll_data",store=True)
    contract_id = fields.Many2one('hr.contract',string="Contract",store=True)
    struct_id = fields.Many2one('hr.payroll.structure',string="Salary Structure",store=True,compute="update_payroll_data")

    worked_days = fields.Float(string="Worked Days")

    wage = fields.Monetary('Basic Salary', tracking=True, help="Employee's monthly gross wage.",compute="compute_salary_details",store=True)
    hra = fields.Monetary(string='HRA', help="House rent allowance.",compute="compute_salary_details",store=True)
    travel_allowance = fields.Monetary(string="Transportation Allowance", help="Transportation allowance",compute="compute_salary_details",store=True)
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances",compute="compute_salary_details",store=True)
    other_deductions = fields.Monetary(string="Other Deductions", help="Other Deductions")
    arrears = fields.Monetary(string="Arrears",help="Arrears")
    advances = fields.Monetary(string="Advances",help="Advances")
    overtime = fields.Monetary(string="Overtime",help="Overtime")
    additions = fields.Monetary(string="Additions",help="Additions")

    gross_salary = fields.Float(string="Gross Salary",compute="compute_gross_salary",store=True)
    net_salary = fields.Float(string="Gross Salary",compute="compute_net_salary",store=True)

    state = fields.Selection([('draft','Draft'),('done','Done')],default="draft")

    date_start = fields.Date(string='Date From', required=True, readonly=True,
                             states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_end = fields.Date(string='Date To', required=True, readonly=True,
                           states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    gosi_charges = fields.Float(string="Gosi Charges")

    

    invoice_id = fields.Many2one('account.move',string="Invoice Ref")
    is_invoiced = fields.Boolean(string="Is invoiced",default=False)

    @api.depends('wage','hra','travel_allowance','other_allowance','other_deductions','arrears','advances','overtime','additions')
    def compute_gross_salary(self):
        for line in self:
            line.gross_salary = (line.wage + line.hra + line.travel_allowance + line.other_allowance + line.arrears + line.advances + line.overtime + line.additions)

    @api.depends('wage','hra','travel_allowance','other_allowance','other_deductions','arrears','advances','overtime','additions')
    def compute_net_salary(self):
        for line in self:
            line.net_salary = (line.wage + line.hra + line.travel_allowance + line.other_allowance + line.arrears + line.advances + line.overtime + line.additions) - line.other_deductions


    @api.depends('client_emp_sequence','employee_id','contract_id','client_id')
    def update_payroll_data(self):
        for line in self:
            line.struct_id = line.contract_id.struct_id.id
            line.custom_employee_type = line.employee_id.custom_employee_type
            line.client_parent_id = line.client_id.partner_id.parent_id.id

    @api.depends('contract_id')
    def compute_salary_details(self):
        for line in self:
            if line.contract_id:
                line.wage = line.contract_id.wage
                line.hra = line.contract_id.hra
                line.travel_allowance = line.contract_id.travel_allowance
                line.other_allowance = line.contract_id.other_allowance
            else:
                raise ValidationError(("No Contract defined for %s")%(line.employee_id.name))


   
    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            company_id = vals.get('company_id') or self.default_get(['company_id'])['company_id']
            self_comp = self.with_company(company_id)
            employee_id = self.env['hr.employee'].search([('client_emp_sequence','=',vals.get('client_emp_sequence'))],limit=1)
            vals['employee_id'] = employee_id.id
            contract_id = self.env['hr.contract'].search([('employee_id','=',employee_id.id),('state','=','open')],limit=1)
            vals['contract_id'] = contract_id.id
             # Check wage before saving
            if 'arrears' in vals:
                self._check_arrears(vals_list, self_comp)
            if 'advances' in vals:
                self._check_advances(vals_list, self_comp)
            if 'other_deductions' in vals:
                self._check_other_deductions(vals_list, self_comp)
            if 'gosi_charges' not in vals:
                self._check_gosi_charges(vals_list, self_comp)
            
            if vals.get('name', 'New') == 'New':
                vals['name'] = self_comp.env['ir.sequence'].next_by_code('client.emp.salary.tracking') or 'New'
                # vals['name'] = next_sequence

            new_vals_list.append(vals)
        res = super(ClientEmployeeSalaryTracking, self_comp).create(new_vals_list)

        return res

    def _check_gosi_charges(self,vals_list, self_comp):
        for vals in vals_list:
            gosi_id = self.env['gosi.charges'].search([('id','!=',False)],limit=1)
            contract_id = self_comp.env['hr.contract'].search([
                    ('employee_id', '=', vals['employee_id']),
                    ('state', '=', 'open')
                ], limit=1)
            if gosi_id:
                vals['gosi_charges'] = ((contract_id.wage + contract_id.hra) * float(gosi_id.name))/100



    def _check_arrears(self, vals_list, self_comp):
        # since arrears are updated periodically, we are updating the values to contract,
        # so that it would be easier to fetch and display in salary computation in payroll

        for vals in vals_list:
            if vals.get('employee_id'):
                contract_id = self_comp.env['hr.contract'].search([
                    ('employee_id', '=', vals['employee_id']),
                    ('state', '=', 'open')
                ], limit=1)
                contract_id.update({
                    'arrears':vals['arrears']
                    })

    def _check_other_deductions(self, vals_list, self_comp):
        # since arrears are updated periodically, we are updating the values to contract,
        # so that it would be easier to fetch and display in salary computation in payroll

        for vals in vals_list:
            if vals.get('employee_id'):
                contract_id = self_comp.env['hr.contract'].search([
                    ('employee_id', '=', vals['employee_id']),
                    ('state', '=', 'open')
                ], limit=1)
                contract_id.update({
                    'other_deductions':vals['other_deductions']
                    })
                

    def _check_advances(self, vals_list, self_comp):
        # since advances are updated periodically, we are updating the values to contract,
        # so that it would be easier to fetch and display in salary computation in payroll
        for vals in vals_list:
            if vals.get('employee_id'):
                contract_id = self_comp.env['hr.contract'].search([
                    ('employee_id', '=', vals['employee_id']),
                    ('state', '=', 'open')
                ], limit=1)
                contract_id.update({
                    'advances':vals['advances']
                    })
                
