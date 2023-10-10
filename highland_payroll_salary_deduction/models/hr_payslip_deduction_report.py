# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: odoo@cybrosys.com
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import fields, models, tools
from datetime import date
import time
from calendar import monthrange


class HrPayrollDeductionReport(models.Model):
    _name = 'hr.payroll.deduction.report'
    _auto = False

    id = fields.Integer(string="ID")
    payslip_name = fields.Char(string="Payslip Name")
    payable_days = fields.Integer(string="Payable Days")
    professional_tax = fields.Integer(string="Professional Tax")
    pf = fields.Integer(string="PF")
    vpf = fields.Integer(string="VPF")
    income_tax = fields.Integer(string="Income Tax")
    employee_code = fields.Char(string="Code")
    esi = fields.Integer(string = "ESI")
    now = date.today()
    month_day = monthrange(now.year, now.month)
    start_date = fields.Date(string="Start Date", default=time.strftime('%Y-%m-01'), invisible=True)
    end_date = fields.Date(string="End Date", default=time.strftime('%Y-%m-' + str(month_day[1]) + ''), invisible=True)
    name = fields.Char(string='Employee Name')
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    state = fields.Selection([('draft', 'Draft'), ('verify', 'Waiting'), ('done', 'Done'), ('cancel', 'Rejected')],
                             string='Status')
    rule_name = fields.Many2one('hr.salary.rule.category', string="Rule Category")
    rule_amount = fields.Float(string="Amount")
    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule")



    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # query = self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( SELECT
        #            %s
        #            FROM %s
        #            %s
        #            )""" % (self._table, self._select(), self._from(), self._group_by()))
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAaaaaa",query)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( 
        SELECT
                min(ps.id) as id ,
                emp.name as name,   
				psl.payable_days as payable_days ,
                ps.number as payslip_name,
                emp.employee_id as employee_code,
                ps.date_from as date_from,
                ps.date_to as date_to,
                (SELECT sum(psl.total)
                    FROM hr_payslip_line psl
                    JOIN hr_salary_rule ON hr_salary_rule.id = psl.salary_rule_id
                    JOIN hr_salary_rule_category  ON hr_salary_rule_category.id = psl.category_id
                    JOIN hr_payslip ON hr_payslip.id = psl.slip_id 
                    JOIN hr_employee ON hr_employee.id = hr_payslip.employee_id
                    WHERE hr_salary_rule.code = 'ESIC' AND hr_employee.id = emp.id and hr_payslip.date_from = ps.date_from  and hr_payslip.date_to = ps.date_to
                    and hr_payslip.id = ps.id  
                ) AS esi,
				(SELECT sum(psl.total)
                    FROM hr_payslip_line psl
                    JOIN hr_salary_rule ON hr_salary_rule.id = psl.salary_rule_id
                    JOIN hr_salary_rule_category  ON hr_salary_rule_category.id = psl.category_id
                    JOIN hr_payslip ON hr_payslip.id = psl.slip_id 
                    JOIN hr_employee ON hr_employee.id = hr_payslip.employee_id
                    WHERE hr_salary_rule.code =  'PF' AND hr_employee.id = emp.id and hr_payslip.date_from = ps.date_from  and hr_payslip.date_to = ps.date_to and
                    hr_payslip.id = ps.id  
                ) AS pf,
                (SELECT sum(psl.total)
                    FROM hr_payslip_line psl
                    JOIN hr_salary_rule ON hr_salary_rule.id = psl.salary_rule_id
                    JOIN hr_salary_rule_category  ON hr_salary_rule_category.id = psl.category_id
                    JOIN hr_payslip ON hr_payslip.id = psl.slip_id 
                    JOIN hr_employee ON hr_employee.id = hr_payslip.employee_id
                    WHERE hr_salary_rule.code =  'VPF' AND hr_employee.id = emp.id and hr_payslip.date_from = ps.date_from  and hr_payslip.date_to = ps.date_to and
                    hr_payslip.id = ps.id  
                ) AS vpf,
                (SELECT sum(psl.total)
                    FROM hr_payslip_line psl
                    JOIN hr_salary_rule ON hr_salary_rule.id = psl.salary_rule_id
                    JOIN hr_salary_rule_category ON hr_salary_rule_category.id = psl.category_id
                    JOIN hr_payslip ON hr_payslip.id = psl.slip_id 
                    JOIN hr_employee ON hr_employee.id = hr_payslip.employee_id
                    WHERE hr_salary_rule.code = 'PT' AND hr_employee.id = emp.id and hr_payslip.date_from = ps.date_from  and hr_payslip.date_to = ps.date_to
                    and hr_payslip.id = ps.id 
                ) AS professional_tax,
                (SELECT sum(psl.total)
                    FROM hr_payslip_line psl
                    JOIN hr_salary_rule ON hr_salary_rule.id = psl.salary_rule_id
                    JOIN hr_salary_rule_category  ON hr_salary_rule_category.id = psl.category_id
                    JOIN hr_payslip ON hr_payslip.id = psl.slip_id 
                    JOIN hr_employee ON hr_employee.id = hr_payslip.employee_id
                    WHERE hr_salary_rule.code = 'INT' AND hr_employee.id = emp.id and hr_payslip.date_from = ps.date_from  and hr_payslip.date_to = ps.date_to 
                ) AS income_tax
				
                
				
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        FROM
                hr_payslip_line psl
                JOIN hr_payslip ps ON ps.id = psl.slip_id
                JOIN hr_salary_rule rlu ON rlu.id = psl.salary_rule_id
                JOIN hr_employee emp ON ps.employee_id = emp.id 
                JOIN hr_salary_rule_category rl ON rl.id = psl.category_id
		WHERE
		    rlu.code in ('ESIC','VPF','PT','INT','PF')
		group by
			ps.id,emp.id,psl.payable_days

        )""" % (self._table,))
