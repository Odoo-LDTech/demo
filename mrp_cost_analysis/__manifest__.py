# -*- coding: utf-8 -*-

{
    'name': 'LD - MRP Cost Analysis Report',
    'version': '1.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'MRP Cost Analysis Report For Odoo Community version.',
    'description': 'MRP Cost Analysis Report For Odoo Community version.',
    'author': 'Livedigital Technologies Private Limited',
    'company': 'Livedigital Technologies Private Limited',
    'maintainer': 'Livedigital Technologies Private Limited',
    'website': 'https://ldtech.in',
    'depends': ['mrp', 'account'],
    'data': [
        'views/mrp_account_view.xml',
        'views/cost_structure_report.xml',
        ],
    'installable': True,
    'assets': {
        'web.report_assets_common': [
            'mrp_cost_analysis/static/src/scss/cost_structure_report.scss',
        ],
    }
}
