from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_view_all_line_attachments(self):
        self.ensure_one()
        attachment_ids = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'account.move.line'),
            ('res_id', 'in', self.line_ids.ids)
        ])

        return {
            'name': 'Journal Line Attachments',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban',
            'domain': [('id', 'in', attachment_ids.ids)],
            'context': {
                'default_res_model': 'account.move.line',
            }
        }
