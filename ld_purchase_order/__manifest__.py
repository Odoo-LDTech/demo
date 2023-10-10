# -*- coding: utf-8 -*-
###################################################################################
{
    'name': 'Purchase Order',
    'version': '16.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Purchase Module customization',
    'author': 'LIVEDIGITAL TECHNOLOGIES PRIVATE LIMITED',
    'company': 'LIVEDIGITAL TECHNOLOGIES PRIVATE LIMITEDs',
    'website': "https://www.ldtech.in",
    'depends': ['base', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_indent_seq_views.xml',
        'views/purchase_indent_views.xml',
        'views/hr_department_view.xml',
        'wizard/reject_remarks_views.xml',
    ],
    
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
