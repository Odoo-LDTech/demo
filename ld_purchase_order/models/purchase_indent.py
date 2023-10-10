# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError
from dateutil.relativedelta import relativedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _compute_indent_count(self):
        for record in self:
            record.indent_count = self.env['purchase.indent'].search_count([('id', '=', self.indent_id.id)])

    indent_id = fields.Many2one('purchase.indent', string='Purchase Indent')
    indent_count = fields.Integer(string="Indent Count", compute='_compute_indent_count')

    @api.constrains('order_line')
    def _check_prod_id(self):
        for record in self:
            if not record.order_line:
                raise ValidationError("Select at-least one product in the order line.")

    def action_open_indent(self):
        """Indent smart button"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.indent',
            'domain': [('id', '=', self.indent_id.id)],
            'context': "{'create': False}"
        }


class PurchaseIndent(models.Model):
    _name = 'purchase.indent'
    _inherit = ['mail.thread']
    _description = "Purchase Indent"
    _order = "id desc"

    @api.depends('prod_ids.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.prod_ids:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    def _get_employee_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_id.id

    name = fields.Char(string='Indent No', default='New')
    indent_date = fields.Date(string='Indent date', readonly=True, default=datetime.today())
    state = fields.Selection([
        ('new', 'New'),
        ('hod_in_progress', 'Waiting for HOD Approval'),
        ('sm_in_progress', 'Waiting for SM Approval'),
        ('sm_approved', 'SM Approved'),
        ('rejected', 'Rejected'),
        ('close', 'Closed'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='always', default='new')
    indent_type = fields.Selection([
        ('normal', 'Normal'),
        ('emergency', 'Emergency'),
    ], string='Indent Type', track_visibility='always', default='normal')
    rejected_remarks = fields.Text(string='Rejected Remarks', track_visibility='always', readonly=True)
    material_required_date = fields.Date(string='Material required date')
    inspection_criteria = fields.Char(string='Inspection Criteria')
    user_remarks = fields.Text('User Remarks', track_visibility='always')
    hod_remarks = fields.Text('HOD Remarks', track_visibility='always')
    sm_remarks = fields.Text('Store Manager Remarks', track_visibility='always')
    delivery_location = fields.Char('Delivery Location', track_visibility='always')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
                                     compute='_amount_all', tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    department_flag = fields.Boolean(string='Department Flag', copy=False, compute='get_department_flag')
    store_manager_flag = fields.Boolean(string='Store Manager', copy=False, compute='get_store_manager_flag')

    # Relational Fields
    prod_ids = fields.One2many('product.details', 'prod_id', string='Product Details', required=True)
    store_manager_id = fields.Many2one('hr.employee', string="Store Manager", readonly=True)
    ana_cost_center_id = fields.Many2one('account.analytic.account', string='Cost Center')
    rejected_user_id = fields.Many2one('res.users', 'Cancelled User', readonly=True)
    hod_id = fields.Many2one('hr.employee', string='HOD', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', string='Requested By', required=True, default=_get_employee_id,
                                  track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    rfq_count = fields.Integer(string="RFQ Count", compute='_compute_rfq_count')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Indent')

    def _compute_rfq_count(self):
        for record in self:
            record.rfq_count = self.env['purchase.order'].search_count([('indent_id', '=', self.id)])

    def action_send_hod_approval(self):
        self.state = 'hod_in_progress'

    def action_hod_approved(self):
        self.state = 'sm_in_progress'

    def action_sm_approved(self):
        self.state = 'sm_approved'

    def action_rfq_count(self):
        """Purchase smart button"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('indent_id', '=', self.id)],
            'context': "{'create': False}"
        }

    @api.depends('state', 'department_id')
    def get_department_flag(self):
        for data in self:
            data.department_flag = False
            department_user = data.hod_id and data.hod_id.user_id and data.hod_id.user_id.id or False
            if self.env.user.id == department_user:
                data.department_flag = True

    @api.depends('state', 'department_id')
    def get_store_manager_flag(self):
        for data in self:
            data.store_manager_flag = False
            store_manager = data.store_manager_id and data.store_manager_id.user_id and data.store_manager_id.user_id.id or False
            if self.env.user.id == store_manager:
                data.store_manager_flag = True

    def button_reject(self):
        form_view = self.env.ref('ld_purchase_order.reject_remark_view_id')
        return {
            'name': "Reject Remarks",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view.id,
            'res_model': 'reject.remark',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('employee_id')
    def onchange_department_id(self):
        for record in self:
            if record.employee_id:
                record.hod_id = record.employee_id.department_id.manager_id.id or False
                record.store_manager_id = record.employee_id.department_id.store_manager_id.id or False

    @api.model
    def create(self, vals):
        vals.update({'name': 'IND/' + self.env['ir.sequence'].next_by_code('purchase.indent.sequence') or _('New')})
        return super(PurchaseIndent, self).create(vals)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id

    def new_purchase_quotation(self):
        view = self.env.ref('ld_purchase_order.new_purchase_quaotation_wizard')
        return {
            'name': _('New Quotation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'pi.quotation',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
        }

    @api.constrains('prod_ids')
    def _check_number_of_products(self):
        for record in self:
            if not record.prod_ids:
                raise ValidationError("Add a product to the order line.")


class PIQuotation(models.Model):
    _name = 'pi.quotation'
    _description = "PI Quotaion"

    # category_id = fields.Many2one('partner.category', string='Vendor Category', required=False)
    date = fields.Date(string='Response Date', index=True, default=datetime.today(), readonly=True)
    partner_ids = fields.Many2many('res.partner', string="Vendors")

    def create_quotation(self):
        active_id = self.env.context.get('active_ids')
        for poi in self.env['purchase.indent'].browse(active_id):
            for vendors in self.partner_ids:
                purchase = self.env['purchase.order'].create({
                    'partner_id': vendors.id,
                    # 'indent_id': [4, poi.id] if poi.id else False,
                    'indent_id': poi.id,
                    'state': 'draft'
                })
                for line in poi.prod_ids:
                    purchase_line = self.env['purchase.order.line'].create({
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'order_id': purchase.id,
                        'price_unit': line.price_unit,
                    })
                poi.purchase_id = purchase.id


class ProductDetails(models.Model):
    _name = "product.details"
    _description = "Product Details"

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'], )
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.prod_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            # 'partner': self.prod_id.partner_id,
        }

    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description', related='product_id.name')
    available_qty = fields.Integer(string='Available Qty')
    product_qty = fields.Float(string='Required Qty', digits='Product Unit of Measure',
                               required=True, default='1')
    product_uom = fields.Many2one(related='product_id.uom_id', string='Unit of Measure', )
    is_purchase = fields.Boolean(string='Need Purchase', readonly=True)
    code = fields.Char('Code', readonly=True)
    schedule_date = fields.Date(string='Scheduled Date')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    lpp = fields.Float(string='LPP', readonly=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    prod_id = fields.Many2one('purchase.indent', string="Product Details")

    price_subtotal = fields.Monetary(compute='_compute_amount', digits=(16, 2), string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    remarks = fields.Text(string='Remarks')

    @api.onchange('product_id', 'product_qty')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.standard_price
            self.code = self.product_id.default_code
            self.write({'available_qty': self.product_id.qty_available})
            if self.product_qty > self.available_qty:
                self.write({'is_purchase': True})
            else:
                self.write({'is_purchase': False})
            self.update({'taxes_id': [(6, 0, self.product_id.supplier_taxes_id.ids)]})
            po_line_obj = self.env["purchase.order.line"].search([('product_id', '=', self.product_id.id),
                                                                  ('order_id.state', '=', 'purchase')], limit=1,
                                                                 order='id desc')
            self.lpp = po_line_obj.price_unit
            for line in self:
                line.update({'taxes_id': [(6, 0, line.product_id.taxes_id.ids)]})


