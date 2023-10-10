# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

{
    'name': 'LD Repair Order',
    'version': '16.0.1.0',
    'sequence': 1,
    'category': 'Inventory',
    'description':
        """
       Repair

    """,
    'summary': 'Repair',
    'depends': ['repair'],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_order_views.xml',
        ],
    'demo': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
