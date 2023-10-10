# -*- coding: utf-8 -*-

{

    'name': 'HR payment Advise',
    'version': '14.0.1.0.0',
    'description': 'This module enables multi company features',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr','hr_contract', 'hr_payroll_community', ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payroll_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
