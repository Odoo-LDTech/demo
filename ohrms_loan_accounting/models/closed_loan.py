# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SkipLoanInstallments(models.Model):
    _name = 'closed.loan'
    _description = 'closed Loan'
    _rec_name = 'employee_id'


    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",)
    loan_id = fields.Many2one('hr.loan', string="Select Loan")
    emp_loan_id = fields.Many2many('hr.loan', string="Loan", compute="_compute_emp_loans")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Waiting HR Approval'),
        ('waiting_approval_2', 'Waiting Finance Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
        ('closed', 'Closed'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_approve(self):
        self.write({'state': 'waiting_approval_2'})

    def action_double_approve(self):
        self.write({'state': 'approve'})


    def action_refuse(self):
        self.write({'state': 'refuse'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_closed(self):
        self.write({'state': 'closed'})
        skip_loan = self.env['hr.loan'].search([('id', '=', self.loan_id.id)])
        skip_loan.state = self.state

    @api.depends('employee_id')
    def _compute_emp_loans(self):
        for rec in self:
            loans = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id)])
            rec.emp_loan_id = loans.ids
