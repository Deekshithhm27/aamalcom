from odoo import models, _
from odoo.exceptions import AccessError
from collections import defaultdict

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def check(self, mode, values=None):
        """ Override attachment access check to allow employees to upload/view their own docs """
        if self.env.is_superuser():
            return True

        # Still enforce that user is an internal user
        if not (self.env.is_admin() or self.env.user.has_group('base.group_user') or self.env.user.has_group('visa_process.group_service_request_manager')):
            raise AccessError(_("Sorry, you are not allowed to access this documessnt."))

        model_ids = defaultdict(set)
        if self:
            self.env['ir.attachment'].flush(['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
            self._cr.execute(
                'SELECT res_model, res_id, create_uid, public, res_field '
                'FROM ir_attachment WHERE id IN %s',
                [tuple(self.ids)]
            )
            for res_model, res_id, create_uid, public, res_field in self._cr.fetchall():
                if public and mode == 'read':
                    continue

                # 🔽 Relax this rule: allow creating attachments on own employee record
                if res_model == 'hr.employee' and res_id == self.env.user.employee_id.id:
                    continue

                if not self.env.is_system() and (res_field or (not res_id and create_uid != self.env.uid)):
                    raise AccessError(_("Sorry, you are not allowed to access this document."))

                if not (res_model and res_id):
                    continue

                model_ids[res_model].add(res_id)

        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        for res_model, res_ids in model_ids.items():
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                continue

            records = self.env[res_model].browse(res_ids).exists()
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            # Keep checks for other models
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)

        return True
