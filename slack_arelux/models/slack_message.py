# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from dateutil.relativedelta import relativedelta
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class SlackMessage(models.Model):
    _inherit = 'slack.message'

    @api.model
    def reporte_ranking_semanal_presupuestos_enviados_por_comercial(self, date_start, date_end):
        user_ids = []
        # search
        sale_order_ids_all = self.env['sale.order'].sudo().search([
            ('ar_qt_activity_type', '=', 'todocesped'),
            ('ar_qt_customer_type', '=', 'particular'),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('user_id', '!=', False),
            ('create_date', '>=', date_start.strftime("%Y-%m-%d") + ' 00:00:00'),
            ('create_date', '<=', date_end.strftime("%Y-%m-%d") + ' 23:59:59')
        ])
        if len(sale_order_ids_all) > 0:
            automation_log_ids = self.env['automation.log'].sudo().search([
                ('model', '=', 'sale.order'),
                ('action', '=', 'send_mail'),
                ('res_id', 'in', sale_order_ids_all.ids)
            ])
            sale_order_ids_all_without_automation = self.env['sale.order'].sudo().search([
                ('id', 'in', sale_order_ids_all.ids),
                ('id', 'not in', automation_log_ids.mapped('res_id'))
            ])
            res_user_ids = self.env['res.users'].sudo().search([
                ('id', 'in', sale_order_ids_all_without_automation.mapped('user_id').ids)
            ], order='name ASC')
            if len(res_user_ids) > 0:
                for res_user_id in res_user_ids:
                    # define
                    user_id_item = {
                        'id': res_user_id.id,
                        'name': str(res_user_id.name)
                    }
                    # total_sale_order
                    sale_order_ids = self.env['sale.order'].sudo().search([
                        ('id', 'in', sale_order_ids_all_without_automation.ids),
                        ('user_id', '=', res_user_id.id)
                    ])
                    user_id_item['total_sale_order'] = len(sale_order_ids)
                    # total_sale_order_sent
                    sale_order_ids = self.env['sale.order'].sudo().search([
                        ('id', 'in', sale_order_ids_all_without_automation.ids),
                        ('user_id', '=', res_user_id.id),
                        ('state', '=', 'sent')
                    ])
                    user_id_item['total_sale_order_sent'] = len(sale_order_ids)
                    # append
                    user_ids.append(user_id_item)
        #user_ids sort
        if len(user_ids)>0:
            user_ids.sort(key=lambda x: x.get('total_sale_order_sent'), reverse=True)
        #user_ids
        return user_ids

    @api.model
    def reporte_ranking_semanal_presupuestos_aceptados_por_comercial(self, date_start, date_end):
        user_ids = []
        # search
        sale_order_ids_all = self.env['sale.order'].sudo().search([
            ('ar_qt_activity_type', '=', 'todocesped'),
            ('ar_qt_customer_type', '=', 'particular'),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('user_id', '!=', False),
            ('state', 'in', ('sale', 'done')),
            ('create_date', '>=', date_start.strftime("%Y-%m-%d") + ' 00:00:00'),
            ('create_date', '<=', date_end.strftime("%Y-%m-%d") + ' 23:59:59')
        ])
        res_user_ids = self.env['res.users'].sudo().search([
            ('id', 'in', sale_order_ids_all.mapped('user_id').ids)
        ], order='name ASC')
        if len(res_user_ids) > 0:
            for res_user_id in res_user_ids:
                # define
                user_id_item = {
                    'id': res_user_id.id,
                    'name': str(res_user_id.name)
                }
                # total_sale_order
                sale_order_ids = self.env['sale.order'].sudo().search([
                    ('id', 'in', sale_order_ids_all.ids),
                    ('user_id', '=', res_user_id.id),
                    ('state', 'in', ('sale', 'done'))
                ])
                user_id_item['total_sale_order'] = len(sale_order_ids)
                # append
                user_ids.append(user_id_item)
        # user_ids sort
        if len(user_ids) > 0:
            user_ids.sort(key=lambda x: x.get('total_sale_order'), reverse=True)
        # user_ids
        return user_ids

    @api.model
    def reporte_ranking_semanal_upselling_por_comercial(self, date_start, date_end):
        user_ids = []
        # product_template
        product_template_id = self.env['product.template'].sudo().search([
            ('default_code', 'in', ('JAR143', 'COM8', 'JAR85'))
        ])
        sale_order_line_ids = self.env['sale.order.line'].sudo().search([
            ('product_id', 'in', product_template_id.ids),
            ('price_unit', '>', 0),
            ('order_id.ar_qt_activity_type', '=', 'todocesped'),
            ('order_id.ar_qt_customer_type', '=', 'particular'),
            ('order_id.claim', '=', False),
            ('order_id.amount_total', '>', 0),
            ('order_id.user_id', '!=', False),
            ('order_id.state', 'in', ('sale', 'done')),
            ('order_id.create_date', '>=', date_start.strftime("%Y-%m-%d") + ' 00:00:00'),
            ('order_id.create_date', '<=', date_end.strftime("%Y-%m-%d") + ' 23:59:59')
        ])
        if len(sale_order_line_ids)>0:
            sale_order_ids = self.env['sale.order'].sudo().search([
                ('id', 'in', sale_order_line_ids.mapped('order_id').ids)
            ])
            res_user_ids = self.env['res.users'].sudo().search([
                ('id', 'in', sale_order_ids.mapped('user_id').ids)
            ], order='name ASC')
            if len(res_user_ids) > 0:
                for res_user_id in res_user_ids:
                    # define
                    user_id_item = {
                        'id': res_user_id.id,
                        'name': str(res_user_id.name)
                    }
                    # total_sale_order
                    sale_order_ids_filter = self.env['sale.order'].sudo().search([
                        ('id', 'in', sale_order_ids.ids),
                        ('user_id', '=', res_user_id.id)
                    ])
                    user_id_item['total_sale_order'] = len(sale_order_ids_filter)
                    # append
                    user_ids.append(user_id_item)
        # user_ids sort
        if len(user_ids) > 0:
            user_ids.sort(key=lambda x: x.get('total_sale_order'), reverse=True)
        # user_ids
        return user_ids

    @api.model
    def reporte_ranking_semanal_ventas_totales_por_comercial(self, date_start, date_end):
        user_ids = []
        # search
        sale_order_ids_all = self.env['sale.order'].sudo().search([
            ('ar_qt_activity_type', '=', 'todocesped'),
            ('ar_qt_customer_type', 'in', ('particular', 'profesional')),
            ('claim', '=', False),
            ('amount_total', '>', 0),
            ('user_id', '!=', False),
            ('state', 'in', ('sale', 'done')),
            ('create_date', '>=', date_start.strftime("%Y-%m-%d") + ' 00:00:00'),
            ('create_date', '<=', date_end.strftime("%Y-%m-%d") + ' 23:59:59')
        ])
        res_user_ids = self.env['res.users'].sudo().search([
            ('id', 'in', sale_order_ids_all.mapped('user_id').ids)
        ], order='name ASC')
        if len(res_user_ids) > 0:
            for res_user_id in res_user_ids:
                # define
                user_id_item = {
                    'id': res_user_id.id,
                    'name': str(res_user_id.name),
                    'amount_sale_order': 0,
                    'amount_sale_order_format': 0,
                    'currency_symbol': False
                }
                # total_sale_order
                sale_order_ids = self.env['sale.order'].sudo().search([
                    ('id', 'in', sale_order_ids_all.ids),
                    ('user_id', '=', res_user_id.id),
                    ('state', 'in', ('sale', 'done'))
                ])
                user_id_item['total_sale_order'] = len(sale_order_ids)
                # amount_sale_order
                if len(sale_order_ids)>0:
                    for sale_order_id in sale_order_ids:
                        user_id_item['amount_sale_order'] += sale_order_id.amount_untaxed
                        #currency_symbol
                        if user_id_item['currency_symbol']==False:
                            user_id_item['currency_symbol'] = sale_order_id.currency_id.symbol
                #format
                user_id_item['amount_sale_order'] = "{0:.2f}".format(user_id_item['amount_sale_order'])
                user_id_item['amount_sale_order_format'] = str(user_id_item['amount_sale_order']) + ' ' + str(user_id_item['currency_symbol'])
                # append
                user_ids.append(user_id_item)
        # user_ids sort
        if len(user_ids) > 0:
            user_ids.sort(key=lambda x: x.get('amount_sale_order'), reverse=True)
        #user_ids
        return user_ids

    @api.multi
    def cron_odoo_slack_reporte_ranking_semanal(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_slack_reporte_ranking_semanal')
        #define
        current_date = datetime.today()
        date_start = current_date + relativedelta(days=-7)
        date_end = current_date
        # Presupuestos enviados por comercial
        user_ids_presupuestos_enviados_por_comercial = self.reporte_ranking_semanal_presupuestos_enviados_por_comercial(date_start, date_end)
        attachments = []
        if len(user_ids_presupuestos_enviados_por_comercial)>0:
            count = 1
            for user_id in user_ids_presupuestos_enviados_por_comercial:
                attachment_item = {
                    "text": '#'+str(count)+' '+str(user_id['name'])+': '+str(user_id['total_sale_order_sent'])+'/'+str(user_id['total_sale_order'])
                }
                attachments.append(attachment_item)
                count += 1
        # msg
        msg = '*Ranking presupuestos enviados por comercial* ['+str(date_start.strftime("%d/%m/%Y"))+' - '+str(date_end.strftime("%d/%m/%Y"))+']'
        # slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': 'slack.message',
            'res_id': 0,
            'msg': str(msg),
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_reporte_ranking_semanal')
        }
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        # Presupuestos aceptados por comercial
        user_ids_presupuestos_aceptados_por_comercial = self.reporte_ranking_semanal_presupuestos_aceptados_por_comercial(date_start, date_end)
        attachments = []
        if len(user_ids_presupuestos_aceptados_por_comercial) > 0:
            count = 1
            for user_id in user_ids_presupuestos_aceptados_por_comercial:
                attachment_item = {
                    "text": '#'+str(count)+' '+ str(user_id['name']) + ': ' + str(user_id['total_sale_order'])
                }
                attachments.append(attachment_item)
                count += 1
        # msg
        msg = '*Presupuestos aceptados por comercial* ['+str(date_start.strftime("%d/%m/%Y"))+' - '+str(date_end.strftime("%d/%m/%Y"))+']'
        # slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': 'slack.message',
            'res_id': 0,
            'msg': str(msg),
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_reporte_ranking_semanal')
        }
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        # UpSelling por comercial
        user_ids_upselling_por_comercial = self.reporte_ranking_semanal_upselling_por_comercial(date_start, date_end)
        attachments = []
        if len(user_ids_upselling_por_comercial) > 0:
            count = 1
            for user_id in user_ids_upselling_por_comercial:
                attachment_item = {
                    "text": '#'+str(count)+' '+ str(user_id['name']) + ': ' + str(user_id['total_sale_order'])
                }
                attachments.append(attachment_item)
                count += 1
        # msg
        msg = '*UpSelling por comercial*  ['+str(date_start.strftime("%d/%m/%Y"))+' - '+str(date_end.strftime("%d/%m/%Y"))+']'
        # slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': 'slack.message',
            'res_id': 0,
            'msg': str(msg),
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_reporte_ranking_semanal')
        }
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        # Ventas totales por comercial
        user_ids_ventas_totales_por_comercial = self.reporte_ranking_semanal_ventas_totales_por_comercial(date_start, date_end)
        attachments = []
        if len(user_ids_ventas_totales_por_comercial) > 0:
            count = 1
            for user_id in user_ids_ventas_totales_por_comercial:
                attachment_item = {
                    "text": '#'+str(count)+' '+ str(user_id['name']) + ': ' + str(user_id['amount_sale_order_format'])
                }
                attachments.append(attachment_item)
                count += 1
        # msg
        msg = '*Ventas totales por comercial*  ['+str(date_start.strftime("%d/%m/%Y"))+' - '+str(date_end.strftime("%d/%m/%Y"))+']'
        # slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': 'slack.message',
            'res_id': 0,
            'msg': str(msg),
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_reporte_ranking_semanal')
        }
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)