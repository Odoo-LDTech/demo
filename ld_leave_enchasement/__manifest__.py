{
    'name': 'Leave Enchasement',
    'version': '1.0.0',
    'category': 'OFC',
    'sequence': -100,
    'summary': 'ld leave enchasement',
    'description': "leave enchasement details",
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/reject_reason.xml',
        'views/leave_enchasement.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}
