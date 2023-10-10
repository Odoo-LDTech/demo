# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
	_inherit = 'res.partner'

	is_broker = fields.Boolean('Is Broker')
	is_customer = fields.Boolean('Is Customer')
	is_vendor = fields.Boolean('Is Vendor')


class ResCompany(models.Model):
	_inherit = 'res.company'

	so_company_details = fields.Html('Company Details')
	so_footer_line1 = fields.Char('Footer Line 1')
	so_footer_line2 = fields.Char('Footer Line 2')

	po_company_details = fields.Html('Company Details')
	po_footer_line1 = fields.Char('Footer Line 1')
	po_footer_line2 = fields.Char('Footer Line 2')
