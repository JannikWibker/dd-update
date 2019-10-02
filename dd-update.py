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
#parser.add_argument('--daemon',         metavar='<seconds>',    type=int,   help='wether to run as a daemon or not; if yes then argument is timeout between updates')
parser.add_argument('--version',        action='store_true',                help='print the current version')
parser.add_argument('--silent', '-s',   action='store_true',                help='wether or not to disable ALL output, even if it is important')

args = parser.parse_args()

if args.version:
  print('dd-update version 1.0')
  exit()

# <-- parsing command line arguments

# >-- loading config file and handling default values

# maybe open with read/write in order to not have to rewrite file every time; would have to implement custom create file code

try:
  with open(args.config, "r") as config:
    if(args.verbose):
      if not args.silent: print("config file found")

except FileNotFoundError:
  open(args.config, "w")
  if not args.silent:
    print("created empty config file " + args.config)
    if args.config != "./dd-update.yml":
      print("file path of created config file differs from default, the \"--config=" + args.config + "\" option is thereby required")
  exit()

f = open(args.config, "r")

o = yaml.load(f, Loader=yaml.Loader)

if o == None:
  if not args.silent: print("config error: no yml found")
  exit()

if "options" not in o:
  if not args.silent: print("config error: no options found")
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

if args.silent:
    options["silent"] = args.silent
else:
  options["silent"] = False

if options["verbose"] and options["silent"]:
    options["silent"] = False

if not(options["web"].startswith("https://")) and not(options["web"].startswith("http://")):
   options["web"] = "https://" + options["web"]

# <-- loading config file and handling default values

# >-- filtering out which domains to update

domains = {}

if options["domain"] and options["domain"] != '':
  if o[options["domain"]]:
    domains[options["domain"]] = o[options["domain"]]
  else:
    if not options["silent"]: print('config error: could not update requested domain, not listed in config file')
    exit()
else:
  domains = o
  del domains["options"]

for key in domains:
   if not(domains[key]["server"].startswith("https://")) and not(domains[key]["server"].startswith("http://")):
    if not(domains[key]["ssl"]):
      domains[key]["server"] = "http://" + domains[key]["server"]
    else:
      domains[key]["server"] = "https://" + domains[key]["server"]
   
if options["verbose"]:
  print("domains to update:")
  for domain_name in set(domains):
    print(domain_name)

# <-- filtering out which domains to update

# >-- ip lookup function

def ip_lookup():
  if options["use"] == "web" and options["web"] != None:
    req = requests.get(options["web"])
    if options["verbose"]: 
      print("LOOKUP: [" + str(req.status_code) + "]: " + req.text)
    if req.status_code != 200:
      if not options["silent"]: print("LOOKUP: something went wrong while looking up the new ip address")
      exit()
    else:
      return req.text
  else:
    if options["verbose"]: print("LOOKUP: not using web; no-op; not implemented")

# <-- ip lookup function

# >-- cache function

def check_cache(ip):
  if options["force"] == True:
    return True
  try:
    with open(".dd-update.cache.yml", "r") as cache_r:
      c = yaml.load(cache_r, Loader=yaml.Loader)
      prev_ip = c["ip"]
      if options["verbose"]: 
        print("CACHE: previous ip was " + prev_ip)
        print("CACHE: new ip is       " + ip)
      if prev_ip != ip:
       cache_w = open(".dd-update.cache.yml", "w")
       c["ip"] = ip
       yaml.dump(c, cache_w, default_flow_style=False)
       return True
      else:
        return False

  except FileNotFoundError:
    if options["cache"]:
      cache_w = open(".dd-update.cache.yml", "w")
      yaml.dump(dict(ip = ip), cache_w, default_flow_style=False)

    return True

# <-- cache function

# >-- main logic

new_ip = ip_lookup()

if check_cache(new_ip):
  if options["verbose"]: print('MAIN: ip change detected, updating domains')
  for key in domains:
    print(key)
    if domains[key]["protocol"] == 'cloudflare':

      if "zone_id" in set(domains[key]):
        if "record_id" in set(domains[key]):
          api.cloudflare.main(options, new_ip, domains[key], domains[key]["zone_id"], domains[key]["record_id"])
        else:
          api.cloudflare.main(options, new_ip, domains[key], domains[key]["zone_id"])
      else:
        api.cloudflare.main(options, new_ip, domains[key])
    else:
      if options["verbose"]: print('MAIN: currently only cloudflare protocol is supported')
else:
  if options["verbose"]: print('MAIN: no ip change detected')
  exit()

# <-- main logic

# structure:
# - [x] parsing command line arguments
#   - [x] --verbose, --domain=<key>, --force, --no_cache, --daemon=<time>, --config=<file path>, --version, ...
# - [x] looking which domains should (/could) be updated (either all or the specified one)
# - [x] get ip address using ip_lookup()
# - [x] if response differs from local cache update all relevant domains
# - [x] loop over all domains that need changing and:
#   - [x] figure out what protocol to use (only cloudflare is supported for now)
#   - [x] get the credentials / zone / server / ...
#   - [x] update the domain
#
# [ ] figure out how caching of "zone_id", "record_id" could work with cloudflare / cache
# [ ] figure out if the config file location is good, shouldn't it maybe be inside of /etc/ by default; 
#     where should dd-update be located after installing? just it's own directory or somewhere else? 
#     if somewhere else consider using /etc/ for the config file
