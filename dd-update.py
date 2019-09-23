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
      print("LOOKUP: [" + req.status_code + "]: " + req.text)
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
  if options["cache"] == False:
    return True
  try:
    with open(".dd-update.cache", "r") as cache_r:
      prev_ip = cache_r.readline()
      if options["verbose"]: 
        print("CACHE: previous ip was " + prev_ip)
        print("CACHE: new ip is       " + ip)
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
  if options["verbose"]: print('MAIN: ip change detected, updating domains')
  for key in domains:
    print(key)
    if domains[key]["protocol"] == 'cloudflare':

      if "zone_id" in set(domains[key]):
        if "record_id" in set(domains[key]):
          api.cloudflare.main(options, "123.45.67.89", domains[key], domains[key]["zone_id"], domains[key]["record_id"])
        else:
          api.cloudflare.main(options, "123.45.67.89", domains[key], domains[key]["zone_id"])
      else:
        api.cloudflare.main(options, "123.45.67.89", domains[key])
    else:
      if options["verbose"]: print('MAIN: currently only cloudflare protocol is supported')
else:
  if options["verbose"]: print('MAIN: no ip change detected')
  exit()

# <-- main logic

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
# - [x] if response differs from local cache update all relevant domains
# - [x] loop over all domains that need changing and:
#   - [x] figure out what protocol to use (only cloudflare is supported for now)
#   - [x] get the credentials / zone / server / ...
#   - [x] update the domain
#
# [ ] figure out how caching of "zone_id", "record_id" could work with cloudflare / cache
# [ ] 

# figure out how daemon stuff will work and if it is even needed. Could also rely on cronjobs