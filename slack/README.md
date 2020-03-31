El módulo contiene el desarrollo para implementar funcionalidades de Odoo e integrarlas con Slack https://slack.com/) a nivel de mensaje directo o en canales.

## odoo.conf
```
#slack
slack_bot_user_oauth_access_token=xxxxx
```

## Parámetros de configuración
```
slack_oniad_log_channel
slack_oniad_log_contabilidad_channel
slack_oniad_log_ses_mail_tracking_channel
slack_oniad_log_calidad_channel
slack_oniad_cesce_channel
``` 

account.invoice (Facturas):

Implementa la acción action_auto_create_message_slack que sirve para notificar al canal configurado en slack_oniad_log_contabilidad_channel de una nueva factura creada automáticamente (https://grupoarelux.atlassian.net/wiki/spaces/O/pages/322011935/oniad+autogenerate+sales - We couldn't find this link  )

 

crm.lead (Leads):

Implementa la acción action_leads_create_sendinblue_list_id que sirve para notificar al canal configurado en slack_oniad_log_channel de una nueva iniciativa/oportunidad desde Sendinblue (https://grupoarelux.atlassian.net/wiki/spaces/O/pages/322240845/oniad+sendinblue - We couldn't find this link  )

 

mail.mail (Email):

Optimiza la acción _postprocess_sent_message para que si no se puede enviar el email y se procude un error, notifique del error.


mail.message (Mensaje):

Implementa la acción generate_auto_starred_slack que sirve para notificar al usuario en Odoo SOLO si tiene activo el campo slack_member_id y activo slack_mail_message en el apartado del usuario. Cada mensaje le llegaría como mensaje directo a el envíado por "SlackBot" (https://grupoarelux.atlassian.net/wiki/spaces/O/pages/322339152/oniad+mail+auto+starred - We couldn't find this link  )


slack.message:

Modelo que sirve de intermediario para en la acción de create envíe el mensaje correspondiente a través de Slack
