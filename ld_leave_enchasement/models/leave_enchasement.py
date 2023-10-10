from odoo import models, fields, api, _


class LeaveEnchasement(models.Model):
    _name = "leave.enchasement"

    employee_name = fields.Many2one('hr.employee', string="Employee Name")
    department = fields.Char(string="Department")
    leave = fields.Integer(string='Leave')
    amount = fields.Integer(string='Amount')
    total = fields.Integer(string='Total')
    # reason_for_reject = fields.Char(string="Reason For Reject")

    status = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'),
                               ('reject', 'reject')], string='Status', default='draft')

    def action_approved(self):
        self.write({
            'status': 'approve',
        })

    def action_rejected(self):
        self.write({
            'status': 'reject',
        })

    def action_draft(self):
        self.write({
            'status': 'draft',
        })

    def reject_reason_wizard(self):
        return {
            'name': _('Reject Reason Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'reject.reason',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('ld_leave_enchasement.reject_reason_wizard_view_form').id,
            'target': 'new'
        }


class HrEmp(models.Model):
    _inherit = 'hr.employee'
