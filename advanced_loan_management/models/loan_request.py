# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Sabeel (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LoanRequest(models.Model):
    """Can create new loan requests and manage records"""
    _name = 'loan.request'
    _inherit = ['mail.thread']
    _description = 'Loan Request'

    name = fields.Char(string='Loan Reference', readonly=True,
                       copy=False, help="Sequence number for loan requests",
                       default=lambda self: self.env['ir.sequence'].next_by_code('loan.request'))
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self:
                                 self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.
                                  currency_id)
    loan_type_id = fields.Many2one('loan.type', string='Loan Type',
                                   required=True, help="Can choose different "
                                                       "loan types suitable")
    loan_amount = fields.Float(string="Loan Amount", store=True,
                               help="Total loan amount", )
    disbursal_amount = fields.Float(string="Disbursal_amount",
                                    help="Total loan amount "
                                         "available to disburse")
    tenure = fields.Integer(string="Tenure",
                            help="Installment period")
    interest_rate = fields.Float(string="Interest rate", help="Interest "
                                                              "percentage")
    date = fields.Date(string="Date", default=fields.Date.today(),
                       readonly=True, help="Date")
    partner_id = fields.Many2one('res.partner', string="Partner",
                                 required=True,
                                 help="Partner")
    repayment_lines_ids = fields.One2many('repayment.line',
                                          'loan_id',
                                          string="Loan Line", index=True,
                                          help="Repayment lines")
    documents_ids = fields.Many2many('loan.documents',
                                     string="Proofs",
                                     help="Documents as proof")
    upload_document_one = fields.Binary(string="Documents")
    upload_document_two = fields.Binary(string="Other Documents")
    upload_document_three = fields.Binary(string="Other Documents")
    upload_document_four = fields.Binary(string="Other Documents")

    img_attachment_ids = fields.Many2many('ir.attachment',
                                          relation="m2m_ir_identity_card_rel",
                                          column1="documents_ids",
                                          string="Images",
                                          help="Image proofs")
    journal_id = fields.Many2one('account.journal',
                                 string="Journal",
                                 help="Journal types",
                                 domain="[('type', '=', 'purchase'),"
                                        "('company_id', '=', company_id)]",
                                 )
    debit_account_id = fields.Many2one('account.account',
                                       string="Debit account",
                                       help="Choose account for "
                                            "disbursement debit")
    credit_account_id = fields.Many2one('account.account',
                                        string="Credit account",
                                        help="Choose account for "
                                             "disbursement credit")
    reject_reason = fields.Text(string="Reason", help="Displays "
                                                      "rejected reason")
    request = fields.Boolean(string="Request", default=False,
                             help="For monitoring the record")
    treasury_request_id = fields.Many2one(
        'hr.service.request.treasury', 
        string='Treasury Request', 
        readonly=True,
        help="Link to the related Treasury Request record."
    )
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('checked', 'Checked'),('confirmed', 'Confirmed'),
                   ('waiting for approval', 'Waiting For Approval'),
                   ('waiting_gm_approval', 'Waiting GM Approval'), ('waiting_fm_approval', 'Waiting FM Approval'),('submit_to_treasury', 'submitted To Treasury'),('disbursed', 'Disbursed'),
                   ('rejected', 'Rejected'), ('closed', 'Closed'),
                   ('approved','Approved')],
        required=True, readonly=True, copy=False,
        tracking=True, default='draft', help="Loan request states")
    total_treasury_requests = fields.Integer(
        string="Treasury Requests",
        compute="_compute_total_treasury_requests"
    )
    is_my_coach = fields.Boolean(
        string="Is My Coach",
        compute='_compute_is_my_coach',
        store=False
    )
    @api.depends('partner_id')
    def _compute_is_my_coach(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.coach_id:
                current_user_employee = self.env.user.partner_id
                rec.is_my_coach = (current_user_employee == rec.partner_id.coach_id)
            else:
                rec.is_my_coach = False
    
    def _compute_total_treasury_requests(self):
        for rec in self:
            rec.total_treasury_requests = self.env['hr.service.request.treasury'].search_count(
                [('service_request_ref', '=', f'hr.exit.reentry,{rec.id}')]
            )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('increment_loan_ref')
        
        res = super(LoanRequest, self).create(vals)
        return res
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        readonly=True,
        tracking=True,
        default=lambda self: self.env.user.employee_id.id
    )
    @api.model
    def create(self, vals):
        if not vals.get('employee_id'):
            employee = self.env.user.employee_id
            if employee:
                vals['employee_id'] = employee.id
        request = super(LoanRequest, self).create(vals)
        return request

        

    @api.onchange('loan_type_id')
    def _onchange_loan_type_id(self):
        """Changing field values based on the chosen loan type"""
        type_id = self.loan_type_id
        self.loan_amount = type_id.loan_amount
        self.disbursal_amount = type_id.disbursal_amount
        self.tenure = type_id.tenure
        self.interest_rate = type_id.interest_rate
        self.documents_ids = type_id.documents_ids

    def action_loan_request(self):
        """Changes the state to confirmed and send confirmation mail"""
        self.write({'state': "confirmed"})
        partner = self.partner_id
        loan_no = self.name
        subject = 'Loan Confirmation'

        message = (f"Dear {partner.name},<br/> This is a confirmation mail "
                   f"for your loan{loan_no}. We have submitted your loan "
                   f"for approval.")

        outgoing_mail = self.company_id.email
        mail_values = {
            'subject': subject,
            'email_from': outgoing_mail,
            'author_id': self.env.user.partner_id.id,
            'email_to': partner.email,
            'body_html': message,
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()

    def action_request_for_loan(self):
        """Change the state to waiting for approval"""
        if self.request:
            self.write({'state': "waiting for approval"})
        else:
            message_id = self.env['message.popup'].create(
                {'message': _("Compute the repayments before requesting")})
            return {
                'name': _('Repayment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.popup',
                'res_id': message_id.id,
                'target': 'new'
            }
    def action_resubmit(self):
        """Change to Approved state"""
        self.write({'state': "draft"})
    
    def action_loan_approved(self):
        """Change to Approved state"""
        self.write({'state': "waiting_gm_approval"})
    
    def action_loan_approved_gm(self):
        """Change to Approved state"""
        self.write({'state': "waiting_fm_approval"})
    
    # The crucial method update
    def action_loan_approved_treasury(self):
        self.ensure_one()
        
        # 1. Find the HR Employee record associated with the Partner
        # We use partner_id to find the related employee, which is required by hr.service.request.treasury
        employee = self.env['hr.employee'].search([
            ('address_home_id', '=', self.partner_id.id)
        ], limit=1)
        
        # Alternative search logic (if partner is linked to user/employee in a different way):
        # employee = self.env['hr.employee'].search([('user_id.partner_id', '=', self.partner_id.id)], limit=1)
        
        
        # 2. Prepare values for the new Treasury document
        treasury_vals = {
            'service_request_ref': f'loan.request,{self.id}', # LINK BACK TO CURRENT LOAN RECORD
            # We use the found employee's ID to populate the treasury record
            'employee_id': employee.id, 
            'total_amount': self.disbursal_amount, # Use disbursal_amount
            'state': 'submitted', 
        }
        
        # 3. Create the treasury document
        treasury_request = self.env['hr.service.request.treasury'].create(treasury_vals)
        
        # 4. Update the state of the current record and link to the new treasury document
        self.write({
            'state': 'submit_to_treasury',
            'treasury_request_id': treasury_request.id, # Link the Treasury record to the Loan
        })
        
        # 5. Return an action to open the newly created treasury document
        return {
            'type': 'ir.actions.act_window',
            'name': _('Treasury Request: %s') % treasury_request.name,
            'res_model': 'hr.service.request.treasury',
            'res_id': treasury_request.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # Helper method to view the created treasury request (if any)
    def action_view_treasury_requests(self):
        self.ensure_one()
        if not self.treasury_request_id:
            raise UserError(_("No Treasury Request linked to this loan."))
            
        return {
            'name': _('Treasury Request'),
            'view_mode': 'form',
            'res_model': 'hr.service.request.treasury',
            'type': 'ir.actions.act_window',
            'res_id': self.treasury_request_id.id,
            'target': 'current',
        }
    def action_disburse_loan(self):
        """Disbursing the loan to customer and creating journal
         entry for the disbursement"""
        self.write({'state': "disbursed"})

        for loan in self:
            amount = loan.disbursal_amount
            loan_name = loan.partner_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            debit_account_id = loan.debit_account_id.id
            credit_account_id = loan.credit_account_id.id
            date_now = loan.date
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': date_now,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,

            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': date_now,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'name': f'DIS / {reference}',
                'narration': reference,
                'ref': reference,
                'journal_id': journal_id,
                'date': date_now,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True

    def action_close_loan(self):
        """Closing the loan"""
        demo = []
        for check in self.repayment_lines_ids:
            if check.state == 'unpaid':
                demo.append(check)
        if len(demo) >= 1:
            message_id = self.env['message.popup'].create(
                {'message': _("Pending Repayments")})
            return {
                'name': _('Repayment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.popup',
                'res_id': message_id.id,
                'target': 'new'
            }
        self.write({'state': "closed"})

    def action_loan_rejected(self):
        """You can add reject reasons here"""
        return {'type': 'ir.actions.act_window',
                'name': 'Loan Rejection',
                'res_model': 'reject.reason',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_loan': self.name}
                }

    def action_compute_repayment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        self.request = True
        for loan in self:
            loan.repayment_lines_ids.unlink()
            date_start = (datetime.strptime(str(loan.date),
                                            '%Y-%m-%d') +
                          relativedelta(months=1))
            amount = loan.loan_amount / loan.tenure
            interest = loan.loan_amount * loan.interest_rate
            interest_amount = interest / loan.tenure
            total_amount = amount + interest_amount
            partner = self.partner_id
            for rand_num in range(1, loan.tenure + 1):
                self.env['repayment.line'].create({
                    'name': f"{loan.name}/{rand_num}",
                    'partner_id': partner.id,
                    'date': date_start,
                    'amount': amount,
                    'interest_amount': interest_amount,
                    'total_amount': total_amount,
                    # 'interest_account_id': self.env.ref('advanced_loan_management.loan_management_inrst_accounts').id,
                    # 'repayment_account_id': self.env.ref('advanced_loan_management.demo_loan_accounts').id,
                    'loan_id': loan.id})
                date_start += relativedelta(months=1)
        return True
