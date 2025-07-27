from odoo import models, fields, api,_
from datetime import date, timedelta
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_change_request_count = fields.Integer(
        string='Change Requests',
        compute='_compute_employee_change_request_count')

    def _compute_employee_change_request_count(self):
        change_request_model = self.env['hr.employee.change.request']
        for employee in self:
            count = change_request_model.search_count([('employee_id', '=', employee.id)])
            employee.employee_change_request_count = count


    # def _cron_notify_probation_end(self):
    #     today = date.today()
    #     notify_date = today + timedelta(days=7)

    #     employees = self.search([
    #         ('probation_end_date', '=', notify_date),
    #         ('parent_id', '!=', False),('custom_employee_type','=','internal')
    #     ])

    #     print("---employees",employees)

    #     template = self.env.ref('aamalcom_hr_operations.mail_template_probation_end_notify', raise_if_not_found=False)
    #     if not template:
    #         return

    #     for employee in employees:
    #         template.sudo().send_mail(employee.id, force_send=True)
    #     
    @api.model
    def cron_check_probation_ending(self):
        today = fields.Date.context_today(self)
        limit_date = fields.Date.to_string(fields.Date.from_string(today) + timedelta(days=15))

        employees = self.search([
            ('probation_end_date', '!=', False),
            ('probation_end_date', '<=', limit_date),
            ('probation_end_date', '>=', today),
        ])

        if not employees:
            return

        mail_template = self.env.ref('aamalcom_hr_operations.email_template_probation_warning', False)
        hr_group = self.env.ref('visa_process.group_service_request_hr_manager', raise_if_not_found=False)
        hr_managers = hr_group.users if hr_group else self.env['res.users']

        activity_type = self.env.ref('aamalcom_hr_operations.mail_activity_type_probation_manager_notify', False)

        for employee in employees:
            has_open_request = self.env['hr.probation.extend.request'].search_count([
                ('employee_id', '=', employee.id),
                ('state', 'not in', ['done', 'cancelled']),
            ])
            domain_activities = [
                ('res_model', '=', 'hr.employee'),
                ('res_id', '=', employee.id),
                ('activity_type_id', '=', activity_type.id if activity_type else False),
            ]
            if employee.parent_id and employee.parent_id.user_id:
                domain_activities.append(('user_id', '=', employee.parent_id.user_id.id))
            else:
                continue  # skip if no manager user

            # Remove all old activities to avoid duplicates
            self.env['mail.activity'].search(domain_activities).unlink()

            if has_open_request:
                continue

            manager_user = employee.parent_id.user_id
            if not manager_user:
                continue

            vals_mail = {
                'email_to': manager_user.partner_id.email,
                'email_cc': ",".join(u.partner_id.email for u in hr_managers if u.partner_id.email),
                'email_from': self.env.user.company_id.email or self.env.user.email,
                'auto_delete': True,
            }

            if mail_template:
                mail_template.send_mail(employee.id, email_values=vals_mail, force_send=True)
            # else:
            #     mail_values = {
            #         'subject': _('Probation period ending soon for %s') % employee.name,
            #         'body_html': _(
            #             "<p>Dear %s,</p>"
            #             "<p>The probation period of your team member <strong>%s</strong> is ending on <strong>%s</strong>.</p>"
            #             "<p>Please create a probation extension request if required.</p>"
            #             "<p>Regards,<br/>HR System</p>"
            #         ) % (employee.parent_id.name, employee.name, employee.probation_end_date),
            #         'email_to': manager_user.partner_id.email,
            #         'email_cc': ",".join(u.partner_id.email for u in hr_managers if u.partner_id.email),
            #     }
            #     self.env['mail.mail'].create(mail_values).send()

            if activity_type:
                self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('hr.employee').id,
                    'res_id': employee.id,
                    'user_id': manager_user.id,
                    'activity_type_id': activity_type.id,
                    'summary': _('Probation ending soon for employee %s') % employee.name,
                    'note': _('Please review probation period for employee %s and create extension request if needed.') % employee.name,
                    'date_deadline': fields.Date.today() + timedelta(days=15),
                })