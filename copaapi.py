import json
import urllib3
import requests

def req_api(container_pool, container_name, operation, parameters={}):
    url = 'http://localhost:8000/core/containers_list/api/'
    new_req = {}
    new_req["container_pool"] = container_pool
    new_req["container_name"] = container_name
    new_req["operation"] = operation

    for key in parameters:
        new_req[key] = parameters[key]
        #print parameters[key]

    #data = {'container_pool': container_pool, 'container_name': container_name, 'operation': operation, 'cmd': ['ifconfig']}
    # data = {'container_pool':'Server1', 'container_name':'RX1', 'operation':'images_list', }

    data = new_req
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}


    r = requests.post(url, data=json.dumps(data), headers=headers).json()

    return r

#oper = {}
#oper['cmd'] = ['ls', '-la']
#print oper
#req_api("Server1","RX","information",oper)

#a = req_api("Server1","RX","information")
#print a['result']['network']['eth0']['counters']['packets_received']

#print req_api("Server1", "RX", "migrate", {"destination_pool": "Server2"})

#print req_api("Server1", "VideoServer", "information")

#print req_api("Server1", "VideoServer", "information")['result']['network']['eth0']['counters']['packets_received']
