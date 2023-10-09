# -*- encoding: utf-8 -*-
{
    'name': 'LD : Master Production Schedule',
    'author': 'Livedigital Technologies Private Limited',
    'company': 'Livedigital Technologies Private Limited',
    'maintainer': 'Livedigital Technologies Private Limited',
    'website': 'https://ldtech.in',
    'version': '1.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Master Production Schedule',
    'depends': ['base_import', 'mrp', 'purchase_stock'],
    'description': 'This app enables the Master Production Schedule Feature.',
    'data': [
        'security/ir.model.access.csv',
        'security/mrp_mps_security.xml',
        'views/mrp_mps_views.xml',
        'views/mrp_mps_menu_views.xml',
        'views/mrp_product_forecast_views.xml',
        'views/inhe_views.xml',
        'views/mrp_mps_forecast_details_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_mps/static/src/**/*',
        ],
    }
}
