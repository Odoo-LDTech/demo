# -*- encoding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.tools.date_utils import start_of, end_of, add, subtract
from odoo.tools.misc import format_date


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    schedule_count = fields.Integer('Schedules', compute='_compute_schedule_count')

    def _compute_schedule_count(self):
        domain = [
            '|',
                ('product_id.bom_line_ids.bom_id', 'in', self.ids),
                '|',
                    ('product_id', 'in', self.product_id.ids),
                    ('product_id.product_tmpl_id', 'in', self.product_tmpl_id.ids),
        ]
        grouped_data = self.env['mrp.production.schedule'].read_group(
            domain, ['product_id'], ['product_id'])
        product_schedule_counts = {}
        for data in grouped_data:
            product_schedule_counts[data['product_id'][0]] = data['product_id_count']
        for bom in self:
            schedule_count = 0
            if bom.product_id:
                ids = bom.product_id.ids
            else:
                ids = bom.product_tmpl_id.product_variant_ids.ids
            for product_id in bom.bom_line_ids.product_id.ids + ids:
                schedule_count += product_schedule_counts.get(product_id, 0)
            bom.schedule_count = schedule_count


class ProductProduct(models.Model):
    _inherit = 'product.product'

    schedule_count = fields.Integer('Schedules', compute='_compute_schedule_count')

    def _compute_schedule_count(self):
        grouped_data = self.env['mrp.production.schedule'].read_group(
            [('product_id', 'in', self.ids)], ['product_id'], ['product_id'])
        schedule_counts = {}
        for data in grouped_data:
            schedule_counts[data['product_id'][0]] = data['product_id_count']
        for product in self:
            product.schedule_count = schedule_counts.get(product.id, 0)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    schedule_count = fields.Integer('Schedules', compute='_compute_schedule_count')

    def _compute_schedule_count(self):
        grouped_data = self.env['mrp.production.schedule'].read_group(
            [('product_id.product_tmpl_id', 'in', self.ids)], ['product_id'], ['product_id'])
        product_schedule_counts = {}
        for data in grouped_data:
            product_schedule_counts[data['product_id'][0]] = data['product_id_count']
        for template in self:
            schedule_count = 0
            for product_id in template.product_variant_ids.ids:
                schedule_count += product_schedule_counts.get(product_id, 0)
            template.schedule_count = schedule_count

    def action_open_mps_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mrp_mps.action_mrp_mps")
        action['domain'] = [('product_id.product_tmpl_id', 'in', self.ids)]
        return action


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_planned_mps = fields.Datetime(string='Scheduled Date', compute='_compute_date_planned_mps', store=True, index=True)

    @api.depends('order_line.date_planned', 'date_order')
    def _compute_date_planned_mps(self):
        for order in self:
            min_date = False
            for line in order.order_line:
                if not min_date or line.date_planned and line.date_planned < min_date:
                    min_date = line.date_planned
            # since we only care about the date, remove time part so that when search based on a date we can also match it
            if min_date:
                order.date_planned_mps = min_date.date()
            else:
                order.date_planned_mps = order.date_order.date()


class Company(models.Model):
    _inherit = "res.company"

    manufacturing_period = fields.Selection([
        ('month', 'Monthly'),
        ('week', 'Weekly'),
        ('day', 'Daily')], string="Manufacturing Period",
        default='month', required=True,
        help="Default value for the time ranges in Master Production Schedule report.")

    manufacturing_period_to_display = fields.Integer('Number of columns for the\
        given period to display in Master Production Schedule', default=12)
    mrp_mps_show_starting_inventory = fields.Boolean(
        'Display Starting Inventory', default=True)
    mrp_mps_show_demand_forecast = fields.Boolean(
        'Display Demand Forecast', default=True)
    mrp_mps_show_actual_demand = fields.Boolean(
        'Display Actual Demand', default=False)
    mrp_mps_show_indirect_demand = fields.Boolean(
        'Display Indirect Demand', default=True)
    mrp_mps_show_to_replenish = fields.Boolean(
        'Display To Replenish', default=True)
    mrp_mps_show_actual_replenishment = fields.Boolean(
        'Display Actual Replenishment', default=False)
    mrp_mps_show_safety_stock = fields.Boolean(
        'Display Safety Stock', default=True)
    mrp_mps_show_available_to_promise = fields.Boolean(
        'Display Available to Promise', default=False)
    mrp_mps_show_actual_demand_year_minus_1 = fields.Boolean(
        'Display Actual Demand Last Year', default=False)
    mrp_mps_show_actual_demand_year_minus_2 = fields.Boolean(
        'Display Actual Demand Before Year', default=False)

    def _get_date_range(self, years=False):
        """ Return the date range for a production schedude depending the
        manufacturing period and the number of columns to display specify by the
        user. It returns a list of tuple that contains the timestamp for each
        column.
        """
        self.ensure_one()
        date_range = []
        if not years:
            years = 0
        first_day = start_of(subtract(fields.Date.today(), years=years),
                             self.manufacturing_period)
        for columns in range(self.manufacturing_period_to_display):
            last_day = end_of(first_day, self.manufacturing_period)
            date_range.append((first_day, last_day))
            first_day = add(last_day, days=1)
        return date_range

    def _date_range_to_str(self):
        date_range = self._get_date_range()
        dates_as_str = []
        lang = self.env.context.get('lang')
        for date_start, date_stop in date_range:
            if self.manufacturing_period == 'month':
                dates_as_str.append(format_date(self.env, date_start, date_format='MMM yyyy'))
            elif self.manufacturing_period == 'week':
                dates_as_str.append(_('Week {week_num} ({start_date}-{end_date}/{month})').format(
                    week_num=format_date(self.env, date_start, date_format='w'),
                    start_date=format_date(self.env, date_start, date_format='d'),
                    end_date=format_date(self.env, date_stop, date_format='d'),
                    month=format_date(self.env, date_start, date_format='MMM')
                ))
            else:
                dates_as_str.append(format_date(self.env, date_start, date_format='MMM d'))
        return dates_as_str


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    manufacturing_period = fields.Selection(related="company_id.manufacturing_period", string="Manufacturing Period", readonly=False)
    manufacturing_period_to_display = fields.Integer(
        related='company_id.manufacturing_period_to_display',
        string='Number of Manufacturing Period Columns', readonly=False)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_get_domain(self, company_id, values, partner):
        """ Avoid to merge two RFQ for the same MPS replenish. """
        domain = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
        if self.env.context.get('skip_lead_time') and values.get('date_planned'):
            domain += (('date_planned_mps', '=', values['date_planned']),)
        return domain
