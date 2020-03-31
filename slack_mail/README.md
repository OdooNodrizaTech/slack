Se optimiza lo relativo a mail tomando como base el addon Slack enviando notificaciones para acciones personalizadas.

## Parámetros de configuración
```
slack_oniad_log_ses_mail_tracking_channel
```

## mail.mail (Email)

Optimiza la acción _postprocess_sent_message para que si no se puede enviar el email y se procude un error, notifique del error.


## mail.message (Mensaje)

Implementa la acción generate_auto_starred_slack que sirve para notificar al usuario en Odoo SOLO si tiene activo el campo slack_member_id y activo slack_mail_message en el apartado del usuario. Cada mensaje le llegaría como mensaje directo a el envíado por "SlackBot" (https://grupoarelux.atlassian.net/wiki/spaces/O/pages/322339152/oniad+mail+auto+starred - We couldn't find this link  )
