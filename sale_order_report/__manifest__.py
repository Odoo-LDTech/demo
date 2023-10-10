# -*- coding: utf-8 -*-
{
	'name' : 'LD Sale Order Report - Vikram',
	'version' : '16.0.1',
	'author': '',
	'description': "LD Sale Order Report - Vikram",
	'category': 'Report',
	'website': '',
	'depends' : ['base','sale','sale_management','purchase', 'account'],
	'data': [
		'report/report.xml',
		'report/sale_report.xml',
		'report/purchase_report.xml',
		'report/account_report.xml',
		'views/sale_order_view.xml',
		'views/res_partner_view.xml',
	],
	'license':'LGPL-3',
	'installable': True,
	'application': True,
}