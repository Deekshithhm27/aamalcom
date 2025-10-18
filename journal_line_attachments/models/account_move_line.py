from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'account_move_line_attachment_rel',
        'move_line_id',
        'attachment_id',
        string="Attachments"
    )
