from billow import billow
import json
import yaml
from main import app, config

def textprint(d, leader):
    output = ''
    if leader:
        leader += '.'
    if isinstance(d, dict):
        for k, v in d.iteritems():
            if isinstance(v, dict) or isinstance(v, list):
                output += textprint(v, leader + str(k))
            else:
                output += leader + str(k) + ': ' + str(v) + '\n'
    elif isinstance(d, list):
        i = 0
        for v in d:
            if isinstance(v, dict) or isinstance(v, list):
                output += textprint(v, leader + str(i))
            else:
                output += leader + str(i) + ': ' + str(v) + '\n'
            i = i + 1
    else:
        output += leader + ': ' + str(d) + '\n'

    return output

#
# /v2/services.{json,yaml,text}
#

def api_v2_services():
    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.list_services()
    output = list()
    for s in services:
        if s.service not in output:
            output.append(s.service)
    return output

@app.route('/v2/services.json')
def api_v2_services_json():
    output = api_v2_services()
    resp = app.make_response(json.dumps(output))
    resp.mimetype = "application/json"
    return resp

@app.route('/v2/services.yaml')
def api_v2_services_yaml():
    output = api_v2_services()
    resp = app.make_response(yaml.safe_dump(output, encoding='utf-8',
        allow_unicode=True))
    resp.mimetype = "text/yaml"
    return resp

@app.route('/v2/services.text')
def api_v2_services_text():
    output = api_v2_services()
    resp = app.make_response('\n'.join(output))
    resp.mimetype = "text/plain"
    return resp

#
# /v2/service/<service>.{json,yaml,text}
#

def api_v2_service(service):
    bc = billow.billowCloud(regions=config.config['regions'])
    services = bc.get_service(service)
    output = list()
    for s in services:
        output.append(s.config()[s.service])
    return output

@app.route('/v2/service/<service>.json')
def api_v2_service_json(service):
    output = api_v2_service(service)
    resp = app.make_response(json.dumps(output))
    resp.mimetype = "application/json"
    return resp

@app.route('/v2/service/<service>.yaml')
def api_v2_service_yaml(service):
    output = api_v2_service(service)
    resp = app.make_response(yaml.safe_dump(output, encoding='utf-8',
        allow_unicode=True))
    resp.mimetype = "text/yaml"
    return resp

@app.route('/v2/service/<service>.text')
def api_v2_service_text(service):
    output = api_v2_service(service)
    text = ""
    for o in output:
        text += textprint(o, '')
    resp = app.make_response(text)
    resp.mimetype = "text/plain"
    return resp
