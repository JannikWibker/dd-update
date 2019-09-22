import requests

def get_zones(domain):
  url = domain.server + '/zones?name' + domain.zone + '&status=active&page=1&per_page=1'
  response = requests.get(
    url,
    headers = { 'Authorization': 'Bearer ' + domain.password, 'Content-Type': 'application/json' }
  )
  return response.json()


def get_records(domain, zone_id):
  url = domain.server + '/zones/' + zone_id + '/dns_records?type=A&name=' + domain.zone + '&page=1&per_page=1'
  response = requests.get(
    url,
    headers = { 'Authorization': 'Bearer ' + domain.password, 'Content-Type': 'application/json' }
  )
  return response.json()


def update_record(ip, domain, zone_id, record_id):
  url = domain.server + '/zones/' + zone_id + '/dns_records/' + record_id
  response = requests.put(
    url,
    data = { 'type': 'A', 'name': domain.zone, 'content': ip }, 
    headers = { 'Authorization': 'Bearer ' + domain.password, 'Content-Type': 'application/json' }
  )
  return response.json()

def main(ip, domain, zone_id=None, record_id=None):
  if record_id == None:
    if zone_id == None:
      zone_id = get_zones(domain)
    record_id = get_record(domain, zone_id)
  update_record(ip, domain, zone_id, record_id)

__all__ = main