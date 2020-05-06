El módulo contiene el desarrollo para implementar funcionalidades de Odoo e integrarlas con Slack https://slack.com/) a nivel de mensaje directo o en canales.

# ATENCIÓN
En el caso de que de error el addon después de instalar la libreria con: sudo pip3 install slackclient
La solución es: sudo pip3 uninstall slackcliekt y volverla a instalar (Extraño si, pero parece esa la solución: https://github.com/slackapi/python-slackclient/issues/471#issuecomment-507847909)

## odoo.conf
```
#slack
slack_bot_user_oauth_access_token=xxxxx
```

## Parámetros de configuración
```
slack_oniad_log_channel
``` 
