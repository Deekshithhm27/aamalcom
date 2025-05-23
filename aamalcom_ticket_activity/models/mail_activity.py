from odoo import models, exceptions, api

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def write(self, values):
        # Prevent editing if the user is not the owner
        for record in self:
            if record.user_id != self.env.user:
                raise exceptions.AccessError(
                    f"Allowed to modify this activity only by {record.user_id.name}."
                )
        return super().write(values)

    def action_feedback(self, feedback=False, attachment_ids=None):
        # From oe_chatter prevent marking as done if the user is not the owner
        for record in self:
            if record.user_id != self.env.user:
                raise exceptions.AccessError(
                    f"Only {record.user_id.name} is allowed to mark this activity as done."
                )
        return super(MailActivity, self).action_feedback(feedback=feedback, attachment_ids=attachment_ids)

    def action_done(self):
        # Prevent marking as done if the user is not the owner
        for record in self:
            if record.user_id != self.env.user:
                raise exceptions.AccessError(
                    f"Only {record.user_id.name} is allowed to mark this activity as done."
                )
        return super(MailActivity, self).action_done()

    def action_done_schedule_next(self):
        # Prevent marking as done if the user is not the owner
        for record in self:
            if record.user_id != self.env.user:
                raise exceptions.AccessError(
                    f"Only {record.user_id.name} is allowed."
                )
        return super(MailActivity, self).action_done_schedule_next()


