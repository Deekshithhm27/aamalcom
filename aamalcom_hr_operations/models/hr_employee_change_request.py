from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError

class HrEmployeeChangeRequest(models.Model):
    _name = 'hr.employee.change.request'
    _description = 'Employee Information Change Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Request Reference', copy=False, readonly=True, index=True, default='New')
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env.user.employee_ids[:1])
    # Use marital selection from hr.employee
    change_type = fields.Selection([
        ('marital', 'Marital Status'),
        ('mobile', 'Mobile Number'),
        ('email', 'Email Address'),
    ], string='Change Type', required=True)
    # For marital, restrict to standard possible values
    current_value = fields.Char(string="Current Value", readonly=True,store=True)
    new_value = fields.Char('New Value', required=True)
    reason = fields.Text('Reason for Change')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=True, copy=False, tracking=True)

    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approval_date = fields.Datetime('Approval Date', readonly=True)

    reject_reason = fields.Text('Reason for Rejection', readonly=True, copy=False)

    is_hr_manager = fields.Boolean(compute="_compute_is_hr_manager")
    # below is to check that current active user
    current_user_id = fields.Integer(compute="_compute_current_user_id", store=False)

    @api.onchange('change_type', 'employee_id')
    def _onchange_change_type(self):
        """Auto-fetch current value from employee based on selected field."""
        for rec in self:
            rec.current_value = ''
            employee = rec.employee_id
            if not employee or not rec.change_type:
                continue
            if rec.change_type == 'marital':
                marital_labels = dict(employee._fields['marital'].selection)
                rec.current_value = marital_labels.get(employee.marital, '') or ''
            elif rec.change_type == 'mobile':
                rec.current_value = employee.mobile_phone or ''
            elif rec.change_type == 'email':
                rec.current_value = employee.work_email or ''

    def _compute_is_hr_manager(self):
        for rec in self:
            rec.is_hr_manager = self.env.user.has_group('visa_process.group_service_request_hr_manager')

    def _compute_current_user_id(self):
        for rec in self:
            rec.current_user_id = self.env.user.id

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.change.request') or 'New'
        rec = super().create(vals)
        return rec

    def action_submit(self):
        for rec in self:
            if rec.change_type == 'marital':
                marital_options = dict(self.employee_id._fields['marital'].selection)
                if rec.new_value not in marital_options:
                    raise UserError(_('Invalid marital status value. Allowed: %s') % ', '.join(marital_options.keys()))
            if rec.state != 'draft':
                raise UserError(_("Only draft requests can be submitted."))
            if rec.requested_by != self.env.user:
                raise UserError(_("Only the request creator can submit this request."))
            rec.state = 'pending'
            rec.activity_schedule_notify_hr_manager()
            rec._notify_hr_manager_new_request()

    def action_approve(self):
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending requests can be approved.'))

        employee = self.employee_id
        print("---------chaneg time",self.change_type)
        if self.change_type == 'marital':
            employee.marital = self.new_value
        elif self.change_type == 'mobile':
            employee.mobile_phone = self.new_value
        elif self.change_type == 'email':
            employee.work_email = self.new_value
        else:
            raise UserError(_('Unsupported change type.'))

        self.state = 'approved'
        self.approved_by = self.env.user
        self.approval_date = fields.Datetime.now()
        self.activity_update_for_employee()
        self._notify_employee_status_update()

    def action_reject(self):
        for rec in self:
            if rec.state != 'pending':
                raise UserError(_("Only pending requests can be rejected."))
        return {
            'name': 'Reject Change Request',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.change.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids},
        }

    def _notify_hr_manager_new_request(self):
        template = self.env.ref('aamalcom_hr_operations.email_template_hr_employee_change_request_new', raise_if_not_found=False)
        if template:
            for rec in self:
                template.send_mail(rec.id, force_send=True)

    def _notify_employee_status_update(self):
        template = self.env.ref('aamalcom_hr_operations.email_template_hr_employee_change_request_status', raise_if_not_found=False)
        if template:
            for rec in self:
                template.send_mail(rec.id, force_send=True)

    def activity_schedule_notify_hr_manager(self):
        """Schedule activity for HR managers when request submitted"""
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        template = self.env.ref('aamalcom_hr_operations.email_template_hr_employee_change_request_new', raise_if_not_found=False)

        hr_manager_group = self.env.ref('visa_process.group_service_request_hr_manager')
        hr_manager_users = hr_manager_group.users.filtered(lambda u: u.has_group('visa_process.group_service_request_hr_manager'))

        for rec in self:
            for user in hr_manager_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,
                    'res_model_id': self.env.ref('aamalcom_hr_operations.model_hr_employee_change_request').id,
                    'activity_type_id': activity_type.id,
                    'user_id': user.id,
                    'summary': _('New Employee Change Request submitted'),
                    'note': _('Please review the request %s') % rec.name,
                    'date_deadline': fields.Date.today(),
                })

    def activity_update_for_employee(self):
        """Remove existing activities and assign notification to employee"""
        activity_type = self.env.ref('mail.mail_activity_data_todo')

        for rec in self:
            to_unlink = self.env['mail.activity'].search([('res_model', '=', 'hr.employee.change.request'), ('res_id', '=', rec.id)])
            to_unlink.unlink()

            # Assign activity to employee user (assuming employee has user_id field)
            if rec.employee_id.user_id:
                self.env['mail.activity'].create({
                    'res_id': rec.id,
                    'res_model_id': self.env.ref('aamalcom_hr_operations.model_hr_employee_change_request').id,
                    'activity_type_id': activity_type.id,
                    'user_id': rec.employee_id.user_id.id,
                    'summary': _('Your Change Request %s is %s') % (rec.name, rec.state.capitalize()),
                    'note': _('Your change request has been %s by HR.') % rec.state,
                    'date_deadline': fields.Date.today(),
                })