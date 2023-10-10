# -*- coding: utf-8 -*-

{
    'name': 'Odoo14 attendance and leave integration',
    'version': '16.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'depends': ['hr', 'hr_contract','hr_payroll_community','hr_attendance','employee_attendance_roadster'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_attendance.xml',
        # 'data/hr_contract_type_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}