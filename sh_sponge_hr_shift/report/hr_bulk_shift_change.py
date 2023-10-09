# -- coding: utf-8 --
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta
import time


class HRShiftChange(models.Model):
	_name = 'hr.shift.bulk.change'

	department_id = fields.Many2one('hr.department', string="Department", required=True)
	resource_calendar_id = fields.Many2one('resource.calendar', string='Working Hours', required=True)
	date = fields.Date(string="Date", default=fields.Date.today(),  readonly=True)
	all_employees = fields.Boolean('All Employees in selected department')
	employee_ids = fields.Many2many('hr.employee', string='Select Employees')
	company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)


	def action_change_shift(self):
		if self.all_employees == True:
			employee_obj = self.env['hr.employee'].search([('department_id','=',self.department_id.id)]).write({
											'resource_calendar_id': self.resource_calendar_id.id})
			emp_contract_obj = self.env['hr.contract'].search([('employee_id.department_id','=',self.department_id.id),
							('state','=','open')]).write({'resource_calendar_id':self.resource_calendar_id.id})

		if self.all_employees == False:
			employee_obj = self.env['hr.employee'].search([('id','=',self.employee_ids.id)]).write({
											'resource_calendar_id': self.resource_calendar_id.id})
			emp_contract_obj = self.env['hr.contract'].search([('employee_id.id','=',self.employee_ids.id),
							('state','=','open')]).write({'resource_calendar_id':self.resource_calendar_id.id})

	@api.onchange('department_id')
	def onchange_department_id(self):
		if self.department_id:
			return {'domain': {'employee_ids': [('department_id', '=', self.department_id.id)]}}
		else:
			return {'domain': {'employee_ids': []}}