from odoo import models, fields, api
import math
from odoo.exceptions import Warning, UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # employee_part = fields.Char(string='Emp')
    currency_id = fields.Many2one('res.currency', string='Currency')
    basic = fields.Float(string='Basic')
    hra = fields.Float(string='HRA')
    special_allowance = fields.Float(string='Other Allowance')
    gross = fields.Float(string='Gross')
    pf = fields.Float(string='PF',default=0.00)
    voluntary_pf = fields.Float(String="Ex. PF")
    p_tax = fields.Float(string='P.Tax')
    esi = fields.Float(string='ESI')
    income_tax = fields.Float(string='Income Tax')
    welfare_deduction = fields.Float(string='Welfare Deduction')
    in_hand = fields.Integer(string='In Hand', compute='_calculate_in_hand',store=True,default=0.00)
    employer_pf = fields.Float(string='Employer PF')
    employer_esi = fields.Float(string='Employer ESI')
    bonus = fields.Float(string='Bonus')
    gratuity = fields.Float(string='Gratuity')
    annual_g = fields.Float(string='Annual G')
    annual_pf = fields.Float(string='Annual PF')
    annual_bonus = fields.Float(string='Annual Bonus')
    annual_gratuity = fields.Float(string='Employee Gratuity')
    ctc_yearly = fields.Float(string='CTC Yearly')
    ctc_monthly = fields.Float(string='CTC Monthly')
    conveyance = fields.Float(string='Conveyance')
    employee_code = fields.Char(related="employee_id.employee_id",string='Employee ID', tracking=True)

    def round_all_pf_esi(self, amount):
        fractional_part = amount - int(amount)
        if fractional_part == 0.00:
            return amount
        if fractional_part >= 0.01:
            amount += 1
        return int(amount)

    def round_all(self, amount):
        fractional_part = amount - int(amount)
        if fractional_part == 0.00:
            return amount
        if fractional_part >= 0.01 and fractional_part <=0.49:
            return int(amount)
        if fractional_part >= 0.50:
            amount += 1
            return int(amount)


    @api.depends('voluntary_pf', 'welfare_deduction', 'income_tax','esi','wage','pf','p_tax')
    def _calculate_in_hand(self):
        for rec in self:
            rec.in_hand =  rec.round_all(rec.wage - (
                rec.esi + rec.pf + rec.voluntary_pf + rec.p_tax + rec.income_tax + rec.welfare_deduction))


    @api.model
    def default_get(self, fields):
        res = super(HrContract, self).default_get(fields)
        res['p_tax'] = 0.00
        res['in_hand'] = 0.00
        return res

    @api.onchange('voluntary_pf', 'welfare_deduction', 'income_tax')
    def get_values(self):
        for rec in self:
            if not rec.basic and rec.wage:
                rec.basic = round((rec.wage * 0.5))
            if not rec.hra and rec.basic:
                rec.hra = round((rec.basic * 0.3))
            if not rec.special_allowance and  rec.wage and  rec.wage and rec.hra:
                rec.special_allowance = round((rec.wage - rec.basic - rec.hra))
            if not rec.pf and rec.basic:
                rec.pf = round((rec.basic * 0.12))
            if not rec.conveyance and rec.basic:
                rec.conveyance = round((rec.basic * 0.25))
            if rec.wage > 13304 and rec.wage <= 25000 :
                rec.p_tax = 125
            if rec.wage >= 25000 :
                rec.p_tax = 200
            rec.esi = (rec.wage * 0.0075)
            # rec.in_hand = (rec.wage - rec.pf - rec.p_tax)
            if not rec.employer_pf and  rec.basic:
                rec.employer_pf = round((rec.basic * 0.12) if (rec.basic * 0.12) < 1800 else 1800)
            if not rec.pf and rec.basic:
                rec.pf = round((rec.basic * 0.12) if (rec.basic * 0.12) < 1800 else 1800)
            if not rec.esi and rec.wage:
                rec.esi = round(math.ceil((0.75 * rec.wage) / 100 if rec.wage <= 21000 else 0.00))
            if not rec.employer_esi and rec.wage:
                rec.employer_esi = round(((3.25 * rec.wage) / 100) if rec.wage <= 21000 else 0.00)
            if not rec.special_allowance and rec.basic and  rec.hra and  rec.conveyance and  rec.wage:
                rec.special_allowance = round(rec.wage - (rec.basic + rec.hra + rec.conveyance))
            # rec.bonus = rec.wage
            # if not rec.gratuity and  rec.basic:
            rec.gratuity = round((rec.basic * 15 * 5 / 26 / 60))
            # if not rec.annual_g and rec.wage:
            rec.annual_g = round((rec.wage * 12))
            # if not rec.annual_pf and  rec.pf:
            rec.annual_pf = round(12 * rec.pf)
            rec.in_hand = round(rec.wage - (
                    rec.esi + rec.pf + rec.voluntary_pf + rec.p_tax + rec.income_tax + rec.welfare_deduction))
            # rec.annual_bonus = rec.bonus
            # if not rec.annual_gratuity and  rec.gratuity:
            rec.annual_gratuity = round((rec.gratuity * 12))
            rec.ctc_monthly = round(rec.wage + rec.employer_esi + rec.employer_pf + rec.gratuity + (rec.bonus / 12))
            rec.ctc_yearly = round(12 * rec.ctc_monthly)

    @api.constrains('voluntary_pf')
    def voluntary_pf_constraint(self):
        for rec in self:
            voluntary_pf = round(8 * rec.basic / 100)
            print("voluntary_pfvoluntary_pfvoluntary_pfvoluntary_pf", voluntary_pf)
            print("rec.voluntary_pfrec.voluntary_pfrec.voluntary_pfrec.voluntary_pf", rec.voluntary_pf)
            if not rec.voluntary_pf <= voluntary_pf:
                raise UserError("Voluntary PF is should be up to 8% of basic")

    @api.onchange('wage')
    def get_values(self):
        for rec in self:
            rec.basic = round((rec.wage * 0.5))
            rec.hra = round((rec.basic * 0.3))
            rec.special_allowance = round((rec.wage - rec.basic - rec.hra))
            rec.pf = round((rec.basic * 0.12))
            rec.conveyance = round((rec.basic * 0.25))
            if rec.wage > 13304 and rec.wage <= 25000 :
                rec.p_tax = 125
            if rec.wage >= 25000 :
                rec.p_tax = 200
            rec.esi = (rec.wage * 0.0075)
            # rec.in_hand = (rec.wage - rec.pf - rec.p_tax)
            rec.employer_pf = round((rec.basic * 0.12) if (rec.basic * 0.12) < 1800 else 1800)
            rec.pf = round((rec.basic * 0.12) if (rec.basic * 0.12) < 1800 else 1800)
            rec.esi = round(math.ceil((0.75 * rec.wage) / 100 if rec.wage <= 21000 else 0.00))
            rec.employer_esi = round(((3.25 * rec.wage) / 100) if rec.wage <= 21000 else 0.00)
            rec.special_allowance = round(rec.wage - (rec.basic + rec.hra + rec.conveyance))
            # rec.bonus = rec.wage
            # if not rec.gratuity and  rec.basic:
            rec.gratuity = round((rec.basic * 15 * 5 / 26 / 60))
            # if not rec.annual_g and rec.wage:
            rec.annual_g = round((rec.wage * 12))
            # if not rec.annual_pf and  rec.pf:
            rec.annual_pf = round(12 * rec.pf)
            if rec.wage:
                rec.in_hand = round(rec.wage - (
                        rec.esi + rec.pf + rec.voluntary_pf + rec.p_tax + rec.income_tax + rec.welfare_deduction))
            # rec.annual_bonus = rec.bonus
            # if not rec.annual_gratuity and  rec.gratuity:
            rec.annual_gratuity = round((rec.gratuity * 12))
            rec.ctc_monthly = round(rec.wage + rec.employer_esi + rec.employer_pf + rec.gratuity + (rec.bonus / 12))
            rec.ctc_yearly = round(12 * rec.ctc_monthly)





