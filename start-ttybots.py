#!/usr/bin/python

import os
import ast
import time
import setproctitle
import multiprocessing as mp
import ttybot
import core.conf as conf
import core.xsys as xsys
import core.dbops as dbops


PROCS = []
CONF = conf.load()
START_FOLDER = os.getcwd()
PORTS = None
# 30 secs
MAIN_DELAY = 30


def start_ports():
   try:
      global PROCS, PORTS
      xsys.trace1("\n- - - starting ports - - -")
      PORTS = ast.literal_eval(conf.__CONF__["devPorts"])
      # for each port
      for dev in PORTS:
         try:
            if not check_tty_dev(dev):
               continue
            # start process
            name = dev.replace("/dev/", "")
            p = mp.Process(name=name, target=ttybot.main, args=("d", dev, None))
            p.start()
            xsys.trace2("PID:", "\t%s" % p.pid)
            PROCS.append(p)
            time.sleep(0.480)
         except Exception as x:
            xsys.log_error(x.message)
      # save to file new on each start & return
      safe_pids()
      return True
   except Exception as x:
      xsys.log_error(x.message)
      return False


def check_tty_dev(dev):
   print "\n- - - - - -"
   print "checking dev: %s" % dev
   if os.path.exists(dev):
      print " --> DevFound"
      return True
   else:
      print " --> DevNotFound"
      return False


def main():
   try:
      # setup env
      xsys.setup_env()
      # mark start
      os.system("date > /var/log/iot/edge-start.log")
      # test for admin
      if not xsys.is_admin():
         print "Run program as admin: sudo ./start-ttybots.py"
         exit(1)
      # test database
      if not dbops.test_database():
         print "DatabaseNotFound: %s" % conf.__CONF__["dbInfo"]
         exit(1)
      # keep going
      if not start_ports():
         xsys.log_error("UnableToStartPorts!")
         exit(1)
      # start scanning rxtx procs
      while True:
         try:
            print "--- start process main ----"
            xsys.trace1("MAIN PID: %s" % os.getpid())
            for p in PROCS:
               xsys.trace1("\tSUB PID: %s" % p.pid)
            time.sleep(MAIN_DELAY)
         except Exception as ex:
            xsys.log_error(ex.message)
   except Exception as ex:
      # if shit goes bad!
      os.system("echo -e '\n+ + + +' >> /var/log/iot/edge.log")
      os.system("date >> /var/log/iot/edge.log")
      os.system("echo '%s' >> /var/log/iot/edge.log" % ex.message)


def safe_pids():
   pidsfile = "logs/pids.log"
   if os.path.exists(pidsfile):
      os.unlink(pidsfile)
   with open(pidsfile, "w") as f:
      f.write("*%s\n" % os.getpid())
      for proc in PROCS:
         f.write("**%s\n" % proc.pid)
   # end


if __name__ == "__main__":
   # start main
   try:
      setproctitle.setproctitle("ttybots/START")
   except Exception as x:
      xsys.log_error(x.message)
   # start main
   main()
