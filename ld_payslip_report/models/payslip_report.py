from odoo import api, fields, models
import datetime
import calendar

class PayslipReport(models.Model):
    _name = "payslip.report"

    name = fields.Char(string='Name')
    employee_id = fields.Char(string='Employee ID')
    designation = fields.Char(string='Designation')
    email_id = fields.Char(string='Email ID')
    esic = fields.Char(string='ESIC')
    uan = fields.Char(string='UAN')
    aadhar_no = fields.Integer(string='Aadhar No.')
    pan = fields.Char(string='PAN')
    bank_name = fields.Char(string='Bank Name')
    account_no = fields.Integer(string='Account No')
    calendar_days = fields.Char(string='Calendar Days')

    gross = fields.Integer(string='Gross')
    employer_pf = fields.Integer(string='Employer PF')
    basic = fields.Integer(string='Basic')
    employee_pf = fields.Integer(string='Employee PF')
    hra = fields.Integer(string='HRA')
    esi = fields.Integer(string='ESI')
    special_allowance = fields.Integer(string='Special Allowance')
    gratutity = fields.Integer(string='Gratutity')
    bonus = fields.Integer(string='Bonus')

    total_earnings = fields.Integer(string='Total Earnings:')
    total_deductions = fields.Integer(string='Total Deductions:')
    net_payable = fields.Integer(string='Net Payable:')
    net_payable_in_words = fields.Char(string='Net Payable in words:')


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    pan_number = fields.Char(string='PAN Number')
    esic = fields.Char(string='ESIC')
    uan = fields.Char(string='UAN')


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    def cal_payable_days(self):
        for rec in self:
            if rec.line_ids and rec.contract_id and rec.employee_id :
                if rec.line_ids.filtered(lambda x:x.payable_days > 0.0).search([ ],limit=1):
                    return rec.line_ids.filtered(lambda x:x.payable_days > 0.0).search([ ],limit=1).payable_days
                else:
                    return  0.0


    employee = fields.Char(string='Employee ID')
    # payable_days = fields.Integer(string='Payable Days',compute='cal_payable_days',default=0.0)
    word_num = fields.Char(string="Amount In Words:", compute='_amount_in_word')
    year_get = fields.Integer(string="Year:", compute='year_name')
    month_get = fields.Char(string="Month:", compute='month_name')

    def month_name(self):
        month = datetime.datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime('%m')
        self.month_get = calendar.month_name[int(month)]

    def year_name(self):
        year = datetime.datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime('%Y')
        self.year_get = int(year)

    @api.onchange('employee_id')
    def onch_employee_id(self):
        self.employee = self.employee_id.employee_id

    def _amount_in_word(self):
        for rec in self:
            for amt in rec.line_ids:
                if amt.name == "Net Salary":
                    rec.word_num = str(rec.employee_id.company_id.currency_id.amount_to_text(amt.total))
                else:
                    rec.word_num = False
                if amt.name == "Loan":
                    rec.loan_value = amt.total
                if amt.name == "ESI":
                    rec.esi_value = amt.total
                if amt.name == "Income Tax":
                    rec.income_tax_value = amt.total
                if amt.name == "Welfare fund":
                    rec.welfare_fund_value = amt.total
                if amt.name == "Other Deduction":
                    rec.other_deduction_value += amt.total
                if amt.name == "Conveyance Allowance":
                    rec.conveyance_allowance_value += amt.amount

            for prcal in rec.worked_days_line_ids:
                if prcal.name == "Regular Attendance days":
                    rec.reg_day = prcal.number_of_days
                if prcal.name == "ESI Attendance days":
                    rec.esi_day = prcal.number_of_days
                if prcal.name == "OnDuty Attendance days":
                    rec.onduty_day = prcal.number_of_days
                if prcal.name == "WeekOff  days":
                    rec.weekoff_day = prcal.number_of_days
                if prcal.name == "Public  days":
                    rec.public_day = prcal.number_of_days

            rec.prcalc = float(rec.reg_day + rec.esi_day + rec.onduty_day)
            rec.offdays = float(rec.weekoff_day + rec.public_day)

    reg_day = fields.Integer(string="Regular Attendance days:", compute='_amount_in_word')
    esi_day = fields.Integer(string="ESI Attendance days:", compute='_amount_in_word')
    onduty_day = fields.Integer(string="OnDuty Attendance days:", compute='_amount_in_word')
    prcalc = fields.Integer(string="PR Days:", compute='_amount_in_word')

    weekoff_day = fields.Integer(string="WeekOff days:", compute='_amount_in_word')
    public_day = fields.Integer(string="Public days:", compute='_amount_in_word')
    offdays = fields.Integer(string="OFF days:", compute='_amount_in_word')

    esi_value = fields.Float(string="ESI", compute='_amount_in_word')
    income_tax_value = fields.Float(string="Income Tax", compute='_amount_in_word')
    welfare_fund_value = fields.Float(string="Income Tax", compute='_amount_in_word')
    loan_value = fields.Float(string="Advance", compute='_amount_in_word')
    other_deduction_value = fields.Float(string="Deduction Value", compute='_amount_in_word')
    conveyance_allowance_value = fields.Float(string="Conveyance Allowance", compute='_amount_in_word')

# class HrContractInherit(models.Model):
#     _inherit = 'hr.contract'
#
#     income_tax = fields.Char(string='Income Tax')
