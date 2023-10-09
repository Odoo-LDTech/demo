from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta
import time


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	def update_contracts(self, new_calendar_id):
		self.env['hr.contract'].search([('employee_id','in',self.ids),('state','=','open')]).write({
			'resource_calendar_id': new_calendar_id})

	@api.onchange('resource_calendar_id')
	def onch_resource_cal_id(self):
		if self.resource_calendar_id:
			self.update_contracts(self['resource_calendar_id'])