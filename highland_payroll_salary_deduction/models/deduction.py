import io
import xlsxwriter
import xlwt
import base64
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api
from odoo.http import request


class PayslipReport(models.TransientModel):
    _name = "monthly.pf.report.wizard"

    name = fields.Char('File Name', size=32)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    deduction_state = fields.Selection([('esi', 'ESI'),('vpf', 'VPF'), ('pf', 'PF'),('professional_tax', 'Professional Tax'), ('income_tax', 'Income Tax',)], required=True)
    employee_id = fields.Many2many('hr.employee', string='Employee')
    report = fields.Binary('Download', filters='.xls', readonly=True)
    all_employee = fields.Boolean(string='All Employee')
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')


    def generate_deduction_report(self):
        for rec in self:
            amount = 0.0
            res_list = [ ]
            if rec.deduction_state == 'esi':
                if rec.employee_id:
                    var = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id)]).filtered(lambda x : x.date_from.month == self.date_from.month and  x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and  x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x : x.code == 'ESIC'):
                        # if not res_list.get('name') == i.slip_id.employee_id.name and res_list('code') == i.slip_id.employee_id.employee_id:
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
                if rec.all_employee:
                    var = self.env['hr.payslip'].search([ ]).filtered(lambda x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x: x.code == 'ESIC'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
            if rec.deduction_state == 'vpf':
                if rec.employee_id:
                    var = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id)]).filtered(lambda x : x.date_from.month == self.date_from.month and  x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and  x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x : x.code == 'VPF'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
                if rec.all_employee:
                    var = self.env['hr.payslip'].search([ ]).filtered(lambda x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x: x.code == 'VPF'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })


            if rec.deduction_state == 'pf':
                if rec.employee_id:
                    var = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]).filtered(lambda x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x : x.code == 'PF'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
                if rec.all_employee:
                    var = self.env['hr.payslip'].search([ ]).filtered(lambda
                                                                            x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)

                    for i in var.line_ids.filtered(lambda x: x.code == 'PF'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                        'Payslip_Name': i.slip_id.number,
                                        'amount': i.total,
                                         })

            if rec.deduction_state == 'professional_tax' :
                if rec.employee_id:
                    var = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]).filtered(lambda
                                                                                                                          x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x : x.code == 'PT'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
                if rec.all_employee:
                    var = self.env['hr.payslip'].search([ ]).filtered(lambda
                                                                            x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)

                    for i in var.line_ids.filtered(lambda x: x.code == 'PT'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
            if rec.deduction_state == 'income_tax' :
                if rec.employee_id:
                    var = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id)]).filtered(lambda x : x.date_from.month == self.date_from.month and  x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and  x.date_to.year == self.date_to.year)
                    for i in var.line_ids.filtered(lambda x : x.code == 'INT'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })
                if rec.all_employee:
                    var = self.env['hr.payslip'].search([ ]).filtered(lambda
                                                                            x: x.date_from.month == self.date_from.month and x.date_to.month == self.date_to.month and x.date_from.year == self.date_from.year and x.date_to.year == self.date_to.year)

                    for i in var.line_ids.filtered(lambda x: x.code == 'INT'):
                        res_list.append({'name': i.slip_id.employee_id.name,
                                         'Code': i.slip_id.employee_id.employee_id,
                                         'from_date': i.slip_id.date_from.strftime("%m/%d/%Y"),
                                         'to_date': i.slip_id.date_to.strftime("%m/%d/%Y"),
                                         'Payable_Days': i.payable_days,
                                         'Payslip_Name': i.slip_id.number,
                                         'amount': i.total,
                                         })

            employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)]).name
            context = self.env.context
            wb1 = xlwt.Workbook(encoding='utf-8')
            ws1 = wb1.add_sheet('Download deduction report')
            fp = BytesIO()
            header_content_style = xlwt.easyxf('font: name Times size 30 px, bold 1, height 300')
            sub_header_style = xlwt.easyxf('font: name Times size 40 px, bold 1, height 500')
            sub_header_content_style = xlwt.easyxf("font: name Times size 20 px, height 300")
            row = 0
            col = 0
            ws1.col(0).width = 256 * 40
            ws1.col(1).width = 256 * 20
            ws1.col(2).width = 256 * 20
            ws1.col(3).width = 256 * 30
            ws1.col(4).width = 256 * 40
            ws1.col(5).width = 256 * 40
            ws1.col(6).width = 256 * 30
            ws1.write(row, col, "Name", sub_header_style)
            ws1.write(row , col + 1,"Code" , sub_header_style)
            ws1.write(row, col + 2, "Payable_Days", sub_header_style)
            ws1.write(row, col + 3, "Payslip_Name", sub_header_style)
            ws1.write(row, col + 4,"From_Date" , sub_header_style)
            ws1.write(row, col + 5, "To_Date", sub_header_style)
            ws1.write(row, col + 6, self.deduction_state , sub_header_style)
            row+=1
            if rec.employee_id:
                for row_list in res_list:
                    ws1.write(row, col,row_list.get('name') )
                    ws1.write(row, col + 1,row_list.get('Code')  )
                    ws1.write(row, col + 2, row_list.get('Payable_Days'))
                    ws1.write(row, col + 3, row_list.get('Payslip_Name'))
                    ws1.write(row, col + 4, row_list.get('from_date'))
                    ws1.write(row, col + 5, row_list.get('to_date'))
                    ws1.write(row, col + 6, row_list.get('amount'))
            if rec.all_employee:
                for row_list in res_list:
                    ws1.write(row, col,row_list.get('name') )
                    ws1.write(row, col + 1,row_list.get('Code')  )
                    ws1.write(row, col + 2, row_list.get('Payable_Days'))
                    ws1.write(row, col + 3, row_list.get('Payslip_Name'))
                    ws1.write(row, col + 4, row_list.get('from_date'))
                    ws1.write(row, col + 5, row_list.get('to_date'))
                    ws1.write(row, col + 6, row_list.get('amount'))

                    row+=1
            wb1.save(fp)
            context = {}
            out = base64.encodebytes(fp.getvalue())
            context['name'] = 'deduction_report.xls'
            context['file'] = out
            self.write({'state': 'get','report': out, 'name': 'deduction_report.xls'})

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'monthly.pf.report.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
