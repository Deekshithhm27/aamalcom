from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[('salary_advance', 'Salary Advance')],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'salary_advance': 'cascade'}
    )
    
    currency_id = fields.Many2one(
            'res.currency',
            string='Currency',
            default=lambda self: self.env.company.currency_id,
            )
        
    salary_advance_amount = fields.Monetary("Salary Advance Amount",
    currency_field='currency_id') 
        
    nature_of_advance = fields.Text("Nature of Advance")
    invoiced = fields.Boolean(string="Invoiced")
    to_be_invoiced = fields.Boolean(string="To be Invoiced")
    unpaid_inv_reason = fields.Text("Reason for Unpaid Invoice")
    hide_unpaid_reason = fields.Boolean(
        string="Hide Reason for Unpaid Invoice",
        compute="_compute_hide_unpaid_reason",
        store=False
    )
    invoiced_ref = fields.Many2one(
    'account.move',
    string="Invoiced Ref No.*",
    store=True,
    tracking=True,
    copy=False
    )

   
    @api.model
    def update_pricing(self):  
        super(ServiceEnquiry, self).update_pricing()  
        for record in self:
            if  record.service_request == 'salary_advance':
                pricing_id = self.env['service.pricing'].search([
                    ('service_request_type', '=', record.service_request_type),
                    ('service_request', '=', record.service_request)], limit=1)
                for p_line in pricing_id.pricing_line_ids:
                    if p_line.duration_id == record.employment_duration:
                        record.service_enquiry_pricing_ids.create({
                            'name': pricing_id.name,
                            'service_enquiry_id': record.id,
                            'service_pricing_id': pricing_id.id,
                            'service_pricing_line_id': p_line.id,
                            'amount': p_line.amount,
                            'remarks': p_line.remarks
                        })
                if record.salary_advance_amount > 0:
                    record.service_enquiry_pricing_ids.create({
                        'name': 'Salary Advance',
                        'amount': record.salary_advance_amount,
                        'service_enquiry_id': record.id,
                    })
    
    @api.depends('invoiced_ref.payment_state')
    def _compute_hide_unpaid_reason(self):
        for record in self:
            record.hide_unpaid_reason = record.invoiced_ref.payment_state in ['paid', 'in_payment']

    @api.onchange('invoiced')
    def _onchange_invoiced(self):
        if self.service_request == 'salary_advance' and self.invoiced:
            self.to_be_invoiced = False

    @api.onchange('to_be_invoiced')
    def _onchange_to_be_invoiced(self):
        if self.service_request == 'salary_advance' and self.to_be_invoiced:
            self.invoiced = False

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'salary_advance':
                if record.salary_advance_amount <= 0:
                    raise ValidationError("Kindly Update Salary Advance Amount")
                if not record.nature_of_advance:
                    raise ValidationError("Nature of Advance cannot be empty.")
                if record.invoiced and not record.invoiced_ref:
                    raise ValidationError("Select at least one Invoiced Reference Number")
                if not record.invoiced and not record.to_be_invoiced:
                    raise ValidationError("Either 'Invoiced' or 'To be Invoiced' must be checked.")
                record.dynamic_action_status = f"PM needs to submit for approval"
                record.action_user_id = record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_salary_advance_submit_for_approval(self):
        for record in self:
            if record.service_request == 'salary_advance':
                record.state = 'waiting_op_approval'
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.dynamic_action_status = f"Waiting for approval by OM"
                record.action_user_id = employee.user_id
                record.write({'processed_date': fields.Datetime.now()})
                record.send_email_to_op()

    def action_op_refuse(self):
        current_employee = self.env.user.employee_ids[:1]
        for record in self:
            if record.service_request == 'salary_advance':
                record.state = 'refuse'
                record.write({'processed_date': fields.Datetime.now()})
                record.dynamic_action_status = f"Refused by {current_employee.name if current_employee else 'OH'}"

    def action_gm_refuse(self):
        current_employee = self.env.user.employee_ids[:1]
        for record in self:
            if record.service_request == 'salary_advance':
                record.state = 'refuse'
                record.write({'processed_date': fields.Datetime.now()})
                record.dynamic_action_status = f"Refused by {current_employee.name if current_employee else 'GM'}"

    def action_finance_approved(self):
        res = super().action_finance_approved()
        for record in self:
            if record.service_request == 'salary_advance':
                treasury = self.env['service.request.treasury'].sudo().search([
                    ('service_request_id', '=', record.id)
                ], limit=1)
                if treasury:
                    treasury.write({
                        'nature_of_advance': record.nature_of_advance
                    })
        return res
    
    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'salary_advance' and record.to_be_invoiced:
                invoice_line_ids = []
                for line in record.service_enquiry_pricing_ids:
                    invoice_line_ids.append((0, 0, {
                        'name': line.name,
                        'employee_id': record.employee_id.id,
                        'price_unit': line.amount,
                        'quantity': 1,
                        'service_enquiry_id': record.id
                    }))

                move_vals = {
                    'client_id': record.client_id.id,
                    'client_parent_id': record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id': record.employee_id.id,
                    'move_type': 'service_ticket',
                    'invoice_line_ids': invoice_line_ids,
                }

                if record.nature_of_advance:
                    move_vals['nature_of_advance'] = record.nature_of_advance

                self.env['draft.account.move'].create(move_vals)
        return result


class ServiceEnquiryPricingLine(models.Model):
    _inherit = 'service.enquiry.pricing.line'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        store=True,
        readonly=False,
        related="company_id.currency_id",
        help="The payment's currency."
    )