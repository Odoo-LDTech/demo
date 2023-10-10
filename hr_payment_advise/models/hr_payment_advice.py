# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError



class HrPayrollAdvice(models.Model):
    _name = 'hr.payroll.advice'
    _description = "HR Payroll Advice"

    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    name = fields.Char(readonly=True, required=True,)
    note = fields.Text(string='Description', default='Please make the payroll transfer from above account number to the below mentioned account numbers towards employee salaries:')
    date = fields.Date(readonly=True, required=True,  default=_get_default_date,
        help='Advice Date is used to search Payslips')
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('confirm', 'Confirmed'),
    #     ('cancel', 'Cancelled'),
    # ], string='Status', default='draft', index=True, readonly=True)
    number = fields.Char(string='Reference', readonly=True)
    line_ids = fields.One2many('hr.payroll.advice.line', 'advice_id', string='Employee Salary',
         readonly=True, copy=True)
    chaque_nos = fields.Char(string='Cheque Numbers')
    neft = fields.Boolean(string='NEFT Transaction', help='Check this box if your company use online transfer for salary')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
         default=lambda self: self.env.user.company_id)
    bank_id = fields.Many2one('res.bank', string='Bank', readonly=True,
        help='Select the Bank from which the salary is going to be paid')
    batch_id = fields.Many2one('hr.payslip.run', string='Batch', readonly=True)



    # def confirm_sheet(self):
    #     for advice in self:
    #         if not advice.line_ids:
    #             raise UserError(_('You can not confirm Payment advice without advice lines.'))
    #         date = fields.Date.from_string(fields.Date.today())
    #         advice_year = date.strftime('%m') + '-' + date.strftime('%Y')
    #         number = self.env['ir.sequence'].next_by_code('payment.advice')
    #         advice.write({
    #             'number': 'PAY' + '/' + advice_year + '/' + number,
    #             'state': 'confirm',
    #         })
    #
    #
    # def set_to_draft(self):
    #     self.write({'state': 'draft'})
    #
    # def cancel_sheet(self):
    #     self.write({'state': 'cancel'})

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.bank_id = self.company_id.partner_id.bank_ids and self.company_id.partner_id.bank_ids[0].bank_id.id or False



class HrPayrollAdviceLine(models.Model):
    _name = 'hr.payroll.advice.line'
    _description = 'Bank Advice Lines'

    advice_id = fields.Many2one('hr.payroll.advice', string='Bank Advice')
    name = fields.Char('Bank Account No.', required=True)
    ifsc_bank_code = fields.Char(string='IFSC Code',store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    bysal = fields.Float(string='Amount', digits=dp.get_precision('Payroll'))
    company_id = fields.Many2one('res.company', related='advice_id.company_id', string='Company', store=True, readonly=False)
    ifsc = fields.Boolean(related='advice_id.neft', string='IFSC', readonly=False)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                print("rec.employee_id.bank_account_idrec.employee_id.bank_account_id",rec.employee_id.bank_account_id)
                rec.name = rec.employee_id.bank_account_id
                print("self.employee_id.ifsc_code",rec.employee_id.ifsc_code)
                rec.ifsc_bank_code = rec.employee_id.ifsc_code or ''


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Pay Slips'

    advice_id = fields.Many2one('hr.payroll.advice', string='Bank Advice', copy=False)

