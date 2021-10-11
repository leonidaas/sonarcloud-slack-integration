#!/usr/bin/env python3
import json
import os
import requests
from bottle import route, run, request

SLACK_SONAR_WEBHOOK_URL = os.environ["SLACK_SONAR_WEBHOOK_URL"]


@route('/sonarqube', method='POST')
def sonarqube():
    postdata = json.loads(request.body.read())
    
    result = "OK"
    text = ""
    if postdata['qualityGate']['status'] == "ERROR":
        text = "*" + postdata['project']['name'] + "*"  + " is *failing* the quality gate. "
        for item in postdata['qualityGate']['conditions']:
            text = text + "\n" + "Metric: " + item['metric']
            text = text + "\n" + "Value: " + item['value']
            text = text + "\n" + "Status: " + item['status']
            
    if postdata['qualityGate']['status'] == "OK":
        text = "*" + postdata['project']['name'] + "*" + " is *passing* the quality gate. " 
        for item in postdata['qualityGate']['conditions']:
            text = text + "\n" + "Metric: " + item['metric']
            text = text + "\n" + "Value: " + item['value']
            text = text + "\n" + "Status: " + item['status']

    send_slack_message(text)
    return result

def send_slack_message(text):
    response = requests.post(SLACK_SONAR_WEBHOOK_URL,
                             data=json.dumps({"text": text}), headers={'Content-type': 'application/json'})
    return response.text

@route('/slackmonitor')
def slackmonitor():
    response = requests.post(SLACK_SONAR_WEBHOOK_URL, data=json.dumps({"text": "Service is up and running"}), headers={'Content-type': 'application/json'})

    return response.text

@route('/monitor')
def monitor():
    return "OK"


if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=9090, debug=True)
