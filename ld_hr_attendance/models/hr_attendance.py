# -*- coding: utf-8 -*-
import math
from odoo import api, models, fields
from pytz import timezone


class HrAttendanceInhe(models.Model):
    _inherit = "hr.attendance"

    attendance_status = fields.Selection([
        ('present', 'Present'), ('absent', 'Absent'),
        ('onleave', 'On-Leave'), ('halfday', 'Half-Day')],
        string='Status', compute='_compute_att_status', store=True)

    check_in_date = fields.Date(compute='_compute_check_in', store=True)

    @api.depends('check_in')
    def _compute_check_in(self):
        for rec in self:
            rec.check_in_date = rec.check_in.date()

    @api.depends('check_in')
    def _compute_att_status(self):
        self._compute_check_in()
        grace_time = int(self.env['ir.config_parameter'].sudo().get_param('ld_hr_attendance.grace_time'))
        for rec in self:
            if rec.check_in:
                that_day_attendances = self.env["hr.attendance"].search([('check_in_date', '=', rec.check_in_date),
                                                    ('employee_id', '=', rec.employee_id.id)]).\
                                       sorted(key=lambda r: r.check_in)
                if not that_day_attendances:
                    rec.attendance_status = 'present'
                    continue
                that_day_first_attendance = that_day_attendances[0]
                emp_check_in_day = that_day_first_attendance.check_in.weekday()
                emp_actual_check_in_time = that_day_first_attendance.check_in
                emp_actual_check_in_time_ist = emp_actual_check_in_time.astimezone(\
                    timezone(self.env.context.get('tz') or 'Asia/Kolkata'))
                attendance_ids = rec.employee_id.resource_calendar_id.attendance_ids
                attendance_id = attendance_ids.filtered(lambda act: act.dayofweek == str(emp_check_in_day)
                                                        and act.day_period == 'morning')
                if not attendance_id:
                    rec.attendance_status = 'present'
                    continue
                frac, whole = math.modf(attendance_id.hour_from)
                that_day_checkin_should_be = emp_actual_check_in_time_ist.replace(hour=int(whole), minute=int(frac), second=0)
                if emp_actual_check_in_time_ist > that_day_checkin_should_be:
                    late_time = emp_actual_check_in_time_ist - that_day_checkin_should_be
                    late_time_seconds = late_time.total_seconds()
                    late_time_minutes = (late_time_seconds % 3600) // 60
                    if late_time_minutes > grace_time:
                        that_day_attendances.attendance_status = 'halfday'
                    else:
                        rec.attendance_status = 'present'
                else:
                    rec.attendance_status = 'present'
            else:
                rec.attendance_status = 'present'
