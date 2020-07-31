# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        # need_slack
        credit_limit_old = self.credit_limit
        if 'cesce_risk_state' in vals:
            cesce_risk_state_old = self.cesce_risk_state
        # super
        return_object = super(ResPartner, self).write(vals)
        # need_slack
        if 'cesce_risk_state' in vals:
            credit_limit = self.credit_limit
            cesce_risk_state = self.cesce_risk_state
            # 1er classification_error
            first_classification_error = False
            if cesce_risk_state == 'classification_error' \
                    and cesce_risk_state_old != cesce_risk_state:
                first_classification_error = True
                self.action_send_cesce_risk_classification_error_message_slack()
            # 1er classification_ok
            first_classification_ok = False
            if cesce_risk_state == 'classification_ok' \
                    and cesce_risk_state_old != cesce_risk_state:
                first_classification_ok = True
                self.action_send_cesce_risk_classification_message_slack()
            # credit_limit change
            if not first_classification_ok and not first_classification_error:
                if credit_limit_old != credit_limit:
                    self.action_send_cesce_risk_classification_update_message_slack()
        # return
        return return_object

    @api.multi
    def action_send_cesce_risk_classification_error_message_slack(self):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=res.partner' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": _('Cesce Risk Error'),
                "text": self.cesce_error,
                "color": "#ff0000",
                "fallback": _("View contact %s %s") % (
                    self.name,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _("View contact %s") % self.name,
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Contact"),
                        "value": self.name,
                        'short': True,
                    },
                    {
                        "title": _("Amount requested"),
                        "value": self.cesce_amount_requested,
                        'short': True,
                    }
                ],
            }
        ]
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_cesce_channel'
            ),
        }
        self.env['slack.message'].sudo().create(vals)

    @api.multi
    def action_send_cesce_risk_classification_message_slack(self):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=res.partner' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": _('Cesce Riesgo Allowed'),
                "text": self.name,
                "color": "#36a64f",
                "fallback": _("View contact %s %s") % (
                    self.name,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _("View contact %s") % self.name,
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Amount requested"),
                        "value": self.cesce_amount_requested,
                        'short': True,
                    },
                    {
                        "title": _("Credit limit"),
                        "value": self.credit_limit,
                        'short': True,
                    }
                ],
            }
        ]
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_cesce_channel'
            ),
        }
        self.env['slack.message'].sudo().create(vals)

    @api.multi
    def action_send_cesce_risk_classification_update_message_slack(self):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=res.partner' % (
            web_base_url,
            self.id
        )
        # define
        fecha_efecto = ''
        fecha_anulacion = ''
        # cesce_risk_classification_ids
        classification_ids = self.env['cesce.risk.classification'].sudo().search(
            [
                ('partner_id', '=', self.id)
            ],
            order="fecha_efecto desc",
            limit=1
        )
        if classification_ids:
            fecha_efecto = classification_ids[0].fecha_efecto
            fecha_anulacion = classification_ids[0].fecha_anulacio
        # attachments
        attachments = [
            {
                "title": _('Cesce Risk update'),
                "text": self.name,
                "color": "#36a64f",
                "fallback": _("View contact %s %s") % (
                    self.name,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _("View contact %s") % self.name,
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Cesce risk state"),
                        "value": self.cesce_risk_state,
                        'short': True,
                    },
                    {
                        "title": _("Credit limit"),
                        "value": self.credit_limit,
                        'short': True,
                    },
                    {
                        "title": _("Effect date"),
                        "value": fecha_efecto,
                        'short': True,
                    },
                    {
                        "title": _("Cancellation date"),
                        "value": fecha_anulacion,
                        'short': True,
                    }
                ],
            }
        ]
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_cesce_channel'
            ),
        }
        self.env['slack.message'].sudo().create(vals)
