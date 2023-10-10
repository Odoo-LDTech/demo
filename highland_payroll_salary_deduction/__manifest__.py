# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Highland Payroll Salary Deduction',
    'version': '16.0.1',
    'category': 'hr',
    'author': 'Live digital marketing solutions pvt ltd',
    'website': 'https://www.ldtech.in/',
    'depends': ['hr', 'hr_attendance', 'hr_holidays', 'hr_payroll_community', 'hr_contract','hr_payslip_monthly_report',],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_deduction_report.xml',
        'views/hr_payslip.xml',
        'views/deduction.xml',
        # 'data/ir_cron.xml',
    ],
    'demo': [],
    "application": True,
    'installable': True,
    'auto_install': False,
}
