# -*- coding: utf-8 -*-
import math
from odoo import api, models, fields

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_it_casual = fields.Boolean(string='Is it casual?')
    employee_type_stages_probation = fields.Boolean(string='Probation')
    employee_type_stages_regular =  fields.Boolean(string='Regular')
    employee_type_stages_notice_period = fields.Boolean(string='Notice Period')


