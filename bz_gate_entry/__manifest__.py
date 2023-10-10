# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

{
    'name': 'LD Gate Entry',
    'version': '16.0.1.0',
    'sequence': 1,
    'category': 'Inventory',
    'description':
        """
      Gate Entry

    """,
    'summary': 'Gate Entry',
    'depends': ['stock', 'purchase', 'fleet', 'mail', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/gate_entry.xml',
        # 'views/stock_picking.xml',
        'data/ir_sequence.xml',
        ],
    'demo': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
