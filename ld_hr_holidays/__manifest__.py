{
    'name': 'Hr Holidays',
    'version': '1.0.0',
    'category': 'hr',
    'summary': 'ld hr holidays',
    'description': "hr contract details",
    'depends': ['base','hr','hr_holidays'],
    'data': [
        'data/causal_leave.xml',
        'data/ir_cron.xml',
        'views/hr_employee.xml',
        'views/hr_leave_allocation.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}