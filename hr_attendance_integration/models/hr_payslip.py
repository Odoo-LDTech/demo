# -*- coding:utf-8 -*-

import babel
from collections import defaultdict
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from pytz import utc

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
from calendar import monthrange


# This will generate 16th of days
ROUNDING_FACTOR = 16


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        if res and res[-1]['code'] == 'WORK100':
            res.clear()
        day_from = date_from
        date_to = date_to
        employee_id = contracts.employee_id
        contract = contracts
        employee_attendance = len(self.env['employee.attendance.report'].search(
            [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                 a: a.today_date_atte.month == day_from.month and a.today_date_atte.year == day_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month
                                                                    and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)
        if employee_attendance < 1:
            contract = contracts
            zero_missing_attendances = {
                'name': _("Missing Attendance days"),
                'sequence': 1,
                'code': 'MISSATTE ',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            zero_regular_attendances = {
                'name': _("Regular Attendance days"),
                'sequence': 1,
                'code': 'REGA ',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            zero_onduty_attendances = {
                'name': _("OnDuty Attendance days"),
                'sequence': 1,
                'code': 'ONDA ',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            zero_esi_attendances = {
                'name': _("ESI Attendance days"),
                'sequence': 1,
                'code': 'ESIA ',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            zero_weekoff_attendances = {
                'name': _("WeekOff  days"),
                'sequence': 1,
                'code': 'WEO',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            zero_public_attendances = {
                'name': _("Public  days"),
                'sequence': 1,
                'code': 'PUBD',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            zero_leave_attendances = {
                'name': _("Leave  days"),
                'sequence': 1,
                'code': 'LEAD',
                'number_of_days': 0.00,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            res.append(zero_regular_attendances)
            res.append(zero_esi_attendances)
            res.append(zero_onduty_attendances)
            res.append(zero_weekoff_attendances)
            res.append(zero_public_attendances)
            res.append(zero_leave_attendances)
            res.append(zero_missing_attendances)
        if employee_attendance >= 1:
            employee_attendance_regular = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == day_from.month and a.today_date_atte.year == day_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'reg'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_half_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'halfday'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_public_holiday_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'holiday'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_on_duty_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'od'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_weekoff_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'weekoff'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_leave_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'leave'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_esi_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'esi'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_missing_attendance = len(self.env['employee.attendance.report'].search(
                [('employee_id', '=', employee_id.id)]).filtered(lambda
                                                                     a: a.today_date_atte.month == date_from.month and a.today_date_atte.year == date_from.year and a.today_date_atte.year == date_to.year and a.today_date_atte.month == date_to.month and a.payroll_status in [
                'abs',
                'suspend'] and a.today_date_atte.day >= day_from.day and a.today_date_atte.day <= date_to.day).ids)

            employee_missing_attendance += employee_half_attendance / 2

            missing_attendances = {
                'name': _("Missing Attendance days"),
                'sequence': 1,
                'code': 'MISSATTE ',
                'number_of_days': employee_missing_attendance,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            regular_attendances = {
                'name': _("Regular Attendance days"),
                'sequence': 1,
                'code': 'REGA ',
                'number_of_days': employee_attendance_regular + employee_half_attendance / 2,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            onduty_attendances = {
                'name': _("OnDuty Attendance days"),
                'sequence': 1,
                'code': 'ONDA ',
                'number_of_days': employee_on_duty_attendance,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            esi_attendances = {
                'name': _("ESI Attendance days"),
                'sequence': 1,
                'code': 'ESIA ',
                'number_of_days': employee_esi_attendance,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            weekoff_attendances = {
                'name': _("WeekOff  days"),
                'sequence': 1,
                'code': 'WEO',
                'number_of_days': employee_weekoff_attendance,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            public_attendances = {
                'name': _("Public  days"),
                'sequence': 1,
                'code': 'PUBD',
                'number_of_days': employee_public_holiday_attendance,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            leave_attendances = {
                'name': _("Leave  days"),
                'sequence': 1,
                'code': 'LEAD',
                'number_of_days': employee_leave_attendance,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            res.append(regular_attendances)
            res.append(esi_attendances)
            res.append(onduty_attendances)
            res.append(weekoff_attendances)
            res.append(public_attendances)
            res.append(leave_attendances)
            res.append(missing_attendances)
            # print("leavesvalues",leaves.values()  )
            # res.extend(leaves.values())
        return res
