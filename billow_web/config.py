from billow_web import app
import os

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    ))
#app.config.from_object('yourapplication.default_settings')

if 'BILLOW_SETTINGS' in os.environ:
    app.config.from_envvar('BILLOW_SETTINGS')

config = {
        'urls': [
            { 'name': 'us-east-1', 'url': '/#' },
            ],
        'regions': [
                'us-east-1'
                ]
        }
