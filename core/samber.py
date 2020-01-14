
import os
import re
import conf
import xsys


# this file only exists if gatefs is mapped to //x.x.x.x/IoTGate over samba
# x.x.x.x is the ip of the iot-gate server
IOT_GATE_LOCK_FILE = ".iot-gate-lock"
# test conf if loaded
if conf.__CONF__ is None:
   conf.load()
IOT_DATA_LOCK = conf.__CONF__["dataLock"]


# checks if remote samba share is up and running
# checks if local folder is mapped to remote samba share
# checks bo looking if a remote file exists
def check_samba():
   try:
      fsgate = conf.__CONF__["gateFS"]
      if not os.path.exists(fsgate):
         return 1    # folder not found
      if not fsgate.endswith("/"):
         fsgate += "/"
      # check remote lock file
      fulpath = "%s%s" % (fsgate, IOT_DATA_LOCK)
      if not os.path.exists(fulpath):
         return 2    # lock file not found; remote fs is not mapped;
      # all is well
      return 0
   except Exception as x:
      xsys.log_error(x.message)


# writes data from arduino into a file
def write(msg):
   try:
      # only lines with # start go into lob files
      if not msg.startswith("#"):
         return
      # try write to file; set default foler;
      destfld = conf.__CONF__["gateFS"]
      # check if samaba is connected; 0 on samba is connected;
      if check_samba() != 0:
         xsys.log_error("FolderNotFound: %s" % destfld)
         destfld = conf.__CONF__["tmpDir"]
      # write to file
      __write_to_file__(destfld, msg)
   except Exception as x:
      xsys.log_error(x.message)


def __write_to_file__(destfld, msg):
   try:
      # check for \n on msg end
      if not msg.endswith("\n"):
         msg += "\n"
      # add datetime header to msg
      msg = xsys.prefix_dts_msg(msg)
      # write to file
      fullpath = __file_name__(destfld, msg)
      with open(fullpath, "a+") as f:
         f.write(msg)
   except Exception as x:
      xsys.log_error(x.message)


def __file_name__(destfld, msg):
   loc = conf.__CONF__["locID"]
   if conf.__CONF__["saveMode"] == "DEVID":
      devid = __get_devid__(msg)
      return "%s/LOC_%s_%s_utc.data" % (destfld, loc, devid)
   if conf.__CONF__["saveMode"] == "LOCID":
      return "%s/LOC_%s_utc.data" % (destfld, loc)


# grab devid from msg...
# #R1HRS|DEVID:B410.B|A0
# regex: #.*\|(DEVID:[a-zA-Z0-9\.]{4,32})\|
def __get_devid__(msg):
   rval = "NoDevID"
   rgx = r"#.*\|(DEVID:[a-zA-Z0-9\.]{4,32})\|"
   m1 = re.findall(rgx, msg)
   if len(m1) == 1:
      rval = m1[0].replace(":", "_")
   # return
   return rval
