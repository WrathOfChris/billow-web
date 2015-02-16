from billow_web import app
import os, os.path
import yaml

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    ))
#app.config.from_object('yourapplication.default_settings')

if 'BILLOW_SETTINGS' in os.environ:
    app.config.from_envvar('BILLOW_SETTINGS')

config = {
        'title': 'billow-web',
        'logourl': '/static/AWS_Simple_Icons_AWS_Cloud.svg',
        'regions': [
                'us-east-1'
                ],
        'statsurl': 'https://yourhost.com/grafana/#/dashboard/db/instance?var-instance=',
        'links': [],
        'urls': [
            { 'name': 'us-east-1', 'url': '/#' },
            ],
        'dns': []
        }

# Load config from file
if 'BILLOW_CONFIG_FILE' in os.environ:
    if os.path.exists(os.environ['BILLOW_CONFIG_FILE']):
        with open(os.environ['BILLOW_CONFIG_FILE']) as f:
            config.update(yaml.load(f.read()))
