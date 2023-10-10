# -*- coding: utf-8 -*-

{
    'name': 'LD : MRP Work order Raw Material Update',
    'version': '1.0',
    'author': 'Livedigital Technologies Private Limited',
    'company': 'Livedigital Technologies Private Limited',
    'maintainer': 'Livedigital Technologies Private Limited',
    'website': 'https://ldtech.in',
    'depends': ['mrp'],
    'summary': 'This app allows you to update raw quantities in work order.',
    'description': '''
    Usually inside Odoo mrp work order, you enter end quantity
    and Odoo calculates raw quantity according to BOM. But opposite
    does not happens. But by installing this app, will let you to
    do this. You can update any raw material line and then Odoo will
    compute the end quantity and update the other raw lines too.
    ''',
    'license': 'LGPL-3',
    'installable': True,
    'active': False,
    'data': ['views/batch_mrp_view.xml'],

}

