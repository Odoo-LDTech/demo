# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta
import time


class SkipLoanInstallments(models.Model):
    _name = 'skip.loan.installment'
    _description = 'Skip Loan Installment'
    _rec_name = 'employee_id'


    date = fields.Date(string="Date", default=fields.Date.today(), help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",)
    loan_id = fields.Many2one('hr.loan', string="Select Loan")
    emp_loan_id = fields.Many2many('hr.loan', string="Loan", compute="_compute_emp_loans")
    # skip_loan_ids = fields.One2many('skip.loan.line', 'loan_id', string="Skip Loan Lines")
    skip_loan_line_ids = fields.One2many('skip.loan.line', 'loan_id', string="Skip Loan Lines")
    installment_arrangements = fields.Selection([('increase_installments_months','Increase Installments Months'),
                        ('add_in_existing_installments', 'Add In Existing Installments'),
                        ], string="Installment Arrangements", default='increase_installments_months')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Waiting HR Approval'),
        ('waiting_approval_2', 'Waiting Finance Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    @api.onchange('loan_id')
    def onchange_loan_id(self):
        for rec in self:
            if any(rec.skip_loan_line_ids):
                rec.skip_loan_line_ids.unlink()
            loans = rec.loan_id.loan_lines.ids
            skip_loan = self.env['hr.loan.line'].search([('id', 'in', loans), ('paid', '=', False)])
            data = []
            for record in skip_loan:
                if not record.amount == 0:
                    data.append((0,0,{
                        'date': record.date,
                        'employee_id': record.employee_id,
                        'amount': record.amount,
                        'paid': record.paid,
                        'loan_id': record.loan_id,
                        'payslip_id': record.payslip_id,
                        'skip_installment': record.skip_installment,
                        'loan_lines_id': record.id,
                        }))
            rec.write({'skip_loan_line_ids':data})
    
    @api.depends('employee_id')
    def _compute_emp_loans(self):
        for rec in self:
            loans = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id)])
            rec.emp_loan_id = loans.ids

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


class SkipLoanInstallments(models.Model):
    _name = 'skip.loan.line'
    _description = 'Skip Loan Lines'


    date = fields.Date(string="Payment Date", required=False, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('skip.loan.installment', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
    skip_installment = fields.Boolean(string="Skip Installment")
    done_skiped_installments = fields.Boolean(string="Done Skip Installment")
    loan_lines_id = fields.Many2one('hr.loan.line',string="Loan Line Id")

    def create(self, values):
        result = super(SkipLoanInstallments, self).create(values)
        for res in result:
            if res.skip_installment and res.loan_lines_id:
                if res.loan_id.installment_arrangements == 'increase_installments_months':
                        res.done_skiped_installments = True
                        date_start = None
                        month_count = len(res.loan_lines_id.loan_id.loan_lines.ids)
                        if res.loan_lines_id.loan_id.payment_date:
                            date_start = datetime.strptime(str(res.loan_lines_id.loan_id.payment_date), '%Y-%m-%d')
                            date_start = date_start + relativedelta(months=month_count)
                        data = [(0, 0, {
                            'date': date_start,
                            'amount': res.loan_lines_id.amount,
                            'paid': res.loan_lines_id.paid,
                            'loan_id': res.loan_lines_id.loan_id,
                            'payslip_id': res.loan_lines_id.payslip_id,
                            'skip_installment': False,
                        })]
                        res.loan_lines_id.loan_id.write({'loan_lines': data})
                        if res.done_skiped_installments == True:
                            res.skip_installment = False

                        res.loan_lines_id.amount = 0
                else:
                    res.done_skiped_installments = True
                    count_loan_line = []
                    for lines in res.loan_lines_id.loan_id.loan_lines:
                        if not lines.amount == 0.00:
                            count_loan_line.append(lines.id)
                    no_of_count = len(count_loan_line)
                    loan_lines = res.loan_lines_id.loan_id.loan_lines
                    for loan_line in loan_lines:
                        if not loan_line.amount == 0.00:
                            loan_line.update({'amount': loan_line.amount + (res.amount / no_of_count)})
                    res.skip_installment = False
        return result

    def write(self, values):
        result = super(SkipLoanInstallments, self).write(values)
        for rec in self:
            if values.get('skip_installment') and rec.loan_lines_id:
                if rec.loan_id.installment_arrangements == 'increase_installments_months':
                    rec.done_skiped_installments = True
                    date_start = None
                    month_count = len(rec.loan_lines_id.loan_id.loan_lines.ids)
                    if self.loan_lines_id.loan_id.payment_date:
                        date_start = datetime.strptime(str(rec.loan_lines_id.loan_id.payment_date), '%Y-%m-%d')
                        date_start = date_start + relativedelta(months=month_count)
                    data = [(0,0,{
                        'date': date_start,
                        'amount': self.loan_lines_id.amount,
                        'paid': self.loan_lines_id.paid,
                        'loan_id': self.loan_lines_id.loan_id,
                        'payslip_id': self.loan_lines_id.payslip_id,
                        'skip_installment': False,
                        })]
                    rec.loan_lines_id.loan_id.write({'loan_lines': data})
                    rec.loan_lines_id.amount = 0
                    if rec.done_skiped_installments == True:
                        values.update({'skip_installment': False})
                else:
                    rec.done_skiped_installments = True
                    count_loan_line = []
                    for lines in rec.loan_lines_id.loan_id.loan_lines:
                        if not lines.amount == 0.00:
                            count_loan_line.append(lines.id)
                    no_of_count = len(count_loan_line)
                    loan_lines = rec.loan_lines_id.loan_id.loan_lines
                    for loan_line in loan_lines:
                        if not loan_line.amount == 0.00:
                            loan_line.update({'amount': loan_line.amount + (rec.amount / no_of_count)})
                    rec.skip_installment = False
        return result
