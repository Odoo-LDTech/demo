from odoo import api, fields, models


class RejectReason(models.TransientModel):
    _name = 'reject.reason'
    # _description = 'Reject.Reason'

    reason_for_reject = fields.Char(string="Reason For Reject")

    def action_confirm(self):
        records = self.env['reject.reason'].browse(self.env.context.get('active_ids'))

    # def action_reject(self):
    #     student_obj = self.env['leave.enchasement'].browse(self._context.get('active_id'))
    #     student_obj.responsible_teacher_id = self.name_id.id
