# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class SlackChannelDailyReport(models.Model):
    _name = 'slack.channel.daily.report'
    _description = 'Slack Channel Daily Report'
    
    @api.model
    def convert_amount_to_monetary_field(self, amount_untaxed):
        options = {
            'display_currency': self.env.user.company_id.currency_id
        }        
        amount_untaxed_monetary = self.env['ir.qweb.field.monetary'].value_to_html(amount_untaxed, options)        
        amount_untaxed_monetary = amount_untaxed_monetary.replace('<span class="oe_currency_value">', '')
        amount_untaxed_monetary = amount_untaxed_monetary.replace('</span>', '')
        return amount_untaxed_monetary

    @api.model
    def bi_pedidos_confirmados_dia(self, date_start, date_end, date_previous_start, date_previous_end):
        #define
        ar_qt_activity_types = ['todocesped', 'arelux']
        ar_qt_customer_types = ['particular', 'profesional']
        #data
        data = {}
        for ar_qt_activity_type in ar_qt_activity_types:
            data[ar_qt_activity_type] = {}
            for ar_qt_customer_type in ar_qt_customer_types:
                data_item = {
                    'data': self.sale_order_filter_amount_untaxed(ar_qt_activity_type, ar_qt_customer_type, date_start, date_end),
                    'data_previous': self.sale_order_filter_amount_untaxed(ar_qt_activity_type, ar_qt_customer_type, date_previous_start, date_previous_end),
                    'text': '',
                    'increment': 0,
                    'color': ''
                }
                #text
                data_item['text'] = str(self.convert_amount_to_monetary_field(data_item['data']))
                #increment
                if data_item['data']>0 or data_item['data_previous']>0:
                    data_item['color'] = '#fbff00'#define color (yellow)
                    #increment
                    data_item['increment'] = data_item['data']-data_item['data_previous']
                    if data_item['increment']!=0:
                        data_item['text'] += ' ('
                        #possitive-neggative
                        if data_item['increment']>0:
                            data_item['text'] += '+'
                            data_item['color'] = '#36a64f'#green
                        else:
                            data_item['color'] = '#ff0000'#red
                        #add and close
                        data_item['text'] += str(self.convert_amount_to_monetary_field(data_item['increment'])) +')'
                #data_item
                data[ar_qt_activity_type][ar_qt_customer_type] = data_item
        #return
        return data
        
    @api.model        
    def sale_order_filter_amount_untaxed(self, ar_qt_activity_type, ar_qt_customer_type, date_from, date_to):
        amount_untaxed = 0
        search_filters = [
            ('state', 'in', ('sale', 'done')),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('ar_qt_customer_type', '=', ar_qt_customer_type),
            ('confirmation_date', '>=', date_from.strftime("%Y-%m-%d")+' 00:00:00'),
            ('confirmation_date', '<=', date_to.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        sale_order_ids = self.env['sale.order'].search(search_filters)
        if len(sale_order_ids)>0:
            for sale_order_id in sale_order_ids:
                amount_untaxed += sale_order_id.amount_untaxed
        #return            
        return amount_untaxed
        
    @api.model        
    def total_pedidos_dia(self, date_start, date_end, date_previous_start, date_previous_end):
        #define
        ar_qt_activity_types = ['todocesped', 'arelux']
        ar_qt_customer_types = ['particular', 'profesional']
        #data
        data = {}
        for ar_qt_activity_type in ar_qt_activity_types:
            data[ar_qt_activity_type] = {}
            for ar_qt_customer_type in ar_qt_customer_types:
                data_item = {
                    'data': self.sale_order_filter_count(ar_qt_activity_type, ar_qt_customer_type, date_start, date_end),
                    'data_previous': self.sale_order_filter_count(ar_qt_activity_type, ar_qt_customer_type, date_previous_start, date_previous_end),
                    'text': '',
                    'increment': 0,
                    'color': ''
                }
                #text
                data_item['text'] = str(data_item['data'])
                #increment
                if data_item['data']>0 or data_item['data_previous']>0:
                    data_item['color'] = '#fbff00'#define color (yellow)
                    #increment
                    data_item['increment'] = data_item['data']-data_item['data_previous']
                    #increment_percent
                    increment_percent_item = 0
                    if data_item['data']>0 and data_item['data_previous']>0:
                        increment_percent_item = (float(data_item['data'])/float(data_item['data_previous']))*100
                    elif data_item['data']==0 and data_item['data_previous']>0:
                        increment_percent_item = -100                        
                    #format
                    data_item['increment_percent'] = "{0:.2f}".format(increment_percent_item)
                    #operations
                    if data_item['increment']!=0:
                        data_item['text'] += ' ('
                        #possitive-neggative
                        if data_item['increment']>0:
                            data_item['text'] += '+'
                            data_item['color'] = '#36a64f'#green
                        else:
                            data_item['text'] += '-'
                            data_item['color'] = '#ff0000'#red
                        #add and close
                        data_item['text'] += str(data_item['increment_percent']) +'%)'
                #data_item
                data[ar_qt_activity_type][ar_qt_customer_type] = data_item
        #return
        return data
        
    @api.model    
    def sale_order_filter_count(self, ar_qt_activity_type, ar_qt_customer_type, date_from, date_to):
        search_filters = [
            ('state', 'in', ('sale', 'done')),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('ar_qt_customer_type', '=', ar_qt_customer_type),
            ('confirmation_date', '>=', date_from.strftime("%Y-%m-%d")+' 00:00:00'),
            ('confirmation_date', '<=', date_to.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        return len(self.env['sale.order'].search(search_filters))
    
    @api.model        
    def total_pedidos_dia_por_comercial(self, date_start, date_end, date_previous_start, date_previous_end):
        #define
        ar_qt_activity_types = ['todocesped', 'arelux']
        #data
        data = {}
        for ar_qt_activity_type in ar_qt_activity_types:
            #data_item
            data_item = {
                'items': []
            }
            #user_ids_item
            user_ids_item = self.sale_order_filter_get_user_ids(ar_qt_activity_type, date_previous_start, date_end)
            if len(user_ids_item)>0:
                for user_id_item in user_ids_item:
                    data_item2 = {
                        'user_name': user_id_item['name'],
                        'user_id': user_id_item['id'],
                        'data': self.sale_order_filter_get_user_id(ar_qt_activity_type, user_id_item['id'], date_start, date_end),
                        'data_previous': self.sale_order_filter_get_user_id(ar_qt_activity_type, user_id_item['id'], date_previous_start, date_previous_end),
                        'text': '',
                        'increment': 0,
                        'color': ''                            
                    }
                    #text
                    data_item2['text'] = str(data_item2['data'])
                    #increment
                    if data_item2['data']>0 or data_item2['data_previous']>0:
                        data_item2['color'] = '#fbff00'#define color (yellow)
                        #increment
                        data_item2['increment'] = data_item2['data']-data_item2['data_previous']
                        #increment_percent
                        increment_percent_item = 0
                        if data_item2['data']>0 and data_item2['data_previous']>0:
                            increment_percent_item = (float(data_item2['data'])/float(data_item2['data_previous']))*100
                        elif data_item2['data']==0 and data_item2['data_previous']>0:
                            increment_percent_item = -100
                        #format
                        data_item2['increment_percent'] = "{0:.2f}".format(increment_percent_item)
                        #operations
                        if data_item2['increment']!=0:
                            data_item2['text'] += ' ('
                            #possitive-neggative
                            if data_item2['increment']>0:
                                data_item2['text'] += '+'
                                data_item2['color'] = '#36a64f'#green
                            else:
                                data_item['text'] += '-'
                                data_item2['color'] = '#ff0000'#red
                            #add and close
                            data_item2['text'] += str(data_item2['increment_percent']) +'%)'                        
                    #append
                    data_item['items'].append(data_item2)           
            #data_item
            data[ar_qt_activity_type] = data_item                
        #return        
        return data
    
    @api.model
    def sale_order_filter_get_user_ids(self, ar_qt_activity_type, date_from, date_to):
        data = []
        user_ids = []
        search_filters = [
            ('state', 'in', ('sale', 'done')),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('user_id', '!=', False),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('confirmation_date', '>=', date_from.strftime("%Y-%m-%d")+' 00:00:00'),
            ('confirmation_date', '<=', date_to.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        sale_order_ids = self.env['sale.order'].search(search_filters)
        if len(sale_order_ids)>0:
            res_users_ids = self.env['res.users'].search([
                ('id', 'in', sale_order_ids.mapped('user_id').ids)
            ])
            if len(res_users_ids)>0:
                for res_users_id in res_users_ids:
                    data.append({
                        'id': res_users_id.id,
                        'name': str(res_users_id.name)
                    })
        #return
        return data
        
    @api.model        
    def sale_order_filter_get_user_id(self, ar_qt_activity_type, user_id, date_from, date_to):
        search_filters = [
            ('state', 'in', ('sale', 'done')),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('user_id', '=', user_id),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('confirmation_date', '>=', date_from.strftime("%Y-%m-%d")+' 00:00:00'),
            ('confirmation_date', '<=', date_to.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        return len(self.env['sale.order'].search(search_filters))        
    
    @api.model    
    def total_muestras_enviadas(self, date_start, date_end, date_previous_start, date_previous_end):
        #define
        ar_qt_activity_types = ['todocesped']
        #data
        data = {}
        for ar_qt_activity_type in ar_qt_activity_types:
            data_item = {
                'data': self.stock_picking_filter_count(ar_qt_activity_type, 7, date_start, date_end),
                'data_previous': self.stock_picking_filter_count(ar_qt_activity_type, 7, date_previous_start, date_previous_end),
                'text': '',
                'increment': 0,
                'color': ''
            }
            #text
            data_item['text'] = str(data_item['data'])
            #increment
            if data_item['data']>0 or data_item['data_previous']>0:
                data_item['color'] = '#fbff00'#define color (yellow)
                #increment
                data_item['increment'] = data_item['data']-data_item['data_previous']
                #increment_percent
                increment_percent_item = 0
                if data_item['data']>0 and data_item['data_previous']>0:
                    increment_percent_item = (float(data_item['data'])/float(data_item['data_previous']))*100
                elif data_item['data']==0 and data_item['data_previous']>0:
                    increment_percent_item = -100                    
                #format
                data_item['increment_percent'] = "{0:.2f}".format(increment_percent_item)
                #operations
                if data_item['increment']!=0:
                    data_item['text'] += ' ('
                    #possitive-neggative
                    if data_item['increment']>0:
                        data_item['text'] += '+'
                        data_item['color'] = '#36a64f'#green
                    else:
                        data_item['text'] += '-'
                        data_item['color'] = '#ff0000'#red
                    #add and close
                    data_item['text'] += str(data_item['increment_percent']) +'%)'
            #data_item
            data[ar_qt_activity_type] = data_item
        #return            
        return data
    
    @api.model        
    def stock_picking_filter_count(self, ar_qt_activity_type, picking_type_id, date_from, date_to):
        search_filters = [
            ('state', '=', 'done'),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('picking_type_id', '=', picking_type_id),
            ('date_done', '>=', date_from.strftime("%Y-%m-%d")+' 00:00:00'),
            ('date_done', '<=', date_to.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        return len(self.env['stock.picking'].search(search_filters))
        
    @api.model
    def total_clientes_nuevos(self, date_start, date_end, date_previous_start, date_previous_end):
        #define
        ar_qt_activity_types = ['todocesped', 'arelux']
        ar_qt_customer_types = ['profesional']
        #data
        data = {}
        for ar_qt_activity_type in ar_qt_activity_types:
            data[ar_qt_activity_type] = {}
            for ar_qt_customer_type in ar_qt_customer_types:
                data_item = {
                    'data': self.res_partner_filter_count(ar_qt_activity_type, ar_qt_customer_type, date_start, date_end),
                    'data_previous': self.res_partner_filter_count(ar_qt_activity_type, ar_qt_customer_type, date_previous_start, date_previous_end),
                    'text': '',
                    'increment': 0,
                    'color': ''
                }
                #text
                data_item['text'] = str(data_item['data'])
                #increment
                if data_item['data']>0 or data_item['data_previous']>0:
                    data_item['color'] = '#fbff00'#define color (yellow)
                    #increment
                    data_item['increment'] = data_item['data']-data_item['data_previous']
                    #increment_percent
                    increment_percent_item = 0
                    if data_item['data']>0 and data_item['data_previous']>0:
                        increment_percent_item = (float(data_item['data'])/float(data_item['data_previous']))*100
                    elif data_item['data']==0 and data_item['data_previous']>0:
                        increment_percent_item = -100                        
                    #format
                    data_item['increment_percent'] = "{0:.2f}".format(increment_percent_item)
                    #operations
                    if data_item['increment']!=0:
                        data_item['text'] += ' ('
                        #possitive-neggative
                        if data_item['increment']>0:
                            data_item['text'] += '+'
                            data_item['color'] = '#36a64f'#green
                        else:
                            data_item['text'] += '-'
                            data_item['color'] = '#ff0000'#red
                        #add and close
                        data_item['text'] += str(data_item['increment_percent']) +'%)'
                #data_item
                data[ar_qt_activity_type][ar_qt_customer_type] = data_item
        #return
        return data
    
    @api.model        
    def res_partner_filter_count(self, ar_qt_activity_type, ar_qt_customer_type, date_from, date_to):
        search_filters = [
            ('active', '=', True),
            ('type', '=', 'contact'),
            ('ar_qt_activity_type', '=', ar_qt_activity_type),
            ('ar_qt_customer_type', '=', ar_qt_customer_type),
            ('create_date', '>=', date_from.strftime("%Y-%m-%d")+' 00:00:00'),
            ('create_date', '<=', date_to.strftime("%Y-%m-%d")+' 23:59:59')
        ]
        return len(self.env['res.partner'].search(search_filters))                                                            

    @api.model    
    def cron_odoo_slack_channel_daily_report(self):
        weekday = datetime.today().weekday()
        weekdays_without_report = [0,6]
        if weekday not in weekdays_without_report:
            #define (general thingsa)
            ar_qt_activity_types = ['todocesped', 'arelux']
            ar_qt_customer_types = ['particular', 'profesional']
            attachments = []
            #dates
            current_date = datetime.today()
            date_yesterday = current_date + relativedelta(days=-1)
            date_before_yesterday = date_yesterday + relativedelta(days=-1)            
            #all info              
            #bi_pedidos_confirmados_dia
            bi_pedidos_confirmados_dia = self.bi_pedidos_confirmados_dia(date_yesterday, date_yesterday, date_before_yesterday, date_before_yesterday)                                
            #bi_pedidos_confirmados_dia > attachments
            for ar_qt_activity_type in ar_qt_activity_types:
                if ar_qt_activity_type in bi_pedidos_confirmados_dia:
                    for ar_qt_customer_type in ar_qt_customer_types:
                        if ar_qt_customer_type in bi_pedidos_confirmados_dia[ar_qt_activity_type]:
                            attachment_item = {                    
                                "text": '['+str(ar_qt_activity_type.title())+'] ['+str(ar_qt_customer_type.title())+'] BI pedidos confirmados: '+bi_pedidos_confirmados_dia[ar_qt_activity_type][ar_qt_customer_type]['text'],
                                "color": bi_pedidos_confirmados_dia[ar_qt_activity_type][ar_qt_customer_type]['color'],                                    
                            }
                            attachments.append(attachment_item)
            #total_pedidos_dia
            total_pedidos_dia = self.total_pedidos_dia(date_yesterday, date_yesterday, date_before_yesterday, date_before_yesterday)
            #total_pedidos_dia > attachments
            for ar_qt_activity_type in ar_qt_activity_types:
                if ar_qt_activity_type in total_pedidos_dia:
                    for ar_qt_customer_type in ar_qt_customer_types:
                        if ar_qt_customer_type in total_pedidos_dia[ar_qt_activity_type]:
                            attachment_item = {                    
                                "text": '['+str(ar_qt_activity_type.title())+'] ['+str(ar_qt_customer_type.title())+'] Numero de pedidos del dia: '+total_pedidos_dia[ar_qt_activity_type][ar_qt_customer_type]['text'],
                                "color": total_pedidos_dia[ar_qt_activity_type][ar_qt_customer_type]['color'],                                    
                            }
                            attachments.append(attachment_item)
            #total_pedidos_dia_por_comercial
            total_pedidos_dia_por_comercial = self.total_pedidos_dia_por_comercial(date_yesterday, date_yesterday, date_before_yesterday, date_before_yesterday)
            #total_pedidos_dia_por_comercial > attachments
            for ar_qt_activity_type in ar_qt_activity_types:
                if ar_qt_activity_type in total_pedidos_dia:
                    total_pedidos_dia_por_comercial_item = total_pedidos_dia_por_comercial[ar_qt_activity_type]
                    if 'items' in total_pedidos_dia_por_comercial_item:
                        for total_pedidos_dia_por_comercial_item_real in total_pedidos_dia_por_comercial_item['items']:
                            attachment_item = {                    
                                "text": '['+str(ar_qt_activity_type.title())+'] ['+str(total_pedidos_dia_por_comercial_item_real['user_name'].title())+'] Numero de pedidos del dia: '+total_pedidos_dia_por_comercial_item_real['text'],
                                "color": total_pedidos_dia_por_comercial_item_real['color'],                                    
                            }
                            attachments.append(attachment_item)
            #total_muestras_enviadas > attachments
            total_muestras_enviadas = self.total_muestras_enviadas(date_yesterday, date_yesterday, date_before_yesterday, date_before_yesterday)    
            for ar_qt_activity_type in ar_qt_activity_types:
                if ar_qt_activity_type in total_muestras_enviadas:
                    attachment_item = {                    
                        "text": '['+str(ar_qt_activity_type.title())+'] Total muestras enviadas: '+total_muestras_enviadas[ar_qt_activity_type]['text'],
                        "color": total_muestras_enviadas[ar_qt_activity_type]['color'],                                    
                    }
                    attachments.append(attachment_item)
            #total_clientes_nuevos
            total_clientes_nuevos = self.total_clientes_nuevos(date_yesterday, date_yesterday, date_before_yesterday, date_before_yesterday)
            for ar_qt_activity_type in ar_qt_activity_types:
                if ar_qt_activity_type in total_clientes_nuevos:
                    for ar_qt_customer_type in ar_qt_customer_types:
                        if ar_qt_customer_type in total_clientes_nuevos[ar_qt_activity_type]:
                            attachment_item = {                    
                                "text": '['+str(ar_qt_activity_type.title())+'] ['+str(ar_qt_customer_type.title())+'] Clientes profesionales nuevos metidos al sistema: '+total_clientes_nuevos[ar_qt_activity_type][ar_qt_customer_type]['text'],
                                "color": total_clientes_nuevos[ar_qt_activity_type][ar_qt_customer_type]['color'],                                    
                            }
                            attachments.append(attachment_item)                                
            #logger
            #_logger.info(attachments)
            #msg
            msg = '*Reporte diario* ['+str(date_yesterday.strftime("%d/%m/%Y"))+' vs '+str(date_before_yesterday.strftime("%d/%m/%Y"))+']'
            #slack_message_vals                                                                       
            slack_message_vals = {
                'attachments': attachments,
                'model': 'slack.channel.daily.report',
                'res_id': 0,
                'msg': str(msg),
                'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_report_channel'),                                                         
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                                                                                                                                                                         