# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class SlackChannelDailyReport(models.Model):
    _name = 'slack.channel.daily.report'

    def convert_amount_to_monetary_field(self, amount_untaxed):
        options = {
            'display_currency': self.env.user.company_id.currency_id
        }        
        amount_untaxed_monetary = self.env['ir.qweb.field.monetary'].value_to_html(amount_untaxed, options)        
        amount_untaxed_monetary = amount_untaxed_monetary.replace('<span class="oe_currency_value">', '')
        amount_untaxed_monetary = amount_untaxed_monetary.replace('</span>', '')
        return amount_untaxed_monetary

    def res_partner_filter(self, ar_qt_activity_type, ar_qt_customer_type, create_date_start=False, create_date_end=False):        
        search_filters_res_partner = [
            ('active', '=', True),
            ('type', '=', 'contact'),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('ar_qt_customer_type', '=', ar_qt_customer_type)
        ]
        if create_date_start!=False:
            create_date_start_filter = create_date_start.strftime("%Y-%m-%d")+' 00:00:00'
            search_filters_res_partner.append(('create_date', '>=', create_date_start_filter))
            
        if create_date_end!=False:
            create_date_end_filter = create_date_end.strftime("%Y-%m-%d")+' 23:59:59'
            search_filters_res_partner.append(('create_date', '<=', create_date_end_filter))            
        
        return self.env['res.partner'].search(search_filters_res_partner)

    def res_partner_prof_with_sale_orders(self, ar_qt_activity_type, ar_qt_customer_type, create_date_start=False, create_date_end=False, confirmation_date_start=False, confirmation_date_end=False):
        total_partners_before = 0
        total_partners_after = 0
                
        res_partner_ids_get = []
        res_partner_ids = self.res_partner_filter(ar_qt_activity_type, ar_qt_customer_type, create_date_start, create_date_end)
        if len(res_partner_ids)>0:
            for res_partner_id in res_partner_ids:
                res_partner_ids_get.append(res_partner_id.id)
            
            total_partners_before = len(res_partner_ids_get)
            
            search_filters_sale_order = [
                ('state', 'in', ('sale', 'done')),
                ('claim', '=', False),
                ('partner_id', 'in', res_partner_ids_get), 
                ('amount_total', '>', 0)
            ]     
            if confirmation_date_start!=False:
                search_filters_sale_order.append(('confirmation_date', '>=', confirmation_date_start.strftime("%Y-%m-%d")))
                
            if confirmation_date_end!=False:
                search_filters_sale_order.append(('confirmation_date', '<=', confirmation_date_end.strftime("%Y-%m-%d")))
                
            sale_order_ids = self.env['sale.order'].search(search_filters_sale_order)
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:
                    if sale_order_id.partner_id.id in res_partner_ids_get:
                        res_partner_ids_get.remove(sale_order_id.partner_id.id)
            
            total_partners_after = len(res_partner_ids_get)
            
        total_with_sale_orders = total_partners_before-total_partners_after                              
        return total_with_sale_orders                
    
    def account_invoice_filter(self, ar_qt_activity_type, ar_qt_customer_type, date_invoice):
        account_invoice = {
            'total': 0,
            'amount_untaxed': 0
        }        
        account_invoice_ids = self.env['account.invoice'].search(
            [
                ('state', '!=', 'draft'),
                ('type', '=', 'out_invoice'),
                ('ar_qt_activity_type', '=', ar_qt_activity_type),
                ('ar_qt_customer_type', '=', ar_qt_customer_type),
                ('date_invoice', '=', date_invoice.strftime("%Y-%m-%d"))
            ]
        )
        if len(account_invoice_ids)>0:
            account_invoice['total'] = len(account_invoice_ids)
            for account_invoice_id in account_invoice_ids:
                account_invoice['amount_untaxed'] += account_invoice_id.amount_untaxed
                
        return account_invoice
        
    def sale_orders_filter(self, ar_qt_activity_type, ar_qt_customer_type, confirmation_date_start, confirmation_date_end):
        sale_order = {
            'total': 0,
            'amount_untaxed': 0
        }        
        search_filters = [
            ('state', 'in', ('sale', 'done')),
            ('claim', '=', False),
            ('ar_qt_activity_type', '=', ar_qt_activity_type), 
            ('amount_total', '>', 0),
            ('confirmation_date', '>=', confirmation_date_start.strftime("%Y-%m-%d")),
            ('confirmation_date', '<=', confirmation_date_end.strftime("%Y-%m-%d"))
        ]
        if ar_qt_customer_type!=False:
            search_filters.append(('ar_qt_customer_type', '=', ar_qt_customer_type))
                        
        sale_order_ids = self.env['sale.order'].search(search_filters)
        if len(sale_order_ids)>0:
            sale_order['total'] = len(sale_order_ids)
            for sale_order_id in sale_order_ids:
                sale_order['amount_untaxed'] += sale_order_id.amount_untaxed
        
        return sale_order
        
    def sale_orders_filter_without_date_order_send_mail(self, ar_qt_activity_type, ar_qt_customer_type, date_order_start, date_order_end):
        search_filters = [
            ('state', 'not in', ('cancel', 'sale', 'done')),
            ('claim', '=', False),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('ar_qt_customer_type', '=', ar_qt_customer_type),
            ('user_id', '!=', False), 
            ('amount_total', '>', 0),
            ('date_order_send_mail', '=', False),
            ('date_order', '>=', date_order_start.strftime("%Y-%m-%d")+' 00:00:00'),
            ('date_order', '<=', date_order_end.strftime("%Y-%m-%d")+' 23:59:59')
        ]                                
        sale_order_ids = self.env['sale.order'].search(search_filters)
        return len(sale_order_ids)                
    
    def sale_orders_filter_date_order_send_mail(self, ar_qt_activity_type, ar_qt_customer_type, confirmation_date_start, confirmation_date_end):
        sale_order = {
            'total': 0,
            'amount_untaxed': 0
        }
        search_filters = [
            ('state', '!=', 'cancel'),
            ('claim', '=', False),
            ('ar_qt_activity_type', '=', ar_qt_activity_type), 
            ('amount_total', '>', 0),
            ('date_order_send_mail', '>=', confirmation_date_start.strftime("%Y-%m-%d")),
            ('date_order_send_mail', '<=', confirmation_date_end.strftime("%Y-%m-%d"))
        ]
        if ar_qt_customer_type!=False:
            search_filters.append(('ar_qt_customer_type', '=', ar_qt_customer_type))
                        
        sale_order_ids = self.env['sale.order'].search(search_filters)
        if len(sale_order_ids)>0:
            sale_order['total'] = len(sale_order_ids)
            for sale_order_id in sale_order_ids:
                sale_order['amount_untaxed'] += sale_order_id.amount_untaxed
        
        return sale_order
        
    def sale_orders_filter_date_order(self, ar_qt_activity_type, ar_qt_customer_type, date_order_start, date_order_end):
        sale_order = {
            'total': 0,
            'amount_untaxed': 0
        }
        search_filters = [
            ('state', 'in', ('sale', 'done')),
            ('claim', '=', False),
            ('ar_qt_activity_type', '=', ar_qt_activity_type), 
            ('amount_total', '>', 0),
            ('user_id', '!=', False),
            ('date_order', '>=', date_order_start.strftime("%Y-%m-%d")+' 00:00:00'),
            ('date_order', '<=', date_order_end.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        if ar_qt_customer_type!=False:
            search_filters.append(('ar_qt_customer_type', '=', ar_qt_customer_type))
                                
        sale_order_ids = self.env['sale.order'].search(search_filters)        
        if len(sale_order_ids)>0:
            sale_order['total'] = len(sale_order_ids)
            for sale_order_id in sale_order_ids:
                sale_order['amount_untaxed'] += sale_order_id.amount_untaxed
        
        return sale_order        
                                                                            
    def shipping_expedition_nacex_yesterday(self, ar_qt_activity_type, ar_qt_customer_type, date_start, date_end):
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('state', '!=', 'error'),
                ('ar_qt_activity_type', '=', ar_qt_activity_type),
                ('ar_qt_customer_type', '=', ar_qt_customer_type),
                ('carrier_id.carrier_type', '=', 'nacex'),                
                ('date', '>=', date_start.strftime("%Y-%m-%d")),
                ('date', '<=', date_end.strftime("%Y-%m-%d"))
            ]
        )
        return len(shipping_expedition_ids)
        
    def stock_picking_filter_management_date(self, ar_qt_activity_type, ar_qt_customer_type, date_start, date_end):
        stock_picking_ids = self.env['stock.picking'].search(
            [
                ('state', '=', 'done'),
                ('ar_qt_activity_type', '=', ar_qt_activity_type),
                ('ar_qt_customer_type', '=', ar_qt_customer_type),
                ('carrier_id.carrier_type', '!=', 'nacex'),
                ('picking_type_id.code', '=', 'outgoing'),                
                ('management_date', '>=', date_start.strftime("%Y-%m-%d")+' 00:00:00'),
                ('management_date', '<=', date_end.strftime("%Y-%m-%d")+' 23:59:59')
            ]
        )
        return len(stock_picking_ids)        
        
    def crm_lead_without_user_id(self, ar_qt_activity_type, ar_qt_customer_type, create_date_start, create_date_end):        
        search_filters = [
            ('active', '=', True),
            ('type', '=', "opportunity"),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('ar_qt_customer_type', '=', ar_qt_customer_type), 
            ('user_id', '=', False),
            ('create_date', '>=', create_date_start.strftime("%Y-%m-%d")+' 00:00:00'),
            ('create_date', '<=', create_date_end.strftime("%Y-%m-%d")+' 23:59:59')
        ]        
        crm_lead_ids = self.env['crm.lead'].search(search_filters)        
        return len(crm_lead_ids)        
        
    def calculate_increment(self, value, value_previous):
        increment = {
            'total': 0,
            'amount_untaxed': 0
        }
        if value['total']>0 or value_previous['total']>0:
            increment['total'] = value['total']-value_previous['total']
            
        if value['amount_untaxed']>0 or value_previous['amount_untaxed']>0:
            increment['amount_untaxed'] = value['amount_untaxed']-value_previous['amount_untaxed']            
            
        return increment

    def odoo_slack_channel_daily_report_prof(self):
        current_date = datetime.today()
        date_yesterday = current_date + relativedelta(days=-1)
        date_before_yesterday = date_yesterday + relativedelta(days=-1)
        
        date_end_last_twelve_months = current_date
        date_start_last_twelve_months = date_end_last_twelve_months + relativedelta(years=-1)
        
        ar_qt_activity_type_filter = ['todocesped', 'arelux']
        #account_invoice_yesterday_prof (1) (yesterday and before_yesterday)
        account_invoice_yesterday_prof = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            account_invoice_yesterday_prof[ar_qt_activity_type] = {
                'yesterday': self.account_invoice_filter(ar_qt_activity_type, 'profesional', date_yesterday),
                'before_yesterday': self.account_invoice_filter(ar_qt_activity_type, 'profesional', date_before_yesterday),
                'increment': 0
            }
            account_invoice_yesterday_prof[ar_qt_activity_type]['increment'] = self.calculate_increment(account_invoice_yesterday_prof[ar_qt_activity_type]['yesterday'], account_invoice_yesterday_prof[ar_qt_activity_type]['before_yesterday'])        
        #sale_order_yesterday (2) (yesterday and before_yesterday)
        sale_order_yesterday = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            sale_order_yesterday[ar_qt_activity_type] = {
                'yesterday': self.sale_orders_filter(ar_qt_activity_type, 'profesional', date_yesterday, date_yesterday),
                'before_yesterday': self.sale_orders_filter(ar_qt_activity_type, 'profesional', date_before_yesterday, date_before_yesterday),
                'increment': 0, 
            }
            sale_order_yesterday[ar_qt_activity_type]['increment'] = self.calculate_increment(sale_order_yesterday[ar_qt_activity_type]['yesterday'], sale_order_yesterday[ar_qt_activity_type]['before_yesterday'])                                                                                              
        #cartera_profesionales (3)
        catera_profesionales = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:        
            catera_profesionales[ar_qt_activity_type] = self.res_partner_prof_with_sale_orders(ar_qt_activity_type, 'profesional', False, False, False, False)
        #stock_picking_filter_management_date_yesterday_prof (3B) (yesterday and before_yesterday)            
        stock_picking_filter_management_date_yesterday_prof = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type] = {
                'yesterday': self.stock_picking_filter_management_date(ar_qt_activity_type, 'profesional', date_yesterday, date_yesterday),
                'before_yesterday': self.stock_picking_filter_management_date(ar_qt_activity_type, 'profesional', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment'] = stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['yesterday']-stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['before_yesterday']                                                                        
        #cartera_profesionales_sin_compra_last_year (4)
        cartera_profesionales_sin_compra_last_year = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            res_partner_ids = []
            res_partner_ids_get = self.res_partner_filter(ar_qt_activity_type, 'profesional', False, False)
            if len(res_partner_ids_get)>0:
                for res_partner_id_get in res_partner_ids_get:
                    res_partner_ids.append(res_partner_id_get.id)
                    
            sale_order_ids = self.env['sale.order'].search(
                [
                    ('amount_total', '>', 0),
                    ('claim', '=', False),
                    ('partner_id', 'in', res_partner_ids),
                    ('confirmation_date', '>=', date_start_last_twelve_months.strftime("%Y-%m-%d")),
                    ('confirmation_date', '<=', date_end_last_twelve_months.strftime("%Y-%m-%d"))
                ]
            )            
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:
                    if sale_order_id.partner_id.id in res_partner_ids:
                        res_partner_ids.remove(sale_order_id.partner_id.id)
                        
            cartera_profesionales_sin_compra_last_year[ar_qt_activity_type] = len(res_partner_ids)                                                                
        #cartera_profesionales_nuevos_sin_compra_create_date_yesterday (5) (yesterday and before_yesterday)
        cartera_profesionales_nuevos_sin_compra_create_date_yesterday = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type] = {
                'yesterday': 0,
                'before_yesterday': 0,
                'increment': 0
            }
            #yesterday        
            res_partner_ids = []
            res_partner_ids_get = self.res_partner_filter(ar_qt_activity_type, 'profesional', date_yesterday, date_yesterday)
            if len(res_partner_ids_get)>0:
                for res_partner_id_get in res_partner_ids_get:
                    res_partner_ids.append(res_partner_id_get.id)
                    
            sale_order_ids = self.env['sale.order'].search(
                [
                    ('amount_total', '>', 0),
                    ('claim', '=', False),
                    ('partner_id', 'in', res_partner_ids),
                    ('state', 'in', ('sale', 'done'))
                ]
            )
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:
                    if sale_order_id.partner_id.id in res_partner_ids:
                        res_partner_ids.remove(sale_order_id.partner_id.id)
            
            cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['yesterday'] = len(res_partner_ids)
            #before_yesterday        
            res_partner_ids = []
            res_partner_ids_get = self.res_partner_filter(ar_qt_activity_type, 'profesional', date_before_yesterday, date_before_yesterday)
            if len(res_partner_ids_get)>0:
                for res_partner_id_get in res_partner_ids_get:
                    res_partner_ids.append(res_partner_id_get.id)
                    
            sale_order_ids = self.env['sale.order'].search(
                [
                    ('amount_total', '>', 0),
                    ('claim', '=', False),
                    ('partner_id', 'in', res_partner_ids),
                    ('state', 'in', ('sale', 'done'))
                ]
            )
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:
                    if sale_order_id.partner_id.id in res_partner_ids:
                        res_partner_ids.remove(sale_order_id.partner_id.id)
            
            cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['before_yesterday'] = len(res_partner_ids)
            #increment
            if cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['yesterday']>0 or cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['before_yesterday']>0:
                cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment'] = cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['yesterday']-cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['before_yesterday']
        #cartera_profesionales_primera_compra_ayer (6)
        cartera_profesionales_primera_compra_ayer = {}   
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            cartera_profesionales_primera_compra_ayer[ar_qt_activity_type] = {
                'yesterday': 0,
                'before_yesterday': 0,
                'increment': 0
            }
            #yesterday
            res_partner_ids = []
            res_partner_ids_get = self.res_partner_filter(ar_qt_activity_type, 'profesional', False, False)
            if len(res_partner_ids_get)>0:
                for res_partner_id_get in res_partner_ids_get:
                    res_partner_ids.append(res_partner_id_get.id)
                    
            sale_order_ids = self.env['sale.order'].search(
                [
                    ('amount_total', '>', 0),
                    ('claim', '=', False),
                    ('partner_id', 'in', res_partner_ids),
                    ('state', 'in', ('sale', 'done'))
                ]
            )
            
            res_partner_ids_sale_order_yesterday = {}
            
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:                    
                    confirmation_date_check = sale_order_id.confirmation_date[:10]
                    if confirmation_date_check==date_yesterday:
                        if sale_order_id.partner_id.id not in res_partner_ids_sale_order_yesterday:
                            res_partner_ids_sale_order_yesterday[sale.order_id.partner_id.id] = 0
                            
                        res_partner_ids_sale_order_yesterday[sale.order_id.partner_id.id] += 1                                                                         
            
            cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['yesterday'] = len(res_partner_ids_sale_order_yesterday)
            #before_yesterday    
            res_partner_ids_sale_order_before_yesterday = {}
            
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:
                    confirmation_date_check = sale_order_id.confirmation_date[:10]
                    if confirmation_date_check==date_before_yesterday:
                        if sale_order_id.partner_id.id not in res_partner_ids_sale_order_before_yesterday:
                            res_partner_ids_sale_order_before_yesterday[sale.order_id.partner_id.id] = 0
                            
                        res_partner_ids_sale_order_before_yesterday[sale.order_id.partner_id.id] += 1                                                                         
            
            cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['before_yesterday'] = len(res_partner_ids_sale_order_before_yesterday)
            #increment
            if cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['yesterday']>0 or cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['before_yesterday']>0:
                cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment'] = cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['yesterday']-cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['before_yesterday']
        #slack_message
        #facturacion_dia (1)
        facturacion_dia_txt = {}
        facturacion_dia_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            facturacion_dia_color[ar_qt_activity_type] = '#fbff00'#Color yellow    
                                
            facturacion_dia_ar_qt_activity_type = self.convert_amount_to_monetary_field(account_invoice_yesterday_prof[ar_qt_activity_type]['yesterday']['amount_untaxed'])
            facturacion_dia_txt[ar_qt_activity_type] = str(facturacion_dia_ar_qt_activity_type)
            
            if account_invoice_yesterday_prof[ar_qt_activity_type]['increment']['amount_untaxed']!=0:                                
                facturacion_dia_ar_qt_activity_type_increment = self.convert_amount_to_monetary_field(account_invoice_yesterday_prof[ar_qt_activity_type]['increment']['amount_untaxed'])
                if "-" not in facturacion_dia_ar_qt_activity_type_increment: 
                    facturacion_dia_ar_qt_activity_type_increment = '+'+str(facturacion_dia_ar_qt_activity_type_increment)
                
                facturacion_dia_txt[ar_qt_activity_type] += ' ('+str(facturacion_dia_ar_qt_activity_type_increment)+')'
                
                facturacion_dia_color[ar_qt_activity_type] = '#36a64f'#Color green
                if "-" in facturacion_dia_ar_qt_activity_type_increment: 
                    facturacion_dia_color[ar_qt_activity_type] = '#ff0000'#Color red                                                                
        #numero_pedido_dia (2)
        numero_pedido_dia_txt = {}
        numero_pedido_dia_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            numero_pedido_dia_color[ar_qt_activity_type] = '#fbff00'#Color yellow
                            
            numero_pedido_dia_txt[ar_qt_activity_type] = str(sale_order_yesterday[ar_qt_activity_type]['yesterday']['total'])
            
            if sale_order_yesterday[ar_qt_activity_type]['increment']['total']!=0:
                if sale_order_yesterday[ar_qt_activity_type]['increment']['total']>0:
                    sale_order_yesterday[ar_qt_activity_type]['increment']['total'] = '+'+str(sale_order_yesterday[ar_qt_activity_type]['increment']['total'])
                
                numero_pedido_dia_txt[ar_qt_activity_type] += ' ('+str(sale_order_yesterday[ar_qt_activity_type]['increment']['total'])+')'
                
                numero_pedido_dia_color[ar_qt_activity_type] = '#36a64f'#Color green
                if sale_order_yesterday[ar_qt_activity_type]['increment']['total']<0:
                    numero_pedido_dia_color[ar_qt_activity_type] = '#ff0000'#Color green                
        #cartera_clientes_profesionales_activos (3)                
        cartera_clientes_profesionales_activos_txt = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            cartera_clientes_profesionales_activos_txt[ar_qt_activity_type] = str(catera_profesionales[ar_qt_activity_type])
        #numero_albaranes_hechos (3B)
        numero_albaranes_hechos_txt = {}
        numero_albaranes_hechos_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            numero_albaranes_hechos_color[ar_qt_activity_type] = ''
            numero_albaranes_hechos_txt[ar_qt_activity_type] = str(stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['yesterday'])
        
            if stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment']!=0:
                if stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment']>0:
                    stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment'] = '+'+str(stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment'])
                                    
                numero_albaranes_hechos_txt[ar_qt_activity_type] += ' ('+str(stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment'])+')'
                                
                numero_albaranes_hechos_color[ar_qt_activity_type] = '#36a64f'#Color green
                if stock_picking_filter_management_date_yesterday_prof[ar_qt_activity_type]['increment']<0:
                    numero_albaranes_hechos_color[ar_qt_activity_type] = '#ff0000'#Color red            
        #cartera_clientes_profesionales_sin_compra (4)                        
        cartera_clientes_profesionales_sin_compra_txt = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            cartera_clientes_profesionales_sin_compra_txt[ar_qt_activity_type] = str(cartera_profesionales_sin_compra_last_year[ar_qt_activity_type])        
        #clientes_profesionales_nuevos (5)            
        clientes_profesionales_nuevos_txt = {}
        clientes_profesionales_nuevos_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            clientes_profesionales_nuevos_color[ar_qt_activity_type] = "#fbff00"#Color yellow
            
            clientes_profesionales_nuevos_txt[ar_qt_activity_type] = str(cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['yesterday'])
            
            if cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment']!=0:
                if cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment']>0:
                    cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment'] = '+'+str(cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment'])
            
                clientes_profesionales_nuevos_txt[ar_qt_activity_type] += ' ('+str(cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment'])+')'
                
                clientes_profesionales_nuevos_color[ar_qt_activity_type] = '#36a64f'#Color green
                if cartera_profesionales_nuevos_sin_compra_create_date_yesterday[ar_qt_activity_type]['increment']<0:
                    clientes_profesionales_nuevos_color[ar_qt_activity_type] = '#ff0000'#Color green            
        #clientes_profesionales_con_primera_compra (6)
        clientes_profesionales_con_primera_compra_txt = {}
        clientes_profesionales_con_primera_compra_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            clientes_profesionales_con_primera_compra_color[ar_qt_activity_type] = "#fbff00"#Color yellow
            
            clientes_profesionales_con_primera_compra_txt[ar_qt_activity_type] = str(cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['yesterday'])
            
            if cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment']!=0:
                if cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment']>0:
                    cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment'] = '+'+str(cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment'])
                    
                clientes_profesionales_con_primera_compra_txt[ar_qt_activity_type] += ' ('+str(cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment'])+')'
                
                clientes_profesionales_con_primera_compra_color[ar_qt_activity_type] = '#36a64f'#Color green
                if cartera_profesionales_primera_compra_ayer[ar_qt_activity_type]['increment']<0:
                    clientes_profesionales_con_primera_compra_color[ar_qt_activity_type] = '#ff0000'#Color green
                                        
        attachments = [
            {   
                "text": '[Todocesped] Facturacion del dia: '+facturacion_dia_txt['todocesped'],
                "color": facturacion_dia_color['todocesped'],                                    
            },
            {
                "text": '[Arelux] Facturacion del dia: '+facturacion_dia_txt['arelux'],
                "color": facturacion_dia_color['todocesped'],                                    
            },
            {
                "text": '[Todocesped] Numero de pedidos del dia: '+numero_pedido_dia_txt['todocesped'],
                "color": numero_pedido_dia_color['todocesped'],                                    
            },
            {
                "text": '[Arelux] Numero de pedidos del dia: '+numero_pedido_dia_txt['arelux'],
                "color": numero_pedido_dia_color['arelux'],                                    
            },
            {
                "text": '[Todocesped] Cartera de clientes profesionales activos: '+cartera_clientes_profesionales_activos_txt['todocesped'],                                    
            },
            {
                "text": '[Arelux] Cartera de clientes profesionales activos: '+cartera_clientes_profesionales_activos_txt['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] Numero de albaranes hechos: '+numero_albaranes_hechos_txt['todocesped'],
                "color": numero_albaranes_hechos_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Numero de albaranes hechos: '+numero_albaranes_hechos_txt['arelux'],
                "color": numero_albaranes_hechos_color['arelux'],                                    
            },
            {
                "text": '[Todocesped] Cartera de clientes profesionales sin compra: '+cartera_clientes_profesionales_sin_compra_txt['todocesped'],                                    
            },
            {
                "text": '[Arelux] Cartera de clientes profesionales sin compra: '+cartera_clientes_profesionales_sin_compra_txt['arelux'],                                    
            },
            {
                "text": '[Todocesped] Clientes profesionales nuevos metidos al sistema: '+clientes_profesionales_nuevos_txt['todocesped'],
                "color": clientes_profesionales_nuevos_color['todocesped'],                                    
            },
            {
                "text": '[Arelux] Clientes profesionales nuevos metidos al sistema: '+clientes_profesionales_nuevos_txt['arelux'],
                "color": clientes_profesionales_nuevos_color['arelux'],                                    
            },
            {
                "text": '[Todocesped] Clientes profesionales con primera compra: '+clientes_profesionales_con_primera_compra_txt['todocesped'],
                "color": clientes_profesionales_con_primera_compra_color['todocesped'],                                    
            },
            {
                "text": '[Arelux] Clientes profesionales con primera compra: '+clientes_profesionales_con_primera_compra_txt['arelux'],
                "color": clientes_profesionales_con_primera_compra_color['arelux'],                                    
            }                                                           
        ]                                               
        slack_message_vals = {
            'attachments': attachments,
            'model': 'slack.channel.daily.report',
            'res_id': 0,
            'msg': '*Profesionales*',            
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_report_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                        
    
    def odoo_slack_channel_daily_report_part(self):
        current_date = datetime.today()
        date_yesterday = current_date + relativedelta(days=-1)
        date_before_yesterday = date_yesterday + relativedelta(days=-1)
        
        date_start_last_twelve_months = current_date
        date_end_last_twelve_months = date_start_last_twelve_months + relativedelta(years=-1)
        
        date_start_last_month = date_yesterday
        date_end_last_month = date_start_last_month + relativedelta(months=-1)
        
        ar_qt_activity_type_filter = ['todocesped', 'arelux']                                                         
        #account_invoice_yesterday_part (1) (yesterday and before_yesterday)
        account_invoice_yesterday_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            account_invoice_yesterday_part[ar_qt_activity_type] = {
                'yesterday': self.account_invoice_filter(ar_qt_activity_type, 'particular', date_yesterday),
                'before_yesterday': self.account_invoice_filter(ar_qt_activity_type, 'particular', date_before_yesterday),
                'increment': 0
            }
            account_invoice_yesterday_part[ar_qt_activity_type]['increment'] = self.calculate_increment(account_invoice_yesterday_part[ar_qt_activity_type]['yesterday'], account_invoice_yesterday_part[ar_qt_activity_type]['before_yesterday'])                                                                                    
        #sale_orders_yesterday_part (2) (yesterday and before_yesterday)
        sale_orders_yesterday_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            sale_orders_yesterday_part[ar_qt_activity_type] = {
                'yesterday': self.sale_orders_filter(ar_qt_activity_type, 'particular', date_yesterday, date_yesterday),
                'before_yesterday': self.sale_orders_filter(ar_qt_activity_type, 'particular', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            sale_orders_yesterday_part[ar_qt_activity_type]['increment'] = self.calculate_increment(sale_orders_yesterday_part[ar_qt_activity_type]['yesterday'], sale_orders_yesterday_part[ar_qt_activity_type]['before_yesterday'])            
        #sale_orders_date_order_send_mail_yesterday_part (3) (yesterday and before_yesterday)
        sale_orders_date_order_send_mail_yesterday_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type] = {
                'yesterday': self.sale_orders_filter_date_order_send_mail(ar_qt_activity_type, 'particular', date_yesterday, date_yesterday),
                'before_yesterday': self.sale_orders_filter_date_order_send_mail(ar_qt_activity_type, 'particular', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment'] = self.calculate_increment(sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['yesterday'], sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['before_yesterday'])
        #stock_picking_filter_management_date_yesterday_part (3B) (yesterday and before_yesterday)            
        stock_picking_filter_management_date_yesterday_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type] = {
                'yesterday': self.stock_picking_filter_management_date(ar_qt_activity_type, 'particular', date_yesterday, date_yesterday),
                'before_yesterday': self.stock_picking_filter_management_date(ar_qt_activity_type, 'particular', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment'] = stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['yesterday']-stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['before_yesterday']                                            
        #shipping_expedition_nacex_yesterday (4) (yesterday and before_yesterday)
        shipping_expedition_nacex_yesterday = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            shipping_expedition_nacex_yesterday[ar_qt_activity_type] = {
                'yesterday': self.shipping_expedition_nacex_yesterday(ar_qt_activity_type, 'particular', date_yesterday, date_yesterday),
                'before_yesterday':  self.shipping_expedition_nacex_yesterday(ar_qt_activity_type, 'particular', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            
            if shipping_expedition_nacex_yesterday[ar_qt_activity_type]['yesterday']>0 or shipping_expedition_nacex_yesterday[ar_qt_activity_type]['before_yesterday']>0:
                shipping_expedition_nacex_yesterday[ar_qt_activity_type]['increment'] = shipping_expedition_nacex_yesterday[ar_qt_activity_type]['yesterday']-shipping_expedition_nacex_yesterday[ar_qt_activity_type]['before_yesterday']                                    
        #sale_orders_date_order_yesterday_part (6) (yesterday and before_yesterday)
        sale_orders_date_order_yesterday_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            sale_orders_date_order_yesterday_part[ar_qt_activity_type] = {
                'yesterday': self.sale_orders_filter_date_order(ar_qt_activity_type, 'particular', date_yesterday, date_yesterday),
                'before_yesterday': self.sale_orders_filter_date_order(ar_qt_activity_type, 'particular', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            sale_orders_date_order_yesterday_part[ar_qt_activity_type]['increment'] = self.calculate_increment(sale_orders_date_order_yesterday_part[ar_qt_activity_type]['yesterday'], sale_orders_date_order_yesterday_part[ar_qt_activity_type]['before_yesterday'])
        #sale_orders_without_date_order_send_mail_part (custom) (yesterday and before yesterday)
        sale_orders_without_date_order_send_mail_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            sale_orders_without_date_order_send_mail_part[ar_qt_activity_type] = {
                'yesterday': self.sale_orders_filter_without_date_order_send_mail(ar_qt_activity_type, 'particular', date_end_last_month, date_start_last_month),
                'before_yesterday': self.sale_orders_filter_without_date_order_send_mail(ar_qt_activity_type, 'particular', date_end_last_month, date_start_last_month),
                'increment': 0
            }
            if sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['yesterday']>0 or sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['before_yesterday']>0:
                sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['increment'] = sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['yesterday']-sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['before_yesterday']             
        
        #crm_leads_without_user_id_yesterday_part (7) (yesterday and before_yesterday)
        crm_leads_without_user_id_yesterday_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            crm_leads_without_user_id_yesterday_part[ar_qt_activity_type] = {
                'yesterday': self.crm_lead_without_user_id(ar_qt_activity_type, 'particular', date_yesterday, date_yesterday),
                'before_yesterday': self.crm_lead_without_user_id(ar_qt_activity_type, 'particular', date_before_yesterday, date_before_yesterday),
                'increment': 0
            }
            if crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['yesterday']>0 or crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['before_yesterday']>0:
                crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment'] = crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['yesterday']-crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['before_yesterday']
        
        #crm_leads_without_user_id_last_month_part (8)
        crm_leads_without_user_id_last_month_part = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            crm_leads_without_user_id_last_month_part[ar_qt_activity_type] = {
                'yesterday': self.crm_lead_without_user_id(ar_qt_activity_type, 'particular', date_start_last_month, date_end_last_month),
            }
                                
        #slack_message
        #facturacion_dia (1)
        facturacion_dia_txt = {}
        facturacion_dia_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            facturacion_dia_color[ar_qt_activity_type] = "#fbff00"#Color yellow
                            
            facturacion_dia_ar_qt_activity_type = self.convert_amount_to_monetary_field(account_invoice_yesterday_part[ar_qt_activity_type]['yesterday']['amount_untaxed'])
            facturacion_dia_txt[ar_qt_activity_type] = str(facturacion_dia_ar_qt_activity_type)
            
            if account_invoice_yesterday_part[ar_qt_activity_type]['increment']['amount_untaxed']!=0:
                facturacion_dia_ar_qt_activity_type_increment = self.convert_amount_to_monetary_field(account_invoice_yesterday_part[ar_qt_activity_type]['increment']['amount_untaxed'])
                if "-" not in facturacion_dia_ar_qt_activity_type_increment:
                    facturacion_dia_ar_qt_activity_type_increment = '+'+str(facturacion_dia_ar_qt_activity_type_increment)
                
                facturacion_dia_txt[ar_qt_activity_type] += ' ('+str(facturacion_dia_ar_qt_activity_type_increment)+')'
                
                facturacion_dia_color[ar_qt_activity_type] = '#36a64f'#Color green
                if "-" in facturacion_dia_ar_qt_activity_type_increment:
                    facturacion_dia_color[ar_qt_activity_type] = '#ff0000'#Color red
        #numero_pedido_dia (2)
        numero_pedido_dia_txt = {}
        numero_pedido_dia_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter: 
            numero_pedido_dia_color[ar_qt_activity_type] = "#fbff00"#Color yellow
                           
            numero_pedido_dia_txt[ar_qt_activity_type] = str(sale_orders_yesterday_part[ar_qt_activity_type]['yesterday']['total'])
            
            if sale_orders_yesterday_part[ar_qt_activity_type]['increment']['total']!=0:
                if sale_orders_yesterday_part[ar_qt_activity_type]['increment']['total']>0:
                    sale_orders_yesterday_part[ar_qt_activity_type]['increment']['total'] = '+'+str(sale_orders_yesterday_part[ar_qt_activity_type]['increment']['total'])
                    
                numero_pedido_dia_txt[ar_qt_activity_type] += ' ('+str(sale_orders_yesterday_part[ar_qt_activity_type]['increment']['total'])+')'
                
                numero_pedido_dia_color[ar_qt_activity_type] = '#36a64f'#Color green
                if sale_orders_yesterday_part[ar_qt_activity_type]['increment']['total']<0:
                    numero_pedido_dia_color[ar_qt_activity_type] = '#ff0000'#Color red                
        #numero_pto_enviados_mail (3)
        numero_pto_enviados_mail_txt = {}
        numero_pto_enviados_mail_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            numero_pto_enviados_mail_color[ar_qt_activity_type] = "#fbff00"#Color yellow
            
            numero_pto_enviados_mail_txt[ar_qt_activity_type] = str(sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['yesterday']['total'])
                        
            if sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment']['total']!=0:
                if sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment']['total']>0:
                    sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment']['total'] = '+'+str(sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment']['total'])
                
                numero_pto_enviados_mail_txt[ar_qt_activity_type] += ' ('+str(sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment']['total'])+')'
                
                numero_pto_enviados_mail_color[ar_qt_activity_type] = '#36a64f'#Color green
                if sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['increment']['total']<0:
                    numero_pto_enviados_mail_color[ar_qt_activity_type] = '#ff0000'#Color red
        #numero_albaranes_hechos (3B)
        numero_albaranes_hechos_txt = {}
        numero_albaranes_hechos_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            numero_albaranes_hechos_color[ar_qt_activity_type] = ''
            numero_albaranes_hechos_txt[ar_qt_activity_type] = str(stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['yesterday'])
        
            if stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment']!=0:
                if stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment']>0:
                    stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment'] = '+'+str(stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment'])
                    
                numero_albaranes_hechos_txt[ar_qt_activity_type] += ' ('+str(stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment'])+')'
                
                numero_albaranes_hechos_color[ar_qt_activity_type] = '#36a64f'#Color green
                if stock_picking_filter_management_date_yesterday_part[ar_qt_activity_type]['increment']<0:
                    numero_albaranes_hechos_color[ar_qt_activity_type] = '#ff0000'#Color red                    
        #percent_muestras_presupuestos (4)        
        percent_muestras_presupuestos_txt = {}
        percent_muestras_presupuestos_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            percent_muestras_presupuestos_color[ar_qt_activity_type] = "#fbff00"#Color yellow
            #yesterday
            expediciones_nacex_yesterday = shipping_expedition_nacex_yesterday[ar_qt_activity_type]['yesterday']
            total_pto_realizados_yesterday = sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['yesterday']['total']
            
            percent_value_yesterday = 0
            if expediciones_nacex_yesterday>0 and total_pto_realizados_yesterday>0:
                percent_value_yesterday = (float(expediciones_nacex_yesterday)/float(total_pto_realizados_yesterday))*100
                percent_value_yesterday = "{0:.2f}".format(percent_value_yesterday)                
            
            percent_muestras_presupuestos_txt[ar_qt_activity_type] = str(percent_value_yesterday)+'%'
            #before_yesterday
            expediciones_nacex_before_yesterday = shipping_expedition_nacex_yesterday[ar_qt_activity_type]['before_yesterday']
            total_pto_realizados_before_yesterday = sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['before_yesterday']['total']
            
            percent_value_before_yesterday = 0
            if expediciones_nacex_before_yesterday>0 and total_pto_realizados_before_yesterday>0:
                percent_value_before_yesterday = (float(expediciones_nacex_before_yesterday)/float(total_pto_realizados_before_yesterday))*100
                percent_value_before_yesterday = "{0:.2f}".format(percent_value_before_yesterday)
            
            if percent_value_yesterday>0 or percent_value_before_yesterday>0:
                increment_calculate_percent_clean = float(percent_value_yesterday)-float(percent_value_before_yesterday)
                increment_calculate_percent = "{0:.2f}".format(increment_calculate_percent_clean)
                if increment_calculate_percent!=0:
                    if increment_calculate_percent_clean>0:
                        increment_calculate_percent = '+'+str(increment_calculate_percent)
                        
                    percent_muestras_presupuestos_txt[ar_qt_activity_type] += ' ('+str(increment_calculate_percent)+'%)'
                    
                    percent_muestras_presupuestos_color[ar_qt_activity_type] = '#36a64f'#Color green
                    if increment_calculate_percent_clean<0:
                        percent_muestras_presupuestos_color[ar_qt_activity_type] = '#ff0000'#Color red                                            
        #percent_presupuestos_realizados_vs_asignados (6)
        percent_presupuestos_realizados_vs_asignados_txt = {}
        percent_presupuestos_realizados_vs_asignados_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            percent_presupuestos_realizados_vs_asignados_color[ar_qt_activity_type] = "#fbff00"#Color yellow
            #yesterday
            numerador_yesterday = sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['yesterday']['total']
            denominador_yesterday = int(numerador_yesterday)+int(sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['yesterday'])
            
            percent_value_yesterday = 0
            if numerador_yesterday>0 and denominador_yesterday>0:
                percent_value_yesterday = (float(numerador_yesterday)/float(denominador_yesterday))*100
                percent_value_yesterday = "{0:.2f}".format(percent_value_yesterday)
                
            percent_presupuestos_realizados_vs_asignados_txt[ar_qt_activity_type] = str(percent_value_yesterday)+'%'
            #before_yesterday
            numerador_before_yesterday = sale_orders_date_order_send_mail_yesterday_part[ar_qt_activity_type]['before_yesterday']['total']
            denominador_before_yesterday = int(numerador_before_yesterday)+int(sale_orders_without_date_order_send_mail_part[ar_qt_activity_type]['before_yesterday'])
            
            percent_value_before_yesterday = 0
            if numerador_before_yesterday>0 and denominador_before_yesterday>0:
                percent_value_before_yesterday = (numerador_before_yesterday/denominador_before_yesterday)*100
                percent_value_before_yesterday = "{0:.2f}".format(percent_value_before_yesterday)
            
            if percent_value_yesterday>0 or percent_value_before_yesterday>0:
                increment_calculate_percent_clean = float(percent_value_yesterday)-float(percent_value_before_yesterday)
                increment_calculate_percent = "{0:.2f}".format(increment_calculate_percent_clean)
                if increment_calculate_percent!=0:                
                    if increment_calculate_percent_clean>0:
                        increment_calculate_percent = '+'+str(increment_calculate_percent)
                        
                    percent_presupuestos_realizados_vs_asignados_txt[ar_qt_activity_type] += ' ('+str(increment_calculate_percent)+'%)'
                    
                    percent_presupuestos_realizados_vs_asignados_color[ar_qt_activity_type] = '#36a64f'#Color green
                    if increment_calculate_percent_clean<0:
                        percent_presupuestos_realizados_vs_asignados_color[ar_qt_activity_type] = '#ff0000'#Color red                 
        
        #flujos_sin_asignar_ayer (7)
        flujos_sin_asignar_ayer_txt = {}
        flujos_sin_asignar_ayer_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            flujos_sin_asignar_ayer_color[ar_qt_activity_type] = "#36a64f"#Color yellow
            
            flujos_sin_asignar_ayer_txt[ar_qt_activity_type] = str(crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['yesterday'])
                        
            if crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment']!=0:
                if crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment']>0:
                    crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment'] = '+'+str(crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment'])
                
                flujos_sin_asignar_ayer_txt[ar_qt_activity_type] += ' ('+str(crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment'])+')'
                
                if crm_leads_without_user_id_yesterday_part[ar_qt_activity_type]['increment']!=0:
                    flujos_sin_asignar_ayer_color[ar_qt_activity_type] = '#ff0000'#Color red                        
        #flujos_sin_asignar_ultimos_30_dias (8)
        flujos_sin_asignar_ultimos_30_dias_txt = {}
        flujos_sin_asignar_ultimos_30_dias_color = {}
        for ar_qt_activity_type in ar_qt_activity_type_filter:
            flujos_sin_asignar_ultimos_30_dias_color[ar_qt_activity_type] = "#36a64f"#Color yellow
            
            flujos_sin_asignar_ultimos_30_dias_txt[ar_qt_activity_type] = str(crm_leads_without_user_id_last_month_part[ar_qt_activity_type]['yesterday'])
            
            if crm_leads_without_user_id_last_month_part[ar_qt_activity_type]['yesterday']>0:
                flujos_sin_asignar_ultimos_30_dias_color[ar_qt_activity_type] = '#ff0000'#Color red 
        
        attachments = [
            {                    
                "text": '[Todocesped] Facturacion del dia: '+facturacion_dia_txt['todocesped'],
                "color": facturacion_dia_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Facturacion del dia: '+facturacion_dia_txt['arelux'],
                "color": facturacion_dia_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] Numero de pedidos del dia: '+numero_pedido_dia_txt['todocesped'],
                "color": numero_pedido_dia_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Numero de pedidos del dia: '+numero_pedido_dia_txt['arelux'],
                "color": numero_pedido_dia_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] Numero de presupuestos del dia enviados por email: '+numero_pto_enviados_mail_txt['todocesped'],
                "color": numero_pto_enviados_mail_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Numero de presupuestos del dia enviados por email: '+numero_pto_enviados_mail_txt['arelux'],
                "color": numero_pto_enviados_mail_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] Numero de albaranes hechos: '+numero_albaranes_hechos_txt['todocesped'],
                "color": numero_albaranes_hechos_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Numero de albaranes hechos: '+numero_albaranes_hechos_txt['arelux'],
                "color": numero_albaranes_hechos_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] % de muestras sobre presupuestos: '+percent_muestras_presupuestos_txt['todocesped'],
                "color": percent_muestras_presupuestos_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] % de muestras sobre presupuestos: '+percent_muestras_presupuestos_txt['arelux'],
                "color": percent_muestras_presupuestos_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] % Presupuestos realizados contra asignados: '+percent_presupuestos_realizados_vs_asignados_txt['todocesped'],
                "color": percent_presupuestos_realizados_vs_asignados_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] % Presupuestos realizados contra asignados: '+percent_presupuestos_realizados_vs_asignados_txt['arelux'],
                "color": percent_presupuestos_realizados_vs_asignados_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] Flujos sin asignar (ayer): '+flujos_sin_asignar_ayer_txt['todocesped'],
                "color": flujos_sin_asignar_ayer_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Flujos sin asignar (ayer): '+flujos_sin_asignar_ayer_txt['arelux'],
                "color": flujos_sin_asignar_ayer_color['arelux'],                                    
            },
            {                    
                "text": '[Todocesped] Flujos sin asignar (ultimos mes): '+flujos_sin_asignar_ultimos_30_dias_txt['todocesped'],
                "color": flujos_sin_asignar_ultimos_30_dias_color['todocesped'],                                    
            },
            {                    
                "text": '[Arelux] Flujos sin asignar (ultimos mes): '+flujos_sin_asignar_ultimos_30_dias_txt['arelux'],
                "color": flujos_sin_asignar_ultimos_30_dias_color['arelux'],                                    
            },                                                            
        ]                                                           
        slack_message_vals = {
            'attachments': attachments,
            'model': 'slack.channel.daily.report',
            'res_id': 0,
            'msg': '*Particulares*',
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_report_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)

    @api.multi    
    def cron_odoo_slack_channel_daily_report(self, cr=None, uid=False, context=None):
        weekday = datetime.today().weekday()
        weekdays_without_report = [0,6]
        if weekday not in weekdays_without_report:                         
            self.odoo_slack_channel_daily_report_prof()        
            self.odoo_slack_channel_daily_report_part()                                                                                                                                                                         