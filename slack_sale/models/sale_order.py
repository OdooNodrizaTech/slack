# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'    
    
    @api.one    
    def action_account_invoice_not_create_partner_without_vat(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=sale.order' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": _('The invoice for the order %s could not be created because '
                           'there is no CIF defined for the customer') % self.name,
                "text": self.name,                        
                "color": "#ff0000",
                "fallback": _("View sale order %s %s") % (
                    self.name,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _("View sale order %s") % self.name,
                        "url": url_item
                    }
                ],
                "fields": [                    
                    {
                        "title": _("User"),
                        "value": self.user_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Address invoice"),
                        "value": self.partner_invoice_id.name,
                        'short': True,
                    }
                ],                    
            }
        ]
        vals = {
            'attachments': attachments,
            'model': 'sale.order',
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_log_contabilidad_channel'
            ),
        }                        
        self.env['slack.message'].sudo().create(vals)
    
    @api.one    
    def action_confirm_create_message_slack_pre(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=sale.order' % (
            web_base_url,
            self.id
        )
        options = {
            'display_currency': self.currency_id
        }
        amount_untaxed_monetary = self.env['ir.qweb.field.monetary'].value_to_html(self.amount_untaxed, options)        
        amount_untaxed_monetary = amount_untaxed_monetary.replace('<span class="oe_currency_value">', '')
        amount_untaxed_monetary = amount_untaxed_monetary.replace('</span>', '')                                                                
                                                                
        attachments = [
            {                    
                "title": _('Sale order confirm'),
                "text": self.name,                        
                "color": "#36a64f",
                "fallback": _("View sale order %s %s") % (
                    self.name,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _("View sale order %s") % self.name,
                        "url": url_item
                    }
                ],
                "fields": [                    
                    {
                        "title": _("User"),
                        "value": self.user_id.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Customer"),
                        "value": self.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Amount untaxed"),
                        "value": amount_untaxed_monetary,
                        'short': True,
                    }
                ],                    
            }
        ]            
        return attachments
    
    @api.one    
    def action_confirm_create_message_slack(self):
        vals = {
            'attachments': self.action_confirm_create_message_slack_pre()[0],
            'model': 'sale.order',
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_sale_order_confirm'),                                                         
        }                        
        self.env['slack.message'].sudo().create(vals)

    @api.one
    def action_confirm_with_claim_create_message_slack(self):
        vals = {
            'attachments': self.action_confirm_create_message_slack_pre()[0],
            'model': 'sale.order',
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_sale_order_confirm_with_claim'),
        }
        self.env['slack.message'].sudo().create(vals)
    
    @api.one    
    def action_custom_send_sms_info_slack(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=sale.order' % (
            web_base_url,
            self.id
        )
        aum = self.env['ir.qweb.field.monetary'].value_to_html(
            self.amount_untaxed,
            {
                'display_currency': self.currency_id
            }
        )
        aum = aum.replace('<span class="oe_currency_value">', '')
        aum = aum.replace('</span>', '')
        
        attachments = [
            {                    
                "title": _('The budget info has been sent by SMS'),
                "text": self.name,                        
                "color": "#36a64f",
                "fallback": _("View sale order %s") % url_item,
                "actions": [
                    {
                        "type": "button",
                        "text": _("View sale order"),
                        "url": url_item
                    }
                ],
                "fields": [                    
                    {
                        "title": _("User"),
                        "value": self.user_id.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Customer"),
                        "value": self.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Amount untaxed"),
                        "value": aum,
                        'short': True,
                    }
                ],                    
            }
        ]
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_channel'),                                                         
        }                        
        self.env['slack.message'].sudo().create(vals)

    @api.multi
    def action_confirm(self):
        return_action_confirm = super(SaleOrder, self).action_confirm()
        if return_action_confirm:
            for obj in self:
                # claim (if exists)
                if 'claim' in obj:
                    if obj.claim:
                        obj.action_confirm_with_claim_create_message_slack()
                    else:
                        if obj.amount_total > 0:
                            obj.action_confirm_create_message_slack()
                else:
                    if obj.amount_total > 0:
                        obj.action_confirm_create_message_slack()
        # return
        return return_action_confirm
