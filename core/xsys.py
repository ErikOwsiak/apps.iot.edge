
import re
import os
import conf
import datetime as dt


# adds datetime prefix to msg
def prefix_dts_msg(msg):
   dts = dt.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
   return "[%s] %s" % (dts, msg)


def fix_msg_for_file(msg):
   dts = dt.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
   return "[%s] %s\n" % (dts, msg)


def get_dts_file_name(ext):
   dts = dt.datetime.utcnow().strftime("%Y-%m-%d")
   return "TMP_%s.%s" % (dts, ext)


# simple error logger
def log_error(msg, mode="a+"):
   try:
      if conf.__DEBUG__:
         print "log_error:\n\t%s" % msg
      loc = conf.__CONF__["edgeID"]
      with open("logs/errors.%s.log" % loc, mode) as f:
         buff = prefix_dts_msg(msg)
         if not buff.endswith("\n"):
            buff += "\n"
         f.write(buff)
   except Exception as ex:
      # if shit goes bad!
      os.system("echo -e '\n+ + + +' >> /var/log/iot/edge.log")
      os.system("date >> /var/log/iot/edge.log")
      os.system("echo '%s' >> /var/log/iot/edge.log" % ex.message)


def is_admin():
   try:
      with open("logs/is_admin.log", "w") as f:
         f.write("AdminTest")
      return True
   except IOError as e:
      print "IOError: %s" % e
      return False


def trace1(msg):
   if not conf.__TRACE__:
      return
   print "\t%s" % msg


def trace2(msg, obj):
   if not conf.__TRACE__:
      return
   print "\n- - - TraceIsOn - - -"
   print "\t%s" % msg
   print "\t%s" % obj


# ...#R5MIN|DEVID:B410.A|IDX:0|...
def get_collector_id(line):
   rgx = r".*\|DEVID:([A-Z0-9\.]{2,24})\|"
   m = re.findall(rgx, line)
   if len(m) != 1:
      return None
   return str(m[0])


def setup_env():
   # create /var/log/iot folder
   varlog = "/var/log/iot"
   if not os.path.exists(varlog):
      os.mkdir(varlog)
   if os.path.exists(varlog):
      print "/var/log/iot -> ok"
