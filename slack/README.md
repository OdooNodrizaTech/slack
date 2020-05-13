El módulo contiene el desarrollo para implementar funcionalidades de Odoo e integrarlas con Slack https://slack.com/) a nivel de mensaje directo o en canales.

Será necesario crear una app en https://api.slack.com/apps/ en el espacio de trabajo que queramos trabajar y definirle de nombre: Odoo y los scopes: channels:read + chat:write

Para el correcto funcionamiento de Slack en los canales, será necesario que dentro del canal, en "Más" pulsemos en "Añadir aplicaciones" y tengamos añadida la aplicación de Odoo previamente creada.

## odoo.conf
```
#slack
slack_bot_user_oauth_access_token=xxxxx
```

## Parámetros de configuración
```
slack_oniad_log_channel
``` 
