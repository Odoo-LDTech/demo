{
    'name': 'Payslip Report',
    'version': '1.0.0',
    'category': 'Task',
    'sequence': -100,
    'summary': 'Salary Payslip Report',
    'description': "Process the products and other fields in a customized way.",
    'depends': ['hr', 'hr_payroll_community'],
    'data': [
        'security/ir.model.access.csv',
        'views/payslip_report.xml',
        'report/payslip_report.xml',
        'report/payslip_template.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}
