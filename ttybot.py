
import os
import sys
import time
import serial
import threading
import psutil
import setproctitle
import core.conf as conf
import core.samber as samber
import core.xsys as xsys
import core.dbops as dbops


TTY_USB_PORT = None
TTY_BAUDRATE = 57600
PORT_ID = None
PORT = None
EDGE = None
FILE_IN = ""
FILE_OUT = ""
CONF_FILE = "conf/ttybot.conf"


# these msg go into local out file for given tty port
# OUTMSGS = ["#DEBUG", "#RDEBUG", "#DEVID", "#HELLO"]
# only forward these msgs to data files
LOGMSGS = ["#R5MIN", "#R10MIN", "#R15MIN", "#R1HRS"]
__CONF__ = None


def run():
   try:
      global PORT
      print "\n -- SPEED: %s; PORT: %s; PORT_ID: %s; --\n" % (TTY_BAUDRATE, TTY_USB_PORT, PORT_ID)
      PORT = serial.Serial(TTY_USB_PORT, TTY_BAUDRATE)
      # start cmd in thread
      t = threading.Thread(name=PORT_ID, target=in_thread, args=(PORT,))
      t.start()
      # keep going
      if not PORT.is_open:
         PORT.open()
      if PORT.is_open:
         print "\n --- PortIsOpen ---\n"
         read_port()
      else:
         xsys.log_error("can't open port: %s\nexit" % PORT)
   except Exception as x:
      xsys.log_error(x.message)
      time.sleep(conf.MINUTE_SECS)


def read_port():
   while True:
      try:
         print "Awaiting RxTx:"
         # clean up the string
         line = PORT.readline().strip()
         # ignore empty lines
         if line == "":
            continue
         # look for start header
         test_msg_header(line)
         # keep going
         print line
         collid = xsys.get_collector_id(line)
         if test_msg(line):
            # store buffer that just came in
            if __CONF__["mode"] == "samba":
               samber.write(line)
            if __CONF__["mode"] == "db":
               # save direct to db on the GATE
               dbops.insert_report(EDGE, collid, line)
            if __CONF__["mode"] == "local":
               pass
         else:
            # write to tty out file
            buff = xsys.prefix_dts_msg(line)
            with open(FILE_OUT, "a+") as f:
               f.write("%s\n" % buff)
      except Exception as x:
         xsys.log_error(x.message)


def read_line_args():
   global TTY_USB_PORT, TTY_BAUDRATE, PORT_ID
   if len(sys.argv) != 3:
      errmsg = "WrongNumberOfArgs: %s" % len(sys.argv)
      raise Exception(errmsg)
   # set baude rate; d is default;
   if sys.argv[1] != "d":
      TTY_BAUDRATE = int(sys.argv[1])
   # read port
   TTY_USB_PORT = sys.argv[2]
   PORT_ID = TTY_USB_PORT.split("/")[2]


def setup():
   global FILE_IN, FILE_OUT, PORT, __CONF__, EDGE
   FILE_IN = "inout/%s.in.buff" % PORT_ID
   FILE_OUT = "inout/%s.out.buff" % PORT_ID
   if not os.path.exists(FILE_IN):
      os.system("touch %s " % FILE_IN)
   if not os.path.exists(FILE_OUT):
      os.system("touch %s " % FILE_OUT)
   # load conf file
   __CONF__ = conf.load(CONF_FILE)
   EDGE = __CONF__["edgeID"].strip()
   print (__CONF__, conf.START_DIR, EDGE)
   # set proc name
   set_proc_name()


def in_thread(port):
   xsys.trace1("\n--- in_thread: [%s] ---\n\n" % PORT_ID)
   # thread loop
   while True:
      try:
         if os.path.getsize(FILE_IN) > 4:
            with open(FILE_IN, "rw+") as f:
               line = f.readline()
               xsys.trace2("LineIn: %s", line)
               f.truncate(0)
            if line != "":
               if not line.endswith('\n'):
                  line += "\n"
               xsys.trace2("PushingBuff: ", line)
               port.write(line.encode("utf-8"))
         time.sleep(4.0)
      except Exception as x:
         xsys.log_error(x.message)


def main(baudrate, port, stdout=None):
   global TTY_USB_PORT, TTY_BAUDRATE, PORT_ID
   # set baude rate; d is default;
   if baudrate != "d":
      TTY_BAUDRATE = baudrate
   # read port
   TTY_USB_PORT = port
   PORT_ID = TTY_USB_PORT.split("/")[2]
   # set stdout
   if stdout is not None:
      sys.stdout = stdout
   # start process
   setup()
   run()


def test_msg(line):
   if line.startswith("#R"):
      return True
   if line.startswith("#HELLO"):
      return True
   return False


def set_proc_name():
   try:
      tmp = PORT_ID.replace("tty", "ttybot/")
      setproctitle.setproctitle(tmp)
   except Exception as x:
      xsys.log_error(x.message)


def update_proc_name(msg):
   try:
      proc = psutil.Process(os.getpid())
      pname = proc.name()
      setproctitle.setproctitle("%s/%s" % (pname, msg))
   except Exception as x:
      xsys.log_error(x.message)


def test_msg_header(line):
   try:
      pass
      # #START|DEVID:B410.B|##
      # if line.startswith("#START"):
      #   update_proc_name(line.split("|")[1])
   except Exception as x:
      xsys.log_error(x.message)


# -----------------------------------------------------------------------------
# start
if __name__ == "__main__":
   read_line_args()
   # print info
   if conf.__DEBUG__:
      print "DebugIsOn"
   if conf.__TRACE__:
      print "TraceIsOn"
   # start process
   setup()
   run()
