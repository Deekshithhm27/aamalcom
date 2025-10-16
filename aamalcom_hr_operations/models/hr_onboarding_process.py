from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _


class HrOnboardingProcess(models.Model):
    _name = 'hr.onboarding.process'
    _description = 'Onboarding Process'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Request ID',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.onboarding.process')
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    
    date_of_joining = fields.Date(
        string='Date of Joining',
        compute="_compute_employee_details",
        store=True,
        readonly=False  
    )

    checklist_line_ids = fields.One2many(
        'hr.onboarding.process.line',
        'process_id',
        string='Onboarding Checklist Lines',
    )

    status = fields.Selection(
        [('draft', 'Draft'),('issued', 'Issued'),
         ('not_issued', 'Not issued'),('pending', 'Pending'),],
        string="Status",
        default='draft'
    )
    
    
    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.doj:
                rec.date_of_joining = rec.employee_id.doj
            elif not rec.employee_id:
                rec.date_of_joining = False

    

    # --- THE NEW FIX: Generate lines when employee is selected ---
    @api.onchange('employee_id')
    def _onchange_employee_id_generate_checklist(self):
        if self.employee_id:
            # Clear existing lines first, only if the record is not yet saved (self.id is False)
            # or if we explicitly want to reset them on employee change.
            if not self.id or not self.checklist_line_ids:
                # Command (5) to clear all existing lines before adding new ones
                self.checklist_line_ids = [(5, 0, 0)]
            
            # If lines already exist, we should probably *not* regenerate them, 
            # unless the intent is to wipe and restart the checklist on every employee change.
            # Assuming you only want to generate them if they don't exist yet on a new record.
            
            if not self.checklist_line_ids:
                checklist_items = self.env['hr.onboarding.checklist'].search([], order='sequence,id')
                
                lines = []
                for item in checklist_items:
                    # Command (0, 0, values) to create new lines
                    lines.append((0, 0, {
                        'onboarding_checklist_id': item.id,
                        'status': 'not_issued',
                    }))
                
                self.checklist_line_ids = lines
        
    def action_submit(self):
        for record in self:
            if not record.employee_id:
                raise ValidationError(_("You must select an Employee before submit."))
            record.status = 'not_issued'


    def action_issued(self):
        for record in self:
            not_issued_lines = record.checklist_line_ids.filtered(lambda l: l.status != 'issued')
            if not_issued_lines:
                pending_items = ", ".join(not_issued_lines.mapped('onboarding_checklist_id.name'))
                raise ValidationError(
                    f"All checklist items must be marked as Issued before completing the onboarding process. "
                    f"Pending items: {pending_items}"
                )
            record.status = 'issued'


class HrOnboardingProcessLine(models.Model):
    _name = 'hr.onboarding.process.line'
    _description = 'Onboarding Process Line'

    process_id = fields.Many2one(
        'hr.onboarding.process',
        string='Onboarding Process',
        ondelete='cascade',
    )
    onboarding_checklist_id = fields.Many2one(
        'hr.onboarding.checklist',
        string='Checklist Item', 
        ondelete='restrict', 
    )
    comments = fields.Text(
        string='Comments',
    )
    status = fields.Selection(
        [('issued', 'Issued'),
         ('not_issued', 'NA'),
         ('pending', 'Pending')],
        string="Status",
        default='not_issued'
    )
    
    name = fields.Char(
        string='Item Name',
        related='onboarding_checklist_id.name',
        store=True,
    )

    def action_issue_item(self):
        self.ensure_one()
        self.write({'status': 'issued'})

    def action_remove_item(self):
        self.ensure_one()
        self.unlink()