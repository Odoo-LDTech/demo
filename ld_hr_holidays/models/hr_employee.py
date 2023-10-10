# -*- coding: utf-8 -*-
import math
from odoo import api, models, fields
from pytz import timezone

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	employee_stage = fields.Selection([
		('probation', 'Probation'),
		('regular', 'Regular'),
		('notice_period', 'Notice Period')], string='Stage', required=True)
	employee_status = fields.Selection([('worker', 'Worker'), ('staff', 'Staff')], 
		string='Employee Status', default='worker')