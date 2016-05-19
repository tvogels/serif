import os
import pickle
import hashlib
import json

class SerifCache(object):

  def __init__(self, cache_file):
    self.cache_file = cache_file
    self.init_cache()

  def init_cache(self):
    if os.path.isfile(self.cache_file):
      self.data = pickle.load(open(self.cache_file, 'rb'))
    else:
      self.data = {}

  def persist(self):
    directory = os.path.dirname(self.cache_file)
    if not os.path.isdir(directory):
      os.makedirs(directory)
    pickle.dump(self.data, open(self.cache_file, 'wb'))

  def hash(self, args, kwargs):
    m = hashlib.md5()
    for arg in args:
      m.update(arg)
    m.update(json.dumps(kwargs))
    return m.digest()

  def __call__(self, fnc_name):

    if fnc_name not in self.data:
      self.data[fnc_name] = {}

    def decorator(fnc):
      def wrapper(*args, **kwargs):
        key = self.hash(args,kwargs)
        if key in self.data[fnc_name]:
          return self.data[fnc_name][key]
        else:
          res = fnc(*args, **kwargs)
          self.data[fnc_name][key] = res
        return res
      return wrapper
    return decorator