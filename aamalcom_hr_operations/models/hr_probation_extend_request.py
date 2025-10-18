# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import base64

class ProbationExtendRequest(models.Model):
    _name = 'hr.probation.extend.request'
    _description = 'Probation Extend Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(
        string='Request Reference', required=True, copy=False, readonly=True, default='New'
    )
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, index=True, tracking=True,domain="[('parent_id.user_id','=',uid),('custom_employee_type','=','internal')]"
    )
    manager_id = fields.Many2one(
        'hr.employee', string='Employee Manager', related='employee_id.parent_id', store=True, readonly=True
    )
    request_date = fields.Date(
        string='Request Date', required=True, default=fields.Date.context_today, readonly=True
    )
    current_probation_term = fields.Char(
        string='Current Probation Term', related='employee_id.probation_term', readonly=True
    )
    current_probation_end_date = fields.Date(
        string='Current Probation End Date', related='employee_id.probation_end_date', readonly=True
    )
    extend_term = fields.Char(
        string='Extend Probation Term',
        required=True,
        help="Duration to extend e.g. 30 days, 1 month",
    )
    hr_recommendation = fields.Selection(
        [('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
        string='HR Recommendation',
        default='pending',
        tracking=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('hr_review', 'HR Review'),
            ('employee_confirm', 'Waiting Employee Confirmation'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    hr_manager_id = fields.Many2one('res.users', string="HR Manager",required=True)
    employee_acceptance = fields.Selection(
        [('pending', 'Pending'), ('accept', 'Accepted'), ('reject', 'Rejected')],
        string='Employee Acceptance',
        default='pending',
        tracking=True,
    )
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)
    letter_pdf = fields.Binary("Extension Letter", readonly=True)
    letter_filename = fields.Char("PDF Filename")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.probation.extend.request') or 'New'
        res = super().create(vals)

        # # assign HR manager user automatically - pick first HR manager user from group
        # hr_group = self.env.ref('visa_process.group_service_request_hr_manager', raise_if_not_found=False)
        # if hr_group and hr_group.users:
        #     res.hr_manager_id = hr_group.users[0]

        return res

    def action_submit_request(self):
        self.ensure_one()
        if self.env.user not in (self.manager_id.user_id,) and not self.env.user.has_group('aamalcom_hr_operations.group_hr_employee_internal'):
            raise UserError(_("Only the employee's manager or HR internal employee can submit the request."))
        if self.state != 'draft':
            raise UserError(_("You can only submit requests in Draft state."))

        self.state = 'submitted'
        self.message_post(body=_("Probation extension request submitted by %s.") % self.env.user.name)
        self._add_hr_review_activity()

    def _add_hr_review_activity(self):
        self.ensure_one()
        hr_group = self.env.ref('visa_process.group_service_request_hr_manager', raise_if_not_found=False)
        if not hr_group:
            return
        for hr_manager in hr_group.users:
            self.activity_schedule(
                'aamalcom_hr_operations.mail_activity_type_probation_hr_review',
                user_id=hr_manager.id,
                note=_("Please review the probation extension request for employee %s.") % self.employee_id.name,
                date_deadline=fields.Date.today() + timedelta(days=10),
            )

    def action_hr_review(self):
        self.ensure_one()
        if not self.env.user.has_group('visa_process.group_service_request_hr_manager'):
            raise UserError(_('Only HR Manager can review the request'))
        if self.state != 'submitted':
            raise UserError(_('Request can only be reviewed if in Submitted state.'))
        if self.hr_recommendation not in ['approve', 'reject']:
            raise UserError(_("Please select HR Recommendation (Approve or Reject) before continuing."))

        if self.hr_recommendation == 'approve':
            self.state = 'employee_confirm'
            self._generate_probation_extend_letter()
            self.message_post(body=_("Probation extension request approved by HR. Letter generated and sent to employee for confirmation."))
            self._send_letter_to_employee()
            self.activity_unlink(['aamalcom_hr_operations.mail_activity_type_probation_hr_review'])
        else:
            self.state = 'cancelled'
            self.message_post(body=_("Probation extension request rejected by HR."))
            self.activity_unlink(['aamalcom_hr_operations.mail_activity_type_probation_hr_review'])

    def action_employee_confirm(self, acceptance=None):
        self.ensure_one()
        if self.state != 'employee_confirm':
            raise UserError(_('The request is not waiting for employee confirmation.'))

        if not acceptance:
            acceptance = self._context.get('acceptance')
        if acceptance not in ['accept', 'reject']:
            raise UserError(_('Invalid acceptance value. Provide "accept" or "reject".'))

        self.employee_acceptance = acceptance
        if acceptance == 'accept':
            self.state = 'done'
            self.message_post(body=_("Employee has accepted the probation extension."))
            self._update_employee_probation_and_contract()
            self.message_post(body=_("Probation term and contract updated. HR to close the request."))
            self.activity_unlink([
                'aamalcom_hr_extension.mail_activity_type_probation_hr_review',
            ])
        else:
            self.state = 'cancelled'
            self.message_post(body=_("Employee has rejected the probation extension."))
            self.activity_unlink([
                'aamalcom_hr_extension.mail_activity_type_probation_hr_review',
            ])

    def action_hr_close(self):
        self.ensure_one()
        if not self.env.user.has_group('visa_process.group_service_request_hr_manager'):
            raise UserError(_('Only HR Manager can close the request.'))
        if self.state != 'done':
            raise UserError(_('Cannot close request not in Done state.'))

        self.state = 'done'
        self.message_post(body=_("Probation extension request closed by HR."))
        self.activity_unlink([
                'aamalcom_hr_extension.mail_activity_type_probation_hr_review',
            ])

    def _generate_probation_extend_letter(self):
        """Generate probation extension letter as PDF and store it as binary."""
        self.ensure_one()
        pdf_content, _ = self.env.ref('aamalcom_hr_operations.action_report_probation_extension_letter')._render_qweb_pdf(self.id)

        filename = f'Probation_Extension_Letter_{self.employee_id.name.replace(" ", "_")}.pdf'
        self.letter_pdf = base64.b64encode(pdf_content)
        self.letter_filename = filename

    def _send_letter_to_employee(self):
        self.ensure_one()

        # Get the email template
        template = self.env.ref('aamalcom_hr_operations.email_template_probation_extension_letter', raise_if_not_found=False)
        if not template or not self.letter_pdf:
            return

        # Create a single attachment (remove duplicates if any)
        attachment_name = self.letter_filename or 'Probation_Extension_Letter.pdf'
        attachment = self.env['ir.attachment'].create({
            'name': attachment_name,
            'type': 'binary',
            'datas': self.letter_pdf,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        # Prepare email with correct attachment format
        email_values = {
            'attachments': [(attachment.name, base64.b64decode(attachment.datas))],
        }

        # Send the email
        template.send_mail(self.id, force_send=True, email_values=email_values)


    def _update_employee_probation_and_contract(self):
        self.ensure_one()
        emp = self.employee_id.sudo()  # elevate access for employee

        def parse_extend_term(term):
            term = term.strip().lower()
            days = 0
            try:
                if 'month' in term:
                    num = int(term.split()[0])
                    days = 30 * num
                elif 'day' in term:
                    num = int(term.split()[0])
                    days = num
                else:
                    days = int(term)
            except Exception:
                days = 0
            return days

        extension_days = parse_extend_term(self.extend_term)
        if extension_days <= 0:
            raise UserError(_('Invalid probation extend term to update.'))

        doj = emp.doj or fields.Date.today()
        old_prob_end_dt = fields.Date.from_string(emp.probation_end_date) if emp.probation_end_date else fields.Date.from_string(doj)

        if not old_prob_end_dt:
            raise UserError(_("Cannot calculate extension. Both probation end date and Date of Joining are missing."))

        new_prob_end_date = old_prob_end_dt + timedelta(days=extension_days)
        new_total_days = (new_prob_end_date - fields.Date.from_string(doj)).days

        # ✅ sudo write on employee
        emp.sudo().write({
            'probation_term': str(new_total_days),
            'probation_end_date': new_prob_end_date,
        })

        if emp.contract_ids:
            contract = emp.contract_ids[0].sudo()  # elevate access for posting
            msg = _(
                "Probation period extended by %s days, new probation end date: %s."
                % (extension_days, new_prob_end_date)
            )
            contract.message_post(body=msg)
            self.contract_id = contract.id

        self.message_post(body=_("Employee probation term updated to %s days (new end date: %s).") % (new_total_days, new_prob_end_date))

    def action_cancel(self):
        for line in self:
            line.state = 'cancelled'