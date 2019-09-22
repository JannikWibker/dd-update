import yaml
import requests
import argparse
import api

# >-- parsing command line arguments

parser = argparse.ArgumentParser(description='dd-update', prog='dd-update')
parser.add_argument('--verbose', '-v',  action='store_true',                help='wether or not to print debug information')
parser.add_argument('--domain', '-d',   metavar='<url>',        type=str,   help='specific domain to update if needed')
parser.add_argument('--force', '-f',    action='store_true',                help='force update; ignore cached value')
parser.add_argument('--no_cache',       action='store_true',                help='if present don\'t write to cache')
parser.add_argument('--config', '-c',   metavar='<file path>',  type=str,   default='./dd-update.yml', help='specify the path to the configuration file')
parser.add_argument('--daemon',         metavar='<seconds>',    type=int,   help='wether to run as a daemon or not; if yes then argument is timeout between updates')
parser.add_argument('--version',        action='store_true',                help='print the current version')

args = parser.parse_args()

if args.version:
  print('dd-update version 1.0')
  exit()

# <-- parsing command line arguments

# >-- loading config file and handling default values

try:
  with open(args.config, "r") as config:
    print("file found")

except FileNotFoundError:
  open(args.config, "w")
  print("created empty config file dd-update.yml")
  exit()

f = open(args.config, "r")

#if f.read() == "":
#  print("config file is empty")
#  exit()

o = yaml.load(f, Loader=yaml.Loader)

if o == None:
  print("config error: no yml found")
  exit()

if "options" not in o:
  print("config error: no options found")
  exit()

options = o["options"]

s_options = set(options)

if 'domain' not in s_options:
  options["domain"] = ''

if 'use' not in s_options:
  options["use"] = 'web'

if 'web' not in s_options and options['use'] == 'web':
  print('config error: using web but web not specified')
  exit()

if 'verbose' not in s_options:
  options["verbose"] = False

if 'cache' not in s_options:
  options["cache"] = True

if args.verbose:
  options["verbose"] = args.verbose

if args.force:
  options["force"] = args.force

if args.domain:
  options["domain"] = args.domain

if args.no_cache:
  options["cache"] = not(args.no_cache)

#print(args)
# print(options)

# <-- loading config file and handling default values

# >-- filtering out which domains to update

domains = {}

if options["domain"] and options["domain"] != '':
  if o[options["domain"]]:
    domains[options["domain"]] = o[options["domain"]]
  else:
    print('config error: could not update requested domain, not listed in config file')
    exit()
else:
  domains = o
  del domains["options"]

print(domains)

# <-- filtering out which domains to update

# >-- ip lookup function

def ip_lookup():
  if options["use"] == "web" and options["web"] != None:
    req = requests.get(options["web"])
    print(req, req.text, req.status_code)
    if req.status_code != 200:
      print("something went wrong")
      exit()
    else:
      print("ip address is " + req.text)
      return req.text
  else:
    print("not using web")

# <-- ip lookup function

# >-- cache function

def check_cache(ip):
  if options["cache"] == False:
    return True
  try:
    with open(".dd-update.cache", "r") as cache_r:
      prev_ip = cache_r.readline()
      print("previous ip was" + prev_ip)
      if prev_ip != ip:
       cache_w = open(".dd-update.cache", "w")
       cache_w.write(ip)
       return False
      else:
        return True

  except FileNotFoundError:
   cache_w = open(".dd-update.cache", "w")
   cache_w.write(ip)
   return False

# <-- cache function

# >-- main logic

# new_ip = ip_lookup()

#if check_cache(new_ip):
if True:
  print('ip change detected, updating domains')
  for key in domains:
    print(key)
    if domains[key]["protocol"] == 'cloudflare':
      
      if "zone_id" in set(domains[key]):
        if "record_id" in set(domains[key]):
          api.cloudflare.main("123.45.67.89", domains[key], domains[key]["zone_id"], domains[key]["record_id"])
        else:
          api.cloudflare.main("123.45.67.89", domains[key], domains[key]["zone_id"])
      else:
        api.cloudflare.main("123.45.67.89", domains[key])
    else:
      print('currently only cloudflare protocol is supported')
else:
  print('no ip change detected')
  exit()

# <-- main logic

# for key in o:
#   print(key)
#   print(o[key])


# url = 'https://...'
# payload = open("request.json")
# headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# r = requests.post(url, data=payload, headers=headers)

# requests:
# request.get(url, headers=headers)
# request.post(url, data=payload, headers=headers)

# -> 
# response object
# - .status_code
# - .headers
# - .text

# structure:
# - [x] parsing command line arguments
#   - [x] --verbose, --domain=<key>, --force, --no_cache, --daemon=<time>, --config=<file path>, --version, ...
# - [x] looking which domains should (/could) be updated (either all or the specified one)
# - [x] get ip address using ip_lookup()
# - if response differs from local cache update all relevant domains
# - loop over all domains that need changing and:
#   - figure out what protocol to use (only cloudflare is supported for now)
#   - get the credentials / zone / server / ...
#   - update the domain

# figure out how daemon stuff will work and if it is even needed. Could also rely on cronjobs