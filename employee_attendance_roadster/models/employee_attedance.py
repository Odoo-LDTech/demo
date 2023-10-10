# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date


class EmployeeAttendance(models.Model):
    _name = 'employee.attendance.report'

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True,
                                  ondelete='cascade')
    shift_type = fields.Char(string='Shift Name', default='Regular')
    shift_in_time = fields.Char(string='Shift in time')
    shift_out_time = fields.Char(string='Shift out time')
    check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', )
    today_date_atte = fields.Date(string="Date")
    biomatric_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ], string='Biomatric Status',
        help="This is show status of biometric attendance")
    payroll_status = fields.Selection([
        ('od', 'od'),
        ('reg', 'Regular'),
        ('abs', 'Abs'),
        ('esi', 'Esi'),
        ('suspend', 'Suspend'),
        ('leave', 'Leave'),
        ('halfday', 'Halfday-ABS'),
        ('weekoff', 'WeekOff'),
        ('holiday', 'Holiday'),
    ], string='Payroll Status')
    shift_status = fields.Selection([
        ('working_day', 'Working Day'),
        ('holiday', 'Holiday'),
        ('weekoff', 'Weekoff'),
    ], string='Shift Status', )

    def create_employee_attendance(self):
        today = date.today()
        # today = datetime.date(2022, 12, 25)
        week_day = today.weekday()
        employee_records = self.env['hr.employee'].search([ ])
        for i in employee_records:
            week_days = []
            [week_days.append(week.dayofweek) if week.dayofweek not in week_days else None for week in
             i.resource_calendar_id.attendance_ids]
            attendance_record = self.env['hr.attendance'].search([('employee_id', '=', i.id)]).filtered(lambda
                                                                                                            x: x.check_in.month == today.month and x.check_in.day == today.day and x.check_in.year == today.year)
            shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
                lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
            shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
                lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
            if attendance_record:
                if attendance_record.worked_hours > 6.0:
                    self.env['employee.attendance.report'].create({
                        'employee_id': i.id,
                        'shift_type': i.resource_calendar_id.name,
                        'shift_in_time': shift_in_time.hour_from,
                        'shift_out_time': shift_out_time.hour_to,
                        'check_in': attendance_record.check_in,
                        'check_out': attendance_record.check_out,
                        'worked_hours': round(attendance_record.worked_hours, 1),
                        'biomatric_status': 'present',
                        'payroll_status': 'reg',
                        'shift_status': 'working_day',
                        'today_date_atte': today,

                    })
                if (attendance_record.worked_hours == 4.0) or attendance_record.worked_hours > 4.0:
                    shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
                        lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
                    shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
                        lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
                    if attendance_record.worked_hours < 6.0:
                        self.env['employee.attendance.report'].create({
                            'employee_id': i.id,
                            'shift_type': i.resource_calendar_id.name,
                            'shift_in_time': shift_in_time.hour_from,
                            'shift_out_time': shift_out_time.hour_to,
                            'check_in': attendance_record.check_in,
                            'check_out': attendance_record.check_out,
                            'worked_hours': round(attendance_record.worked_hours, 1),
                            'biomatric_status': 'present',
                            'payroll_status': 'halfday',
                            'shift_status': 'working_day',
                            'today_date_atte': today,

                        })
                if attendance_record.worked_hours < 4.0:
                    shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
                        lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
                    shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
                        lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
                    self.env['employee.attendance.report'].create({
                        'employee_id': i.id,
                        'shift_type': i.resource_calendar_id.name,
                        'shift_in_time': shift_in_time.hour_from,
                        'shift_out_time': shift_out_time.hour_to,
                        'check_in': attendance_record.check_in,
                        'check_out': attendance_record.check_out,
                        'worked_hours': round(attendance_record.worked_hours, 1),
                        'biomatric_status': 'absent',
                        'payroll_status': 'abs',
                        'shift_status': 'working_day',
                        'today_date_atte': today,

                    })
            if not attendance_record:
                shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
                    lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
                shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
                    lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
                leave_record = self.env['hr.leave'].search([('employee_id', '=', i.id)]).filtered(lambda
                                                                                                      x: x.request_date_from.day == today.day and x.request_date_from.month == today.month and x.request_date_from.year == today.year)
                for leaves in leave_record:
                    if (
                            leaves.request_date_to.day == today.day and leaves.request_date_to.month == today.month and leaves.request_date_to.year == today.year):
                        self.env['employee.attendance.report'].create({
                            'employee_id': i.id,
                            'shift_type': i.resource_calendar_id.name,
                            'shift_in_time': shift_in_time.hour_from,
                            'shift_out_time': shift_out_time.hour_to,
                            'worked_hours': 0.0,
                            'biomatric_status': 'absent',
                            'payroll_status': 'leave',
                            'shift_status': 'working_day',
                            'today_date_atte': today,

                        })
                    if (leaves.request_date_to.month == today.month and leaves.request_date_to.year == today.year):
                        var1 = str(leaves.request_date_from.day)
                        var2 = str(leaves.request_date_to.day)
                        for l in range(int(var1), int(var2), 1):
                            if l == today.day:
                                self.env['employee.attendance.report'].create({
                                    'employee_id': i.id,
                                    'shift_type': i.resource_calendar_id.name,
                                    'shift_in_time': shift_in_time.hour_from,
                                    'shift_out_time': shift_out_time.hour_to,
                                    'worked_hours': 0.0,
                                    'biomatric_status': 'absent',
                                    'payroll_status': 'leave',
                                    'shift_status': 'working_day',
                                    'today_date_atte': today,

                                })

                public_holiday = i.resource_calendar_id.global_leave_ids.filtered(lambda
                                                                                      x: x.date_from.day == today.day and x.date_from.month == today.month and x.date_from.year == today.year and x.date_to.day == today.day and x.date_to.month == today.month and x.date_to.year == today.year)
                if public_holiday:
                    self.env['employee.attendance.report'].create({
                        'employee_id': i.id,
                        'shift_type': i.resource_calendar_id.name,
                        'shift_in_time': shift_in_time.hour_from,
                        'shift_out_time': shift_out_time.hour_to,
                        'worked_hours': 0.0,
                        'biomatric_status': 'absent',
                        'payroll_status': 'holiday',
                        'shift_status': 'holiday',
                        'today_date_atte': today,

                    })
                if not str(week_day) in week_days:
                    self.env['employee.attendance.report'].create({
                        'employee_id': i.id,
                        'shift_type': i.resource_calendar_id.name,
                        'shift_in_time': shift_in_time.hour_from,
                        'shift_out_time': shift_out_time.hour_to,
                        'worked_hours': 0.0,
                        'biomatric_status': 'absent',
                        'payroll_status': 'weekoff',
                        'shift_status': 'weekoff',
                        'today_date_atte': today,

                    })

                if not (public_holiday or leave_record):
                    if str(week_day) in week_days:
                        self.env['employee.attendance.report'].create({
                            'employee_id': i.id,
                            'shift_type': i.resource_calendar_id.name,
                            'shift_in_time': shift_in_time.hour_from,
                            'shift_out_time': shift_out_time.hour_to,
                            'worked_hours': 0.0,
                            'biomatric_status': 'absent',
                            'payroll_status': 'abs',
                            'shift_status': 'working_day',
                            'today_date_atte': today,

                        })


# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     def create_employee_attendance(self):
#         today1 = date.today()
#         today = today1.replace(year=2023, month=3, day=31)
#         # today = datetime.date(2022, 12, 25)
#         week_day = today.weekday()
#         employee_records = self.env['hr.employee'].search([('id', '=', 210)])
#         for i in employee_records:
#             week_days = []
#             [week_days.append(week.dayofweek) if week.dayofweek not in week_days else None for week in
#              i.resource_calendar_id.attendance_ids]
#             attendance_record = self.env['hr.attendance'].search([('employee_id', '=', i.id)]).filtered(lambda
#                                                                                                             x: x.check_in.month == today.month and x.check_in.day == today.day and x.check_in.year == today.year)
#             shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
#                 lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
#             shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
#                 lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
#             if attendance_record:
#                 if attendance_record.worked_hours > 6.0:
#                     self.env['employee.attendance.report'].create({
#                         'employee_id': i.id,
#                         'shift_type': i.resource_calendar_id.name,
#                         'shift_in_time': shift_in_time.hour_from,
#                         'shift_out_time': shift_out_time.hour_to,
#                         'check_in': attendance_record.check_in,
#                         'check_out': attendance_record.check_out,
#                         'worked_hours': round(attendance_record.worked_hours, 1),
#                         'biomatric_status': 'present',
#                         'payroll_status': 'reg',
#                         'shift_status': 'working_day',
#                         'today_date_atte': today,
#
#                     })
#                 if (attendance_record.worked_hours == 4.0) or attendance_record.worked_hours > 4.0:
#                     shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
#                         lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
#                     shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
#                         lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
#                     if attendance_record.worked_hours < 6.0:
#                         self.env['employee.attendance.report'].create({
#                             'employee_id': i.id,
#                             'shift_type': i.resource_calendar_id.name,
#                             'shift_in_time': shift_in_time.hour_from,
#                             'shift_out_time': shift_out_time.hour_to,
#                             'check_in': attendance_record.check_in,
#                             'check_out': attendance_record.check_out,
#                             'worked_hours': round(attendance_record.worked_hours, 1),
#                             'biomatric_status': 'present',
#                             'payroll_status': 'halfday',
#                             'shift_status': 'working_day',
#                             'today_date_atte': today,
#
#                         })
#                 if attendance_record.worked_hours < 4.0:
#                     shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
#                         lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
#                     shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
#                         lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
#                     self.env['employee.attendance.report'].create({
#                         'employee_id': i.id,
#                         'shift_type': i.resource_calendar_id.name,
#                         'shift_in_time': shift_in_time.hour_from,
#                         'shift_out_time': shift_out_time.hour_to,
#                         'check_in': attendance_record.check_in,
#                         'check_out': attendance_record.check_out,
#                         'worked_hours': round(attendance_record.worked_hours, 1),
#                         'biomatric_status': 'absent',
#                         'payroll_status': 'abs',
#                         'shift_status': 'working_day',
#                         'today_date_atte': today,
#
#                     })
#             if not attendance_record:
#                 shift_in_time = i.resource_calendar_id.attendance_ids.filtered(
#                     lambda x: x.day_period == 'morning' and x.dayofweek == str(week_day))
#                 shift_out_time = i.resource_calendar_id.attendance_ids.filtered(
#                     lambda x: x.day_period == 'afternoon' and x.dayofweek == str(week_day))
#                 leave_record = self.env['hr.leave'].search([('employee_id', '=', i.id)]).filtered(lambda
#                                                                                                       x: x.request_date_from.day == today.day and x.request_date_from.month == today.month and x.request_date_from.year == today.year)
#                 for leaves in leave_record:
#                     if (
#                             leaves.request_date_to.day == today.day and leaves.request_date_to.month == today.month and leaves.request_date_to.year == today.year):
#                         self.env['employee.attendance.report'].create({
#                             'employee_id': i.id,
#                             'shift_type': i.resource_calendar_id.name,
#                             'shift_in_time': shift_in_time.hour_from,
#                             'shift_out_time': shift_out_time.hour_to,
#                             'worked_hours': 0.0,
#                             'biomatric_status': 'absent',
#                             'payroll_status': 'leave',
#                             'shift_status': 'working_day',
#                             'today_date_atte': today,
#
#                         })
#                     if (leaves.request_date_to.month == today.month and leaves.request_date_to.year == today.year):
#                         var1 = str(leaves.request_date_from.day)
#                         var2 = str(leaves.request_date_to.day)
#                         for l in range(int(var1), int(var2), 1):
#                             if l == today.day:
#                                 self.env['employee.attendance.report'].create({
#                                     'employee_id': i.id,
#                                     'shift_type': i.resource_calendar_id.name,
#                                     'shift_in_time': shift_in_time.hour_from,
#                                     'shift_out_time': shift_out_time.hour_to,
#                                     'worked_hours': 0.0,
#                                     'biomatric_status': 'absent',
#                                     'payroll_status': 'leave',
#                                     'shift_status': 'working_day',
#                                     'today_date_atte': today,
#
#                                 })
#
#                 public_holiday = i.resource_calendar_id.global_leave_ids.filtered(lambda
#                                                                                       x: x.date_from.day == today.day and x.date_from.month == today.month and x.date_from.year == today.year and x.date_to.day == today.day and x.date_to.month == today.month and x.date_to.year == today.year)
#                 if public_holiday:
#                     self.env['employee.attendance.report'].create({
#                         'employee_id': i.id,
#                         'shift_type': i.resource_calendar_id.name,
#                         'shift_in_time': shift_in_time.hour_from,
#                         'shift_out_time': shift_out_time.hour_to,
#                         'worked_hours': 0.0,
#                         'biomatric_status': 'absent',
#                         'payroll_status': 'holiday',
#                         'shift_status': 'holiday',
#                         'today_date_atte': today,
#
#                     })
#                 if not str(week_day) in week_days:
#                     self.env['employee.attendance.report'].create({
#                         'employee_id': i.id,
#                         'shift_type': i.resource_calendar_id.name,
#                         'shift_in_time': shift_in_time.hour_from,
#                         'shift_out_time': shift_out_time.hour_to,
#                         'worked_hours': 0.0,
#                         'biomatric_status': 'absent',
#                         'payroll_status': 'weekoff',
#                         'shift_status': 'weekoff',
#                         'today_date_atte': today,
#
#                     })
#
#                 if not (public_holiday or leave_record):
#                     if str(week_day) in week_days:
#                         self.env['employee.attendance.report'].create({
#                             'employee_id': i.id,
#                             'shift_type': i.resource_calendar_id.name,
#                             'shift_in_time': shift_in_time.hour_from,
#                             'shift_out_time': shift_out_time.hour_to,
#                             'worked_hours': 0.0,
#                             'biomatric_status': 'absent',
#                             'payroll_status': 'abs',
#                             'shift_status': 'working_day',
#                             'today_date_atte': today,
#
#                         })
