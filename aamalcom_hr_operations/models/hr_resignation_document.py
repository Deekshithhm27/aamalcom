# -*- coding: utf-8 -*-
from odoo import models, fields

class HrResignationDocument(models.Model):
    _name = 'hr.resignation.document'
    _description = 'Resignation Documents'

    name = fields.Char(string='Document Name')
    file_data = fields.Binary(string='File')
    file_name = fields.Char(string='File Name')
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    resignation_id = fields.Many2one(
        'hr.resignation',
        string='Resignation'
    )
    # The new Many2one field to correctly link to the 'hr.suspending' model
    suspending_id = fields.Many2one(
        'hr.suspending',
        string='Suspension'
    )

    warning_id = fields.Many2one(
        'hr.warning',
        string='Warning ID'
    )
