import subprocess
import json

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

flatten = lambda l: [item for sublist in l for item in sublist]

def request(method, url, headers={}, payload=None):
  header_list = flatten([['-H', '{}: {}'.format(header, headers[header])] for header in headers])

  result = ''
  
  if payload:
    result = subprocess.check_output(['curl', '-X', method, '-s', '-w', '\n%{content_type}\n%{response_code}', url, *header_list, '--data', json.dumps(payload)]).decode('utf-8')
  else:
    result = subprocess.check_output(['curl', '-X', method, '-s', '-w', '\n%{content_type}\n%{response_code}', url, *header_list]).decode('utf-8')

  print(result)

  lines = result.splitlines()
  content_type = lines[-2]
  status_code = int(lines[-1]) # also called response_code
  del lines[-2]
  del lines[-1]

  response = '\n'.join(lines)

  return dotdict({ 'json': lambda : json.loads(response), 'status_code': status_code, 'content_type': content_type })

def get(url, headers={}):
  return request('GET', url, headers)

def post(url, headers={}, payload=None):
  return request('POST', url, headers, payload)

def patch(url, headers={}, payload=None):
  return request('PATCH', url, headers, payload)

def put(url, headers={}, payload=None):
  return request('PUT', url, headers, payload)

def delete(url, headers={}, payload=None):
  return request('DELETE', url, headers, payload)
