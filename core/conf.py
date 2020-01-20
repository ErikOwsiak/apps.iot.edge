
import os


__CONF__ = None
__DEBUG__ = False
__TRACE__ = False
DTS_BUCKET_15M = 900
MINUTE_SECS = 60
# store start folder
START_DIR = os.getcwd()


def load(filepath="conf/ttybot.conf"):
   global __CONF__, __DEBUG__, __TRACE__
   if not os.path.exists(filepath):
      return None
   with open(filepath, "r") as f:
      lines = f.readlines()
   __CONF__ = {}
   for ln in lines:
      if ln.startswith("#"):
         continue
      key, val = ln.split("=")
      __CONF__[key] = val.strip()
   # return dictionary
   if __CONF__["__debug__"] == "T":
      __DEBUG__ = True
   if __CONF__["__trace__"] == "T":
      __TRACE__ = True
   # return object
   return __CONF__
