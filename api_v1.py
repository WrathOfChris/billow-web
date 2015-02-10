from billow import billow
from flask import Flask, redirect, render_template
from pprint import pprint, pformat
import json
from main import app

@app.route('/v1/regions.json')
def api_v1_regions_json():
    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.list_services()
    output = list()
    for s in services:
        if s.region not in outoput:
            output.append(s.region)
    return json.dumps(output)

@app.route('/v1/services.json')
def api_v1_services_json():
    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.list_services()
    output = list()
    for s in services:
        if s.service not in output:
            output.append(s.service)
    return json.dumps(output)

@app.route('/v1/environs.json')
def api_v1_environs_json():
    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.list_services()
    output = list()
    for s in services:
        if s.environ not in output:
            output.append(s.environ)
    return json.dumps(output)

@app.route('/v1/service/<service>')
def api_v1_service():
    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.get_service(service)
    output = list()
    for s in services:
        for g in s.groups:
            for i in g.instances:
                instinfo = g.asg.get_instance(i)
                if len(str(i.public_dns_name)) > 0:
                    output.add(str(i.public_dns_name))
                else:
                    output.add(str(i.private_dns_name))
    return make_response('\n'.join(output))

@app.route('/v1/service/<service>/<environ>')
def api_v1_service_environ():
    bc = billow.billowCloud(regions=['us-east-1'])
    services = bc.get_service("%s-%s" % (service, environ))
    output = list()
    for s in services:
        for g in s.groups:
            for i in g.instances:
                instinfo = g.asg.get_instance(i)
                if len(str(i.public_dns_name)) > 0:
                    output.add(str(i.public_dns_name))
                else:
                    output.add(str(i.private_dns_name))
    return make_response('\n'.join(output))
