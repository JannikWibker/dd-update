# import requests
import yaml
from .curl import get, put

def load_cache(filepath, zone):
  try:
    with open(filepath, 'r') as cache_r
    c = yaml.load(cache_r, Loader=yaml.Loader)
    if zone in c:
      return c[zone]
  except FileNotFoundError:
    if options["verbose"]: print('UPDATE: Cache file not found')

def get_zones(options, domain):


  # if "zoneID" in load_cache('.dd-update-cache.yml', domain["zone"]):
  #   return d["zoneID"]
  
  try:
    with open(".dd-update-cache.yml", "r") as cache_r:
      c = yaml.load(cache_r, Loader=yaml.Loader)
      if domain["zone"] in c: 
        d = c[domain["zone"]]
        if "zoneID" in d:
          return d["zoneID"]

  except FileNotFoundError:
    if options["verbose"]: print("UPDATE: Cache file not found")
   
  url = domain["server"] + '/zones?name=' + domain["zone"] + '&status=active&page=1&per_page=1'

  if options["verbose"]:
    print("UPDATE: get_zone " + domain["zone"])
    print("UPDATE: connecting to " + url)
    print("UPDATE: using credentials \"Bearer " + domain["password"] + "\"")
  
  response = get(url, { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' })

  if response.status_code != 200:
    if options["verbose"]:
      print("UPDATE: something went wrong (get_zones)", response.status_code, response.text)
    return
  
  json = response.json()

  if json["success"] == False and options["verbose"]:
    print("UPDATE: something went wrong (get_zones)", json["errors"])
  if options["verbose"]: print("UPDATE: RESPONSE:", json)

  c.update({domain["zone"] : {'zoneID' : json["result"][0]["id"]}})
  cache_w = open(".dd-update-cache.yml", "w")
  yaml.dump(c, cache_w, default_flow_style=False)

  return json["result"][0]["id"]


def get_records(options, domain, zone_id):
  try:
    with open(".dd-update-cache.yml", "r") as cache_r:
      c = yaml.load(cache_r, Loader=yaml.Loader)
      if domain["zone"] in c: 
        d = c[domain["zone"]]
        if "recordID" in d:
          return d["recordID"]

  except FileNotFoundError:
    if options["verbose"]: print("UPDATE: Cache file not found")
   
  url = domain["server"] + '/zones/' + zone_id + '/dns_records?type=A&name=' + domain["zone"] + '&page=1&per_page=1'

  if options["verbose"]:
    print("UPDATE: get_record \"A - " + domain["zone"] + "\" for zone " + zone_id)
    print("UPDATE: connecting to " + url)
    print("UPDATE: using credentials \"Bearer " + domain["password"] + "\"")

  response = get(url, { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' })

  if response.status_code != 200:
    if options["verbose"]:
      print("UPDATE: something went wrong (get_records)", response.status_code, response.text)
    return

  json = response.json()

  if json["success"] == False and options["verbose"]:
    print("UPDATE: something went wrong (get_records)", json["errors"])
  if options["verbose"]: print("UPDATE: RESPONSE:", json)

  c.update({domain["zone"] : {'recordID' : json["result"][0]["id"], 'zoneID' : zone_id}})
  cache_w = open(".dd-update-cache.yml", "w")
  yaml.dump(c, cache_w, default_flow_style=False)

  return json["result"][0]["id"]


def update_record(options, ip, domain, zone_id, record_id):
  url = domain["server"] + '/zones/' + zone_id + '/dns_records/' + record_id

  if options["verbose"]:
    print("UPDATE: update_record \"" + record_id + "\" in \"" + zone_id +" \" to " + ip)
    print("UPDATE: connecting to " + url)
    print("UPDATE: using credentials \"Bearer " + domain["password"] + "\"")

  response = put(
    url,
    { 'Authorization': 'Bearer ' + domain["password"], 'Content-Type': 'application/json' },
    { 'type': 'A', 'name': domain["zone"], 'content': ip, 'proxied': True }
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