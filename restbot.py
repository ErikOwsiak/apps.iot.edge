
import os
import pycurl
import StringIO


g_my_loc_key = "../.conf/location"
g_my_loc_val = ""             # type: str
g_home_key = "../.conf/home"
g_home_val = ""               # type: str
g_gate_ip_key = "../.conf/iot-gate-ip"
g_gate_ip_val = ""            # type: str
g_base_url_key = "../.conf/base-url"
g_base_url_val = ""           # type: str


def do_setup():
   # pull globals
   global g_my_loc_key, g_home_key, g_gate_ip_key, g_post_reads_url_key, \
      g_my_loc_val, g_home_val, g_gate_ip_val, g_base_url_val
   try:
      # load values
      with open(g_my_loc_key, "r") as f:
         g_my_loc_val = f.readline().strip()
      with open(g_home_key, "r") as f:
         g_home_val = f.readline().strip()
      with open(g_gate_ip_key, "r") as f:
         g_gate_ip_val = f.readline().strip()
      with open(g_base_url_key, "r") as f:
         g_base_url_val = f.readline().strip()
      return True
   except Exception as x:
      # todo: save x to file
      print x
      return False


def send_to_gate(msg):
   print "msg: %s" % msg
   if not do_setup():
      return False
   # pull globals
   global g_my_loc_key, g_home_key, g_gate_ip_key, g_base_url_key, \
      g_my_loc_val, g_home_val, g_gate_ip_val, g_base_url_val
   try:
      # insert ip into the url
      # url = g_base_url_val % g_gate_ip_val
      url = "http://188.252.121.194:10080/iot-gate/ops/postBuffer"
      # print "url: %s" % url
      res = StringIO.StringIO()
      curl = pycurl.Curl()
      curl.setopt(pycurl.URL, url)
      curl.setopt(pycurl.HTTPHEADER, ["Content-Type: text/iot-buffer"])
      curl.setopt(pycurl.WRITEFUNCTION, res.write)
      curl.setopt(pycurl.POST, 1)
      curl.setopt(pycurl.POSTFIELDS, msg)
      # post
      curl.perform()
      # read code
      code = curl.getinfo(pycurl.HTTP_CODE)
      if code != 200:
         pass
      else:
         pass
      curl.close()
      val = res.getvalue()
      res.close()
      return code, val
   except Exception as x:
      print x
      return False
