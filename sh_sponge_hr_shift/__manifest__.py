{
    'name': 'Shift customization',
    'version': '1.0.0',
    'category': 'HR',
    'sequence': -100,
    'summary': 'Shift customization',
    'description': "Shift customization",
    'depends': ['hr', 'ld_hr_employee_shift'],
    'data': [
        'security/ir.model.access.csv',
        'report/hr_bulk_shift_change_views.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}