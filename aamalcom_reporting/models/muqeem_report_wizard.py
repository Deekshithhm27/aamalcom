# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging # Import logging
_logger = logging.getLogger(__name__) # Initialize logger

from odoo.tools.misc import format_date
import base64


class ResUsers(models.Model):
    _inherit = "res.users"

    user_type = fields.Selection([('external','External'),('internal','Internal')],string="Type of user to set System Access",required=True)
    internal_company_id = fields.Many2one('res.company',string="Company")
    partner_company_id = fields.Many2one('res.partner',string="Company",domain="[('is_company','=',True)]")

    company_spoc_id = fields.Many2one('hr.employee',string="Project Manager",domain="[('custom_employee_type','=','internal')]")


    def action_create_employee(self):
        self.ensure_one()
        self.env['hr.employee'].create(dict(
            name=self.name,
            company_id=self.env.company.id,
            **self.env['hr.employee']._sync_user(self)
        ))

    @api.onchange('internal_company_id')
    def update_user_company_id(self):
        # this method is used to update the parent_id of internal user
        # parent_company_id is the value which is being fetched in res.partner which depends on user_ids
        # so in this method, we are directly updating the internal user's company to parent_company_id
        for line in self:
            line.partner_company_id = line.internal_company_id.partner_id.id

    @api.onchange('user_type')
    def reset_company_id(self):
        for line in self:
            if line.user_type == 'external':
                line.internal_company_id = False


# models/muqeem_report_wizard.py
class MuqeemReportWizard(models.TransientModel):
    _name = 'muqeem.report.wizard'
    _description = 'Muqeem Report Wizard'

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    service_request = fields.Selection([
        ('hr_card','Issuance for HR card'),
        ('muqeem_dropout', 'Muqeem Dropout'),
        ('iqama_renewal','Iqama Renewal')
    ], string="Service Requests", required=True)

    # New fields
    share_report = fields.Boolean(string="Share the report", default=False)
    # Assuming hr.employee is the internal employee model
    internal_employee_ids = fields.Many2many(
        'hr.employee',
        string="Internal Employees",
        domain=[('user_id', '!=', False)], # Only employees linked to a user can receive emails
        help="Select internal employees who should receive this report via email."
    )

    @api.onchange('share_report')
    def _onchange_share_report(self):
        # Clear selected employees if sharing is unchecked
        if not self.share_report:
            self.internal_employee_ids = [(5, 0, 0)] # Clears all Many2many records

    def print_muqeem_report(self):
        """
        Action to print the Muqeem report, and optionally share it via email.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request': self.service_request,
            'share_report': self.share_report,
        }

        # Generate the report PDF
        report_action = self.env.ref('aamalcom_reporting.action_muqeem_report_pdf')
        pdf_content, _ = report_action._render_qweb_pdf(self, data=data)

        if self.share_report and self.internal_employee_ids:
            # Prepare email values
            template = self.env.ref('aamalcom_reporting.email_template_muqeem_report_share', raise_if_not_found=False)
            if not template:
                raise ValidationError(_("Email template 'aamalcom_reporting.email_template_muqeem_report_share' not found. Please ensure it's loaded."))

            # Create an attachment from the generated PDF
            attachment_name = f"Service_Request_Report_{self.service_request}_{self.from_date}_{self.to_date}.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': attachment_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })

            # Get the service_request_label for the email template
            # This is crucial for fixing the AttributeError
            service_request = dict(self._fields['service_request'].selection).get(self.service_request, self.service_request)

            # Send email using the template's send_mail method
            for employee in self.internal_employee_ids:
                if employee.work_email:
                    template_context = {
                        'employee_name': employee.name,
                        'recipient': employee,
                        # Add service_request_label to the context for the email template
                        'service_request': service_request,
                        # Also add formatted dates if you want to use them directly in subject/body
                        'from_date_formatted': format_date(self.env, self.from_date),
                        'to_date_formatted': format_date(self.env, self.to_date),
                    }

                    template.with_context(lang=self.env.user.lang, **template_context).send_mail(
                        self.id, # The record ID for the template context (i.e., the wizard record)
                        email_values={
                            'email_to': employee.work_email,
                            'attachment_ids': [(6, 0, [attachment.id])],
                        },
                        force_send=True # Set to True to send immediately
                    )
                    _logger.info(f"Report shared with {employee.name} at {employee.work_email}")
                else:
                    _logger.warning(f"Employee {employee.name} has no work email configured. Skipping email for this employee.")

            # attachment.unlink() # Uncomment this line if you want to delete the attachment after mailing

        # Return the report action for display
        return report_action.report_action(self, data=data)