from billow import billow
from flask import Flask, redirect, render_template
from pprint import pprint, pformat
import os
import yaml

app = Flask(__name__)
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
            ]
        }

def header(name=None):
    nav = {
            'name': 'billow-web',
            'logourl': '/static/AWS_Simple_Icons_AWS_Cloud.svg',
            'title': 'billow-web',
            'urls': config['urls']
            }
    if name:
        nav['title'] = name

    output = render_template('header.html')
    output += render_template('navbar.html', nav=nav)
    return output

def footer():
    output = render_template('footer.html')
    return output

@app.route("/services")
def services():
    output = header(name='Services')

    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.list_services()
    svcs = list()
    for s in services:
        svc = {
                'service': s.service,
                'environ': s.environ,
                'region': s.region,
                'url': {
                    'service': '/service/%s/%s' % (s.service, s.environ),
                    'instances': '/instances/%s/%s' % (s.service, s.environ),
                    'config': '/config/%s/%s' % (s.service, s.environ),
                    'stats': '/stats/%s/%s' % (s.service, s.environ),
                    'alerts': '/alerts/%s/%s' % (s.service, s.environ)
                    }
                }
        svcs.append(svc)
    svcs.sort(key=lambda x: x['service'])
    output += render_template('servicelist.html', services=svcs)

    output += footer()
    return output

@app.route('/service/<service>')
def service_noenv_info(service):
    output = header(name='Service')

    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.get_service(service)
    for s in services:
        config = s.config()
        output += render_template('config.html', raw=yaml.safe_dump(config,
            encoding='utf-8', allow_unicode=True))

    output += footer()
    return output

@app.route('/service/<service>/<environ>')
def service_info(service, environ):
    output = header(name='Config')

    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.get_service("%s-%s" % (service, environ))
    for s in services:
        output += render_template('service.html', service=s.config()[service])

    output += footer()
    return output

@app.route('/config/<service>/<environ>')
def service_config(service, environ):
    output = header(name='Config')

    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.get_service("%s-%s" % (service, environ))
    for s in services:
        config = s.config()
        output += render_template('config.html', raw=yaml.safe_dump(config,
            encoding='utf-8', allow_unicode=True))

    output += footer()
    return output

@app.route('/instances/<service>/<environ>')
def instances(service, environ):
    output = header(name='Instances')

    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.get_service("%s-%s" % (service, environ))
    instances = list()
    for s in services:
        for g in s.groups:
            for i in g.instances:
                i['url'] = {
                        'instance': '/instance/%s' % i['id'],
                        'stats': '/stats/%s' % i['id']
                        }
                instances.append(i)
    output += render_template('instancelist.html', instances=instances)

    output += footer()
    return output

# XXX TODO
@app.route('/instance/<instance>')
def instance_info(instance):
    output = header(name='Instance')

    bc = billow.billowCloud(regions=['us-east-1'])
    instances = list()
    for r in bc.regions:
        if r.region == 'us-east-1':
            instances = r.asg.get_instance(instance)
    raw = ''
    for i in instances:
        raw += pformat(vars(i))
    output += render_template('config.html', raw=raw)

    output += footer()
    return output

# XXX TODO
@app.route('/stats/<instance>')
def stats_info(instance):
    bc = billow.billowCloud(regions=['us-east-1'])
    instances = list()
    for r in bc.regions:
        if r.region == 'us-east-1':
            instances = r.asg.get_instance(instance)
    if not instances:
        return '', 404
    i = instances[0]

    statsurl = 'https://yourhost.com/grafana/#/dashboard/db/instance'
    return redirect("%s?var-instance=%s" % (statsurl, i.private_dns_name.split('.')[0]), 302)

@app.route("/")
def root():
    return services()

if __name__ == "__main__":
    app.run()
