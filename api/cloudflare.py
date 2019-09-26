import requests

# if not options["silent"]:

def get_zones(options, domain):
  url = domain["server"] + '/zones?name=' + domain["zone"] + '&status=active&page=1&per_page=1'

  if options["verbose"]:
    print("UPDATE: get_zone " + domain["zone"])
    print("UPDATE: connecting to " + url)
    print("UPDATE: using credentials \"Bearer " + domain["password"] + "\"")
  
  response = requests.get(
    url,
    headers = { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' }
  )

  if response.status_code != 200:
    if options["verbose"]:
      print("UPDATE: something went wrong (get_zones)", response.status_code, response.text)
    return
  
  json = response.json()

  if json["success"] == False and options["verbose"]:
    print("UPDATE: something went wrong (get_zones)", json["errors"])
  if options["verbose"]: print("UPDATE: RESPONSE:", json)

  return json["result"][0]["id"]


def get_records(options, domain, zone_id):
  url = domain["server"] + '/zones/' + zone_id + '/dns_records?type=A&name=' + domain["zone"] + '&page=1&per_page=1'

  if options["verbose"]:
    print("UPDATE: get_record \"A - " + domain["zone"] + "\" for zone " + zone_id)
    print("UPDATE: connecting to " + url)
    print("UPDATE: using credentials \"Bearer " + domain["password"] + "\"")

  response = requests.get(
    url,
    headers = { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' }
  )

  if response.status_code != 200:
    if options["verbose"]:
      print("UPDATE: something went wrong (get_records)", response.status_code, response.text)
    return

  json = response.json()

  if json["success"] == False and options["verbose"]:
    print("UPDATE: something went wrong (get_records)", json["errors"])
  if options["verbose"]: print("UPDATE: RESPONSE:", json)

  return json["result"][0]["id"]


def update_record(options, ip, domain, zone_id, record_id):
  url = domain["server"] + '/zones/' + zone_id + '/dns_records/' + record_id

  if options["verbose"]:
    print("UPDATE: update_record \"" + record_id + "\" in \"" + zone_id +" \" to " + ip)
    print("UPDATE: connecting to " + url)
    print("UPDATE: using credentials \"Bearer " + domain["password"] + "\"")

  response = requests.put(
    url,
    json = { 'type': 'A', 'name': domain["zone"], 'content': ip }, 
    headers = { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' }
  )

  if response.status_code != 200:
    if options["verbose"]:
      print("UPDATE: something went wrong (update_record)", response.status_code, response.text)
    return

  json = response.json()

  if json["success"] == False and options["verbose"]:
      print("UPDATE: something went wrong (update_record)", json["errors"])
  if options["verbose"]: print("UPDATE: RESPONSE:", json)

  return json["result"]

def main(options, ip, domain, zone_id=None, record_id=None):
  if record_id == None:
    if zone_id == None:
      zone_id = get_zones(options, domain)
      if(not(zone_id)): return
    record_id = get_records(options, domain, zone_id)
    if(not(record_id)): return
  update_record(options, ip, domain, zone_id, record_id)

__all__ = main