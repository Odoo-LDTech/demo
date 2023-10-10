{
    'name': 'Hr Contract',
    'version': '1.0.0',
    'category': 'OFC',
    'sequence': -100,
    'summary': 'ld hr contract',
    'description': "hr contract details",
    'depends': ['hr', 'ohrms_overtime', 'hr_timesheet'],
    'data': [
        'views/hr_contract.xml',
        'views/hr_employee.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}