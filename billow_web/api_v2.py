from billow import billow
import json
import yaml
from main import app, config

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
