# -*- coding:utf-8 -*-

from calendar import monthrange
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo import api, fields, models, tools, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # this method has no use now
    # def increase_amount_if_decimal(self,amount):
    #     fractional_part = amount - int(amount)
    #     if fractional_part >= 0.01:
    #         amount += 1
    #     return int(amount)

    @api.model
    def get_contract(self, employee, date_from, date_to):
        clause_1 = ['&', ('date_end', '>=', date_to), ('date_end', '<=', date_from)]
        clause_2 = ['&', ('date_start', '>=', date_to), ('date_start', '>=', date_from)]
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        if self.contract_id:
            self.contract_id = False
        return self.env['hr.contract'].search(clause_final).ids

    def get_last_date_of_month(self,year, month):
        next_month = datetime(year, month, 1) + relativedelta(months=1)
        last_date_of_month = next_month - relativedelta(days=1)
        return last_date_of_month.day

    def round_all_pf_esi(self, amount):
        fractional_part = amount - int(amount)
        if fractional_part == 0.00:
            return amount
        if not fractional_part == 0.01:
            amount += 1
            return int(amount)

    def round_all(self, amount):
        fractional_part = amount - int(amount)
        if fractional_part == 0.00 or fractional_part <= -0.00:
            return amount
        if fractional_part >= 0.01 and fractional_part <=0.49:
            return int(amount)
        if fractional_part >= 0.50:
            amount += 1
            return int(amount)

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            var1 = payslip.get_last_date_of_month(payslip.date_to.year,payslip.date_to.month)
            first_date_of_month = payslip.date_from.replace(day=1).day
            if payslip.date_to.day == var1 and payslip.date_from.day == first_date_of_month:
                absent_line_id = payslip.worked_days_line_ids.filtered(lambda s: s.code == 'MISSATTE ')
                total_earning = 0.0
                total_deduction = 0.0
                net_salary = 0.0
                if absent_line_id:
                    var = absent_line_id.number_of_days
                    working_days = monthrange(payslip.date_from.year, payslip.date_from.month)[-1]
                    payble_days = working_days - var
                    voluntary_pf = payslip.line_ids.filtered (lambda s : s.code == 'VPF')
                    per_day_sal_vpf = voluntary_pf.total / working_days
                    vpf_deduction = absent_line_id.number_of_days * per_day_sal_vpf
                    vpf_earning = payslip.round_all(voluntary_pf.total - vpf_deduction)
                    voluntary_pf.write({'total': vpf_earning})
                    net_salary = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    basic = payslip.line_ids.filtered(lambda s: s.code == 'BASIC')
                    per_day_sal_basic = basic.total / working_days
                    basic_deduction = absent_line_id.number_of_days * per_day_sal_basic
                    basic_earning = payslip.round_all(basic.total - basic_deduction)
                    total_earning += basic_earning
                    basic_line = payslip.line_ids.filtered(lambda s: s.code == 'BASIC')
                    basic_line.write({'total': basic_earning})
                    hra = payslip.line_ids.filtered(lambda s: s.code == 'HRA')
                    per_day_sal_hra = hra.total / working_days
                    hra_deduction = absent_line_id.number_of_days * per_day_sal_hra
                    hra_earning = payslip.round_all(hra.total - hra_deduction)
                    total_earning += hra_earning
                    # hra_line = payslip.line_ids.filtered(lambda s: s.code == 'HRA')
                    hra.write({'total': hra_earning})
                    convence = payslip.line_ids.filtered(lambda s: s.code == 'C')
                    per_day_sal_convence = convence.total / working_days
                    convence_deduction = absent_line_id.number_of_days * per_day_sal_convence
                    convence_earning = payslip.round_all(convence.total - convence_deduction)
                    total_earning += convence_earning
                    convence_line = payslip.line_ids.filtered(lambda s: s.code == 'C')
                    convence_line.write({'total': convence_earning})
                    special_allowance_convence = payslip.line_ids.filtered(lambda s: s.code == 'SA')
                    per_day_sal_special_allowance_convendce = special_allowance_convence.total / working_days
                    special_allowance_convence_deduction = absent_line_id.number_of_days * per_day_sal_special_allowance_convendce
                    sa_convence_earning = payslip.round_all(special_allowance_convence.total - special_allowance_convence_deduction)
                    total_earning += sa_convence_earning
                    sa_convence_earning_line = payslip.line_ids.filtered(lambda s: s.code == 'SA')
                    sa_convence_earning_line.write({'total': sa_convence_earning})
                    child_education = payslip.line_ids.filtered(lambda s: s.code == 'CE')
                    total_earning += child_education.total
                    medical_toal = payslip.line_ids.filtered(lambda s: s.code == 'Medical')
                    total_earning += medical_toal.total
                    total_earning_line = payslip.line_ids.filtered(lambda s: s.code == 'TE')
                    total_earning_line.write({'total': total_earning})
                    pf = payslip.line_ids.filtered(lambda s: s.code == 'PF')
                    per_day_sal_pf = pf.total / working_days
                    pf_deduction = absent_line_id.number_of_days * per_day_sal_pf
                    pf_earning_var = 0.0
                    if basic_earning > 0.0:
                        if basic_earning * 0.12 <= 1800:
                            pf_earning_var = payslip.round_all(basic_earning * 0.12)
                        if basic_earning * 0.12 > 1800:
                            pf_earning_var = 1800
                    pf_earning = pf_earning_var
                    total_deduction += payslip.round_all(pf_earning)
                    pf_line = payslip.line_ids.filtered(lambda s: s.code == 'PF')
                    pf_line.write({'total': pf_earning})
                    esic = payslip.line_ids.filtered(lambda s: s.code == 'ESIC')
                    total_deduction += esic.total
                    professional_tax = payslip.line_ids.filtered(lambda s: s.code == 'PT')
                    total_deduction += professional_tax.total
                    total_deduction_line = payslip.line_ids.filtered(lambda s: s.code == 'Total Deductions')
                    total_deduction_line.write({'total': total_deduction})
                    other_deduction = payslip.line_ids.filtered(lambda s: s.code == 'Other')
                    per_day_other_deduction = other_deduction.total / working_days
                    other_deduction_days = absent_line_id.number_of_days * per_day_other_deduction
                    other_deduction_earning = payslip.round_all(other_deduction.total - other_deduction_days)
                    other_deduction.write({'total': other_deduction_earning})
                    other_gross = payslip.line_ids.filtered(lambda s: s.code == 'GROSS')
                    # per_day_other_gross = other_gross.total / working_days
                    # gross_days = absent_line_id.number_of_days * per_day_other_gross
                    # gross_earning = round(other_gross.total - gross_days)
                    gross_earning = basic_earning + hra_earning + convence_earning + other_deduction_earning
                    other_gross.write({'total': gross_earning})
                    if (gross_earning > 13304 and gross_earning <= 25000):
                        if payble_days > 0.00:
                            p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 125})
                    else:
                        p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 0.00})
                    if gross_earning >= 25000 and payble_days > 0:
                        p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 200})
                    if payble_days == 0:
                        payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 0.00})
                    if payslip.date_from.month == 3:
                        if payslip.line_ids.filtered(lambda s: s.code == 'PT').total == 200:
                            payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 300})
                    # net_salary_var = round(total_earning - total_deduction)
                    net_salary_line = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    # net_salary_total = net_salary_line.total / working_days
                    # net_salary_absent_days = absent_line_id.number_of_days * net_salary_total
                    for line in payslip.line_ids:
                        line.payable_days = payble_days
                    esi_line = payslip.line_ids.filtered(lambda s: s.code == 'ESIC')
                    per_day_esi = esi_line.total / working_days
                    esi_line_total_earning = absent_line_id.number_of_days * per_day_esi
                    esi_earning = payslip.round_all_pf_esi(esi_line.total - esi_line_total_earning)
                    if gross_earning > 0.00 and gross_earning <= 21000 and other_gross.amount <= 21000:
                        esi_line.write({'total': payslip.round_all_pf_esi(gross_earning * 0.0075)})
                    else:
                        esi_line.write({'total': 0.00})
                    deduction_var = payslip.line_ids.filtered(lambda s: s.category_id.code == 'DED')
                    deduction_var_total = 0.0
                    for i in deduction_var:
                        deduction_var_total += i.total
                    net_salary_var = payslip.round_all(other_gross.total - deduction_var_total)
                    net_salary_line = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    if payble_days == 0.00:
                        net_salary_line.write({'total': 0.00})
                    if payble_days > 0.00:
                        net_salary_line.write({'total': net_salary_var})

                    # payslip.sudo().update({
                    #     'line_ids': [(0, 0, {
                    #         'payable_days': float(var)})]
                    #
                    # })

                    # lwop_line = payslip.line_ids.filtered(lambda s: s.code == 'LWOP')
                    # new_net = net_salary.total - lwop_deduction
                    # lwop_line.write({'amount': lwop_deduction})
                    # net_salary.write({'amount': new_net})
            if payslip.date_to.day != var1  or payslip.date_from.day != first_date_of_month:
                remaining_month_days = var1 - payslip.date_to.day
                absent_line_id = payslip.worked_days_line_ids.filtered(lambda s: s.code == 'MISSATTE ')
                total_earning = 0.0
                total_deduction = 0.0
                net_salary = 0.0
                total_earning_amount = 0.0
                total_deduction_amount = 0.0
                net_salary_amount = 0.0
                if absent_line_id:
                    var = absent_line_id.number_of_days
                    working_days = (payslip.date_to.day - payslip.date_from.day) + 1
                    payble_days = working_days - var
                    net_salary = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    voluntary_pf = payslip.line_ids.filtered(lambda s: s.code == 'VPF')
                    per_day_vpf_amount = voluntary_pf.total/monthrange(payslip.date_from.year, payslip.date_from.month)[-1]
                    voluntary_pf.write({'amount': payslip.round_all(per_day_vpf_amount * working_days)})
                    per_day_sal_vpf = voluntary_pf.total / working_days
                    vpf_deduction = absent_line_id.number_of_days * per_day_sal_vpf
                    vpf_earning = payslip.round_all(voluntary_pf.total - vpf_deduction)
                    voluntary_pf.write({'total': vpf_earning})

                    basic = payslip.line_ids.filtered(lambda s: s.code == 'BASIC')
                    per_day_sal_basic_amount = basic.total / \
                                               monthrange(payslip.date_from.year, payslip.date_from.month)[-1]
                    basic.write({'amount': payslip.round_all(per_day_sal_basic_amount * working_days)})
                    per_day_sal_basic = basic.total / working_days
                    basic_deduction = absent_line_id.number_of_days * per_day_sal_basic
                    basic_earning = payslip.round_all(basic.total - basic_deduction)
                    total_earning += basic_earning
                    total_earning_amount += payslip.round_all(per_day_sal_basic_amount * working_days)
                    basic_line = payslip.line_ids.filtered(lambda s: s.code == 'BASIC')
                    basic_line.write({'total': basic_earning})
                    hra = payslip.line_ids.filtered(lambda s: s.code == 'HRA')
                    per_day_sal_hra_amount = hra.total / \
                                               monthrange(payslip.date_from.year, payslip.date_from.month)[-1]
                    hra.write({'amount': payslip.round_all(working_days * per_day_sal_hra_amount)})
                    per_day_sal_hra = hra.total / working_days
                    hra_deduction = absent_line_id.number_of_days * per_day_sal_hra
                    hra_earning = payslip.round_all(hra.total - hra_deduction)
                    total_earning += hra_earning
                    total_earning_amount += payslip.round_all(working_days * per_day_sal_hra_amount)
                    # hra_line = payslip.line_ids.filtered(lambda s: s.code == 'HRA')
                    hra.write({'total': hra_earning})
                    convence = payslip.line_ids.filtered(lambda s: s.code == 'C')
                    convence_line = payslip.line_ids.filtered(lambda s: s.code == 'C')
                    per_day_sal_convence_amount = convence_line.total / \
                                                  monthrange(payslip.date_from.year, payslip.date_from.month)[-1]
                    convence_line.write({'amount': payslip.round_all(working_days * per_day_sal_convence_amount)})
                    per_day_sal_convence = convence.total / working_days
                    convence_deduction = absent_line_id.number_of_days * per_day_sal_convence
                    convence_earning = payslip.round_all(convence.total - convence_deduction)
                    total_earning += convence_earning
                    total_earning_amount += payslip.round_all(working_days * per_day_sal_convence_amount)
                    convence_line.write({'total': convence_earning})
                    special_allowance_convence = payslip.line_ids.filtered(lambda s: s.code == 'SA')
                    sa_convence_earning_line = payslip.line_ids.filtered(lambda s: s.code == 'SA')
                    per_day_sal_special_allowance_convendce_total = sa_convence_earning_line.total / \
                                                                    monthrange(payslip.date_from.year,
                                                                               payslip.date_from.month)[-1]
                    sa_convence_earning_line.write(
                        {'amount': payslip.round_all(working_days * per_day_sal_special_allowance_convendce_total)})
                    per_day_sal_special_allowance_convendce = special_allowance_convence.total / working_days
                    special_allowance_convence_deduction = absent_line_id.number_of_days * per_day_sal_special_allowance_convendce
                    sa_convence_earning = payslip.round_all(special_allowance_convence.total - special_allowance_convence_deduction)
                    total_earning += sa_convence_earning
                    total_earning_amount += payslip.round_all(working_days * per_day_sal_special_allowance_convendce_total)
                    sa_convence_earning_line.write({'total': sa_convence_earning})
                    child_education = payslip.line_ids.filtered(lambda s: s.code == 'CE')
                    total_earning += child_education.total
                    total_earning_amount += child_education.amount
                    medical_toal = payslip.line_ids.filtered(lambda s: s.code == 'Medical')
                    total_earning += medical_toal.total
                    total_earning_amount += medical_toal.amount
                    total_earning_line = payslip.line_ids.filtered(lambda s: s.code == 'TE')
                    total_earning_line.write({'amount':total_earning_amount})
                    total_earning_line.write({'total': total_earning})
                    pf = payslip.line_ids.filtered(lambda s: s.code == 'PF')
                    pf_line = payslip.line_ids.filtered(lambda s: s.code == 'PF')
                    per_day_sal_pf_amount = pf.total / monthrange(payslip.date_from.year, payslip.date_from.month)[-1]
                    pf_line.write({'amount': payslip.round_all(per_day_sal_pf_amount * working_days)})
                    per_day_sal_pf = pf.total / working_days
                    pf_deduction = absent_line_id.number_of_days * per_day_sal_pf
                    pf_earning_var = 0.0
                    if basic_earning > 0.0:
                        if basic_earning * 0.12 < 1800 :
                            pf_earning_var = payslip.round_all(basic_earning * 0.12)
                        if basic_earning * 0.12 > 1800 :
                            pf_earning_var = 1800
                    pf_earning = pf_earning_var
                    total_deduction += payslip.round_all(pf_earning)
                    total_deduction_amount += payslip.round_all(per_day_sal_pf_amount * working_days)
                    pf_line.write({'total': pf_earning})
                    esic = payslip.line_ids.filtered(lambda s: s.code == 'ESIC')
                    total_deduction += esic.total
                    total_deduction_amount +=esic.amount
                    professional_tax = payslip.line_ids.filtered(lambda s: s.code == 'PT')
                    total_deduction += professional_tax.total
                    total_deduction_amount += professional_tax.amount
                    total_deduction_line = payslip.line_ids.filtered(lambda s: s.code == 'Total Deductions')
                    total_deduction_line.write({'total': total_deduction})
                    total_deduction_line.write({'amount': total_deduction_amount})
                    other_deduction = payslip.line_ids.filtered(lambda s: s.code == 'Other')
                    per_day_other_deduction_amount = other_deduction.total/ monthrange(payslip.date_from.year,
                                                                               payslip.date_from.month)[-1]
                    other_deduction.write({'amount': payslip.round_all(per_day_other_deduction_amount * working_days) })
                    per_day_other_deduction = other_deduction.total / working_days
                    other_deduction_days = absent_line_id.number_of_days * per_day_other_deduction
                    other_deduction_earning = payslip.round_all(other_deduction.total - other_deduction_days)
                    other_deduction.write({'total': other_deduction_earning})
                    other_gross = payslip.line_ids.filtered(lambda s: s.code == 'GROSS')
                    # other_gross_amount = other_gross.total /  monthrange(payslip.date_from.year,
                    #                                                            payslip.date_from.month)[-1]
                    # other_gross.write({'amount': payslip.increase _amount_if_decimal(working_days * other_gross_amount)})
                    # per_day_other_gross = other_gross.total / working_days
                    # gross_days = absent_line_id.number_of_days * per_day_other_gross
                    # gross_earning = round(other_gross.total - gross_days)
                    gross_earning = basic_earning + hra_earning + convence_earning + other_deduction_earning
                    other_gross.write({'total': gross_earning})
                    # other_gross_amount_pt = round(working_days * other_gross_amount)
                    if (gross_earning > 13304 and gross_earning <= 25000):
                        if payble_days > 0.00:
                            p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 125})
                    else:
                        p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 0.00})
                    if gross_earning >= 25000 and payble_days > 0:
                        p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 200})
                    if payble_days == 0:
                        payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 0.00})
                    if payslip.date_from.month == 3:
                        if payslip.line_ids.filtered(lambda s: s.code == 'PT').total == 200:
                            payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 300})
                    if (gross_earning > 13304 and gross_earning <= 25000):
                        if payble_days > 0.00:
                            p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 125})
                    else:
                        p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 0.00})
                    if gross_earning >= 25000 and payble_days > 0:
                        p_tax_line = payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 200})
                    if payble_days == 0:
                        payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'total': 0.00})
                    if payslip.date_from.month == 3:
                        if payslip.line_ids.filtered(lambda s: s.code == 'PT').total == 200:
                            payslip.line_ids.filtered(lambda s: s.code == 'PT').write({'amount': 300})
                    # net_salary_var = round(total_earning - total_deduction)
                    net_salary_line = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    # net_salary_total = net_salary_line.total / working_days
                    # net_salary_absent_days = absent_line_id.number_of_days * net_salary_total
                    for line in payslip.line_ids:
                        line.payable_days = payble_days
                    esi_line = payslip.line_ids.filtered(lambda s: s.code == 'ESIC')
                    per_day_esi_amount = esi_line.total / monthrange(payslip.date_from.year, payslip.date_from.month)[
                        -1]
                    esi_line.write({'amount': payslip.round_all_pf_esi(per_day_esi_amount * working_days)})
                    per_day_esi = esi_line.total / working_days
                    esi_line_total_earning = absent_line_id.number_of_days * per_day_esi
                    esi_earning = payslip.round_all_pf_esi(esi_line.total - esi_line_total_earning)
                    if gross_earning > 0.00 and gross_earning <= 21000 and other_gross.amount <= 21000 :
                        esi_line.write({'total':  payslip.round_all_pf_esi(gross_earning * 0.0075)})
                    else:
                        esi_line.write({'total': 0.00})
                    deduction_var = payslip.line_ids.filtered(lambda s: s.category_id.code == 'DED')
                    deduction_var_total = 0.0
                    deduction_var_amount  = 0.0
                    for i in deduction_var:
                        deduction_var_total += i.total
                    for i in deduction_var:
                        deduction_var_amount += i.amount
                    net_salary_var1 = payslip.round_all(other_gross.total - deduction_var_total)
                    net_salary_amount1 = payslip.round_all(other_gross.amount - deduction_var_amount)
                    net_salary_line = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    net_salary_line_amount = payslip.line_ids.filtered(lambda s: s.code == 'NET')
                    if payble_days > 0.00:
                        net_salary_line_amount.update({'amount': net_salary_amount1,})
                    if payble_days == 0.00:
                        net_salary_line.write({'total': 0.00})
                        net_salary_line.write({'amount': 0.00})
                    if payble_days > 0.00:
                        net_salary_line.update({'total': net_salary_var1,})


                    # payslip.sudo().update({
                    #     'line_ids': [(0, 0, {
                    #         'payable_days': float(var)})]
                    #
                    # })
                    # lwop_line = payslip.line_ids.filtered(lambda s: s.code == 'LWOP')
                    # new_net = net_salary.total - lwop_deduction
                    # lwop_line.write({'amount': lwop_deduction})
                    # net_salary.write({'amount': new_net})
        return res


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    payable_days = fields.Float(string='Payable Days')

