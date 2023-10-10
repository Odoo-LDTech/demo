# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Attendance Roadster',
    'version': '16.0.1',
    'summary': 'Employee Attendance Roadster',
    'description': """Employee Attendance Roadster""",
    'category': 'hr',
    'author': 'Live digital marketing solutions pvt ltd',
    'website': 'https://www.ldtech.in/',
    'depends': ['hr', 'hr_attendance', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_attendance.xml',
        'data/ir_cron.xml',
    ],
    'demo': [],
    "application": True,
    'installable': True,
    'auto_install': False,
}
