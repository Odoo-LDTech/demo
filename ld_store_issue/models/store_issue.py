# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError

class StoreIssue(models.Model):
	_name= 'store.issue'
	_inherit = ['mail.thread']
	_description = "Store Issue"
	_order = "name desc"

	def compute_count(self):
		for record in self:
			record.picking_count = self.env['stock.picking'].search_count([('store_issue_id', '=', self.id)])

	def _get_employee_id(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		return employee_id.id

	@api.depends('state')
	def get_hod(self):
		for data in self:
			data.is_hod = False
			if data.env.user.id == data.employee_id.parent_id.user_id.id:
				data.is_hod = True

	name = fields.Char(string="Issue No", readonly=True, default="New")
	rejected_remarks = fields.Char(string="Rejected Remarks", readonly=True, track_visibility='always',)
	notes = fields.Text(string="Description", track_visibility='always',)
	date = fields.Date(string='Date', default=datetime.today())
	employee_id = fields.Many2one('hr.employee', string='Employee', default=_get_employee_id,
									track_visibility='onchange')
	state = fields.Selection([
		('new', 'New'),
		('send_for_hod', 'Waiting for HOD Approval'),
		('hod_approved', 'Confirm'),
		('rejected', 'Rejected'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='always', default='new')
	department_id = fields.Many2one('hr.department', string='Department', related="employee_id.department_id", readonly=False)
	picking_id = fields.Many2one('stock.picking', string='Picking')
	product_ids = fields.One2many('store.products', 'store_id', string='Material')
	picking_count = fields.Integer('Material Issue',compute='compute_count')
	is_material_issue = fields.Boolean(string='Material Issue',default=False, copy=False)
	is_hod = fields.Boolean(string='HOD',readonly=True,  compute='get_hod')
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
	

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('store.issue')
		return super(StoreIssue, self).create(vals)

	def button_send_hod_approval(self):
		for rec in self:
			if not rec.product_ids:
				raise UserError(_("Please select the material details."))
			else:
				rec.write({'state':'send_for_hod'})

	def button_hod_approved(self):
		self.write({'state':'hod_approved'})

	def button_reject(self):
		form_view = self.env.ref('ld_store_issue.material_issue_reject_remark_view_id')
		return {
				'name': "Reject Remarks",
				'view_mode': 'form',
				'view_type': 'form',
				'view_id': form_view.id,
				'res_model': 'material.issue.reject.remark',
				'type': 'ir.actions.act_window',
				'target': 'new',
			}

	def get_picking(self):
		"""Picking smart button"""
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Material Transfer',
			'view_mode': 'tree,form',
			'res_model': 'stock.picking',
			'domain': [('store_issue_id', '=', self.id)],
			'context': "{'create': False}"
		}

	def create_material_issue(self):
		emp_location = self.env["stock.location"].search([('name', '=', 'Employee Location')])
		if not emp_location:
			loc = self.env["stock.location"].create({
				'name':'Employee Location',
				'usage':'inventory',
				})
		if emp_location:
			picking_type_id = self.env["stock.picking.type"].search([('sequence_code', '=', 'INT')],limit=1,order = 'id asc')
			source_locaion_id = self.env["stock.location"].search([('name', '=', 'Physical Locations')],limit=1,order = 'id asc')
			picking = self.env['stock.picking'].create({
					'picking_type_id': picking_type_id.id,
					'location_id': source_locaion_id.id,
					'location_dest_id': emp_location.id ,
					'origin': self.name,
					'store_issue_id': self.id,
					'state':'draft'
					})
			for line in self.product_ids:
				picking_line = self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom': line.product_uom.id,
					'location_id': picking.location_id.id,
					'location_dest_id': picking.location_dest_id.id,
					'product_uom_qty': line.product_qty,
					'picking_id': picking.id,
					'is_quantity_done_editable': True,
					})
			picking.action_confirm()
			# picking.action_set_quantities_to_reservation()
			picking.action_assign()
			self.picking_id = picking.id
			self.is_material_issue = True
		else:
			self.create_material_issue()


class StoreProducts(models.Model):
	_name = "store.products"
	_description = "Store Products"


	product_id = fields.Many2one('product.product', string='Product', required=True)
	available_qty = fields.Integer(string='Available Qty', readonly=True)
	product_qty = fields.Float(string='Required Qty', digits='Product Unit of Measure', 
								required=True, default='1')
	store_id = fields.Many2one('store.issue',string="Product Details")
	product_uom = fields.Many2one(related='product_id.uom_id', string='Unit of Measure',)


	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.write({'available_qty':self.product_id.qty_available})

	@api.constrains('product_qty')
	def _check_validations(self):
		for line in self:
			if line.product_qty < 1:
				raise UserError(_("'Required Qty' should be greater then Zero."))


class Picking(models.Model):
	_inherit = 'stock.picking'


	def compute_store_count(self):
		for record in self:
			record.store_issue_count = self.env['store.issue'].search_count([('picking_id', '=', self.id)])


	store_issue_id = fields.Many2one('store.issue', string='Store Issue')
	store_issue_count = fields.Integer('Store Issue',compute='compute_store_count')

	def get_store_issue(self):
		"""Indent smart button"""
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Store Issue',
			'view_mode': 'tree,form',
			'res_model': 'store.issue',
			'domain': [('picking_id', '=', self.id)],
			'context': "{'create': False}"
		}