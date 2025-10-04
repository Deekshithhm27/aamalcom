# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AssignEmployeeMedicalWizard(models.TransientModel):
    _name = 'assign.employee.medical.wizard'
    _description = 'Assign Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    department_id = fields.Many2one(
        'hr.department', string="Department", required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        domain="[('department_id', '=', department_id)]",
        required=True
    )

    def action_apply(self):
        """
        Updates the state of the active record to 'submitted_to_gre',
        regardless of whether it's an hr.medical.blood.test or hr.exit.reentry record.
        """
        self.ensure_one()
        
        # Get the active model and ID from the context
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        
        # Browse the record from the active model
        if active_model and active_id:
            record = self.env[active_model].browse(active_id)
            if record:
                # Update the state to 'submitted_to_gre' for both models
                record.write({'state': 'submitted_to_gre'})
                
                # You can also update the employee_id on the record if needed
                # record.write({'employee_id': self.employee_id.id})
                
        return {'type': 'ir.actions.act_window_close'}
