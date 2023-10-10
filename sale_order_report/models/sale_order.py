# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_ref = fields.Date('Date Reference')
    broker_id = fields.Many2one('res.partner', 'Broker')


class SaleOrderReport(models.AbstractModel):
    _name = 'report.sale_order_report.report_saleorder_custom'
    _description = 'Sale Order Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)

        def amount_num2word(amt):
            return num2words(amt).title()

        return {
            'docs': docs,
            'amount_num2word': amount_num2word,
        }


class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_note = fields.Text('Delivery Note')
    reference_date = fields.Date('Reference Date')
    other_references = fields.Char('Other References')
    dispatch_doc_no = fields.Char('Dispatch Doc No.')
    delivery_note_date = fields.Date('Delivery Note Date')
    dispatched_through = fields.Char('Dispatched through')
    destination = fields.Char('Destination')
    bill_of_lading = fields.Char('Bill of Lading')
    moter_vehicle_no = fields.Char('Moter Vehicle No.')
    dispatch_doc_no = fields.Char('Dispatch Doc No.')

    def amount_num2word(self, amt):
        return num2words(amt).title()
