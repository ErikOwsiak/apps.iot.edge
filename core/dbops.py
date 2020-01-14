
import time
import json as js
from core import xsys
from ast import literal_eval as make_tuple
import psycopg2
try:
   from core import xconf
except ImportError:
   import conf as xconf


# load global config file
CONF = xconf.load("conf/ttybot.conf")
COLLECTORS_DB_IDS = {}


def get_opened_conn():
   try:
      dbinfo = make_tuple(CONF["dbInfo"])
      constr = "dbname='%s' user='%s' host='%s' password='%s'" % dbinfo
      return psycopg2.connect(constr)
   except psycopg2.Error as e:
      print e


# create table collector_reads (
# 	coll_full_id varchar (128) not null,
# 	dts_bucket_15m bigint not null,
# 	readval numeric(8,2),
# 	dtc timestamp default now());
def insert_report(edgeid, collid, line):
   cur = None
   conn = None
   try:
      conn = get_opened_conn()
      # get db id for edgeid + collid
      db_rid = __get_coll_id(conn, edgeid, collid)
      # error getting row id
      if db_rid is None:
         xsys.log_error("DbNotFound: %s; %s;" % (edgeid, collid))
         return
      # get args from msg body
      dtsbucket = int(time.time() / xconf.DTS_BUCKET_15M)
      # collid, dtsbucket, pin, pinval
      args = get_query_args(line)
      buff = js.dumps(args)
      # build json string
      json = "{\"pins\": %s}" % buff
      qry = "insert into collector_reads values(%i, %i, '%s');"
      qargs = (db_rid, dtsbucket, json)
      cur = conn.cursor()
      cur.execute(qry % qargs)
      # this should be fixed later on; maybe auto commit;
      conn.commit()
   except psycopg2.Error as e:
      print e
   finally:
      # the end & close
      if cur is not None:
         cur.close()
      if conn is not None:
         conn.close()


def __get_coll_id(conn, edgeid, collid):
   global COLLECTORS_DB_IDS
   # set key value
   key = "%s#%s" % (edgeid, collid)
   if key not in COLLECTORS_DB_IDS:
      rowid = __get_coll_id_from_db(conn, edgeid, collid)
      COLLECTORS_DB_IDS[key] = rowid
   # read row id from the bucket
   rid = COLLECTORS_DB_IDS[key]
   return rid


# get collector id from database
def __get_coll_id_from_db(conn, edgeid, collid):
   rid = None
   cur = None
   try:
      tsql = "select rid from collectors c where c.edge_id = '%s' and c.collector_id = '%s';"
      sql = tsql % (edgeid, collid)
      xsys.trace2("sql: ", sql)
      # open cursor
      cur = conn.cursor()
      cur.execute(sql)
      row = cur.fetchone()
      rid = int(row[0])
   except Exception as ex:
      xsys.log_error(ex.message)
   finally:
      # close cursor
      if cur is not None:
         cur.close()
      return rid


def get_query_args(line):
   # get tokens
   tokens = tokenize(line)
   if tokens is None:
      return None
   # keep going
   head, devid, idx, body, end = tokens
   # bag = [p.split(":") for p in body.split(",")]
   arr = []
   for p in body.split(","):
      x = p.split(":")
      arr.append({x[0]: x[1]})
   return arr


def get_body(line):
   # get tokens
   tokens = tokenize(line)
   if tokens is None:
      return None
   # keep going
   head, devid, idx, body, end = tokens
   return body


def sql_insert_collector_reads(dict):
   pass


def tokenize(line):
   tokens = line.split("|")
   if len(tokens) != 5:
      return None
   # validate tokens
   head, devid, idx, body, end = tokens
   t1 = head.startswith("#")
   t2 = devid.startswith("DEVID:")
   t3 = idx.startswith("IDX:")
   # t4 is passed logiclly
   t5 = end.startswith("##")
   # all must be true to continue
   if not (t1 and t2 and t3 and t5):
      return None
   return tokens


# user:sss;pwd:asdfasf;
def __test__():
   conn = get_opened_conn()
   dir(conn)
   conn.close()
