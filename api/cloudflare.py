import yaml
from .curl import get, put

def read_cache(filepath, is_verbose):
  try:
    with open(filepath, 'r') as cache_r:
      return yaml.load(cache_r, Loader=yaml.Loader)
  except FileNotFoundError:
    if is_verbose: print('UPDATE: Cache file not found')
    return {}

def write_cache(filepath, obj):
  cache_w = open(filepath, "w")
  yaml.dump(obj, cache_w, default_flow_style=False)


def get_zones(options, domain):
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

  return json["result"][0]["id"]


def get_records(options, domain, zone_id):
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

  # return json["result"]
  return json

def main(options, ip, domain, zone_id=None, record_id=None):

  cache = read_cache('.dd-update.cache.yml', options["verbose"])

  if domain["zone"] in cache:
    cache_domain = cache[domain["zone"]]
    if "record_id" in cache_domain:
      record_id = cache_domain["record_id"]
    if "zone_id" in cache_domain:
      zone_id = cache_domain["zone_id"]


  if record_id == None or zone_id == None:
    if zone_id == None:
      zone_id = get_zones(options, domain)
      if(not(zone_id)): return
      if domain["zone"] in cache:
        cache[domain["zone"]]["zone_id"] = zone_id
      else:
        cache[domain["zone"]] = { "zone_id": zone_id }

    if record_id == None:
      record_id = get_records(options, domain, zone_id)
      if(not(record_id)): return
      if domain["zone"] in cache:
        cache[domain["zone"]]["record_id"] = record_id
      else:
        cache[domain["zone"]] = { "record_id": record_id }

    if options["cache"]:
      write_cache('.dd-update.cache.yml', cache)

  res = update_record(options, ip, domain, zone_id, record_id)

  if res["success"] == True:
    if options["verbose"]:
      print('UPDATED {} SUCCESSFULLY'.format(domain["zone"]))
  else:
    if options["verbose"]:
      print('UPDATING OF {} FAILED'.format(domain["zone"]))

__all__ = main