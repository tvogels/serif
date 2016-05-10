import collections

def merge_dictionaries(d, u):
  """
  Merge two dictionaries, overruling the first by the second.
  """
  for k, v in u.iteritems():
    if isinstance(v, collections.Mapping):
      r = merge_dictionaries(d.get(k, {}), v)
      d[k] = r
    else:
      d[k] = u[k]
  return d

def get(dictionary, *keys, **kwargs):
  # Get the default
  if 'default' in kwargs:
    default = kwargs['default']
  else:
    default = None

  current = dictionary
  for key in keys:
    if key in current:
      current = current[key]
    else:
      return default
      
  return current