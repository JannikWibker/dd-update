import requests

# if not options["silent"]:

def get_zones(options, domain):
  url = domain["server"] + '/zones?name=' + domain["zone"] + '&status=active&page=1&per_page=1'
  response = requests.get(
    url,
    headers = { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' }
  )
  json = response.json()
  if json["success"] == False and options["verbose"]:
    print("something went wrong (get_zones)", json["errors"])
  if options["verbose"]: print(json["result"])
  return json["result"]["id"]


def get_records(options, domain, zone_id):
  url = domain["server"] + '/zones/' + zone_id + '/dns_records?type=A&name=' + domain["zone"] + '&page=1&per_page=1'
  response = requests.get(
    url,
    headers = { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' }
  )
  json = response.json()
  if json["success"] == False and options["verbose"]:
    print("something went wrong (get_records)", json["errors"])
  if options["verbose"]: print(json["result"])
  return json["result"]["id"]


def update_record(options, ip, domain, zone_id, record_id):
  url = domain["server"] + '/zones/' + zone_id + '/dns_records/' + record_id
  response = requests.put(
    url,
    data = { 'type': 'A', 'name': domain["zone"], 'content': ip }, 
    headers = { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' }
  )
  json = response.json()
  if json["success"] == False and options["verbose"]:
      print("something went wrong (update_record)", json["errors"])
  if options["verbose"]: print(json["result"])
  return json["result"]

def main(options, ip, domain, zone_id=None, record_id=None):
  if record_id == None:
    if zone_id == None:
      zone_id = get_zones(options, domain)
    record_id = get_records(options, domain, zone_id)
  update_record(options, ip, domain, zone_id, record_id)

__all__ = main