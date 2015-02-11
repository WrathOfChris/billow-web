from billow import billow
from flask import Flask, redirect, render_template
from pprint import pprint, pformat
import datetime
import yaml
from billow_web import app, config

def header(name=None):
    nav = {
            'name': 'billow-web',
            'logourl': '/static/AWS_Simple_Icons_AWS_Cloud.svg',
            'title': 'billow-web',
            'urls': config.config['urls']
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

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.list_services()
    svcs = list()
    for s in services:
        svc = {
                'service': s.service,
                'environ': s.environ,
                'region': s.region,
                'url': {
                    'service': '/service/%s/%s' % (s.service, s.environ),
                    'instances': '/instancestatus/%s/%s' % (s.service, s.environ),
                    'config': '/config/%s/%s' % (s.service, s.environ),
                    'stats': '/stats/%s/%s' % (s.service, s.environ),
                    'alerts': '/alerts/%s/%s' % (s.service, s.environ),
                    'visual': '/visual/%s/%s' % (s.service, s.environ)
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

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service(service)
    for s in services:
        output += render_template('service.html', service=s.config()[service])

    output += footer()
    return output

@app.route('/service/<service>/<environ>')
def service_info(service, environ):
    output = header(name='Service')

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service("%s-%s" % (service, environ))
    for s in services:
        output += render_template('service.html', service=s.config()[service])

    output += footer()
    return output

@app.route('/config/<service>/<environ>')
def service_config(service, environ):
    output = header(name='Config')

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service("%s-%s" % (service, environ))
    for s in services:
        sconfig = s.config()
        output += render_template('config.html', service=service,
                environ=environ, raw=yaml.safe_dump(sconfig,
                    encoding='utf-8', allow_unicode=True))

    output += footer()
    return output

@app.route('/instancestatus/<service>/<environ>')
def instancestatus(service, environ):
    output = header(name='InstanceStatus')

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service("%s-%s" % (service, environ))
    instances = list()
    for s in services:
        for g in s.groups:
            for i in g.instancestatus:
                i['url'] = {
                        'instance': '/instance/%s/%s/%s' % (service, environ,
                            i['id']),
                        'stats': '/stats/%s' % i['id']
                        }
                instances.append(i)
    output += render_template('instancestatus.html', service=service,
            environ=environ, instances=instances)

    output += footer()
    return output

@app.route('/instances/<service>/<environ>')
def instances(service, environ):
    output = header(name='Instances')

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service("%s-%s" % (service, environ))
    instances = list()
    for s in services:
        for g in s.groups:
            for i in g.instances:
                if i['public_ip_address']:
                    i['ip_address'] = i['public_ip_address']
                else:
                    i['ip_address'] = i['private_ip_address']
                if i['public_dns_name']:
                    i['dns_name'] = i['public_dns_name']
                else:
                    i['dns_name'] = i['private_dns_name']
                launch = datetime.datetime.strptime(i['launch_time'],
                        "%Y-%m-%dT%H:%M:%S.%fZ")
                uptime = datetime.datetime.utcnow() - launch
                i['uptime'] = str(uptime - datetime.timedelta(
                    microseconds=uptime.microseconds))
                i['url'] = {
                        'instance': '/instance/%s/%s/%s' % (service, environ,
                            i['id']),
                        'stats': '/stats/%s' % i['id']
                        }
                instances.append(i)

    output += render_template('instancelist.html', service=service,
            environ=environ, instances=instances)

    output += footer()
    return output

@app.route('/instance/<service>/<environ>/<instance>')
def instance_service_info(service, environ, instance):
    output = header(name='Instance')

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service("%s-%s" % (service, environ))

    inst = None
    for s in services:
        inst = s.get_instance(instance)
        if inst:
            output += render_template('instance.html', instance=inst,
                    service=service, environ=environ)
            break

    output += footer()
    return output

@app.route('/visual/<service>/<environ>')
def visual(service, environ):
    output = header(name='Visual')

    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service("%s-%s" % (service, environ))
    for s in services:
        output += render_template('visual.html', service=s.info()[service])

    output += footer()
    return output

# XXX TODO
@app.route('/instance/<instance>')
def instance_info(instance):
    output = header(name='Instance')

    bc = billow.billowCloud(regions=config.config['regions'])
    instances = list()
    for r in bc.regions:
        if r.region == 'us-east-1':
            instances = r.asg.get_instance(instance)
    raw = ''
    for i in instances:
        raw += pformat(vars(i))
    output += render_template('instance.html', raw=raw)

    output += footer()
    return output

# XXX TODO
@app.route('/stats/<instance>')
def stats_info(instance):
    bc = billow.billowCloud(regions=config.config['regions'])
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
