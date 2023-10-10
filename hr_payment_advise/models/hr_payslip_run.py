# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    available_advice = fields.Boolean(string='Made Payment Advice?',
                                       help='If this box is checked which means that Payment Advice exists for current batch',
                                       readonly=False, copy=False)


    def draft_payslip_run(self):
        super(HrPayslipRun, self).draft_payslip_run()
        self.write({'available_advice': False})


    def create_advice(self):
        for run in self:
            if run.available_advice:
                raise UserError(_("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") % (run.name,))
            company = self.env.user.company_id
            advice = self.env['hr.payroll.advice'].create({
                        'batch_id': run.id,
                        'company_id': company.id,
                        'name': run.name,
                        'date': run.date_end,
                        'bank_id': company.partner_id.bank_ids and company.partner_id.bank_ids[0].bank_id.id or False
                    })
            for slip in run.slip_ids:
                slip.action_payslip_done()
                if not slip.employee_id.bank_account_id :
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.employee_id.bank_account_id,
                        'ifsc_bank_code': slip.employee_id.ifsc_code or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
        self.write({'available_advice': True})