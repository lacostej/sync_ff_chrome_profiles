'''
One way sync passwords from Firefox to Chrome profile

Author: jerome.lacoste@gmail.com
'''
import sys
import os
import shutil

ff_dump_exe = 'ff_key3db_dump'


def load_ff_pwds(ff_csv):
  '''load a CSV file as dumped by the ff_dump_exe program. Returns an array containing:
0  hostname           TEXT NOT NULL,
1  httpRealm          TEXT,
2  formSubmitURL      TEXT,
3  usernameField      TEXT NOT NULL,
4  passwordField      TEXT NOT NULL,
5  decryptedUsername  TEXT NOT NULL,
6  decryptedPassword  TEXT NOT NULL,
'''
  f = open(ff_csv, "r")
  content = f.read()
  result = []
  for csv in content.split("\r\n"):
    if (csv != ""):
      result.append(csv.split(","))
  return result

def displayLoginCount(cursor):
  cursor.execute('SELECT COUNT(*) from logins');
  print "NB logins: " + str(cursor.fetchall())

def displayLogins(cursor):
  cursor.execute('SELECT * from logins');
  print "NB logins: " + str(cursor.fetchall())

def sync_pwds(ff_pwds, chrome_db):
  from pysqlite2 import dbapi2 as sqlite
  connection = sqlite.connect(chrome_db)
  cursor = connection.cursor()

  displayLoginCount(cursor)
  displayLogins(cursor)

  # FIXME get moz_disabledHosts info
  for pwd in ff_pwds:
    '''
   0  origin_url VARCHAR NOT NULL, 
   1  action_url VARCHAR,
   2  username_element VARCHAR,
   3  username_value VARCHAR,
   4  password_element VARCHAR,
   5  password_value BLOB,
   6  submit_element VARCHAR,
   7  signon_realm VARCHAR NOT NULL,
   8  ssl_valid INTEGER NOT NULL,
   9  preferred INTEGER NOT NULL,
  10  date_created INTEGER NOT NULL,
  11  blacklisted_by_user INTEGER NOT NULL,
  12  scheme INTEGER NOT NULL,UNIQUE (origin_url, username_element, username_value, password_element, submit_element, signon_realm));
  '''
    ssl_valid = ssl_value(pwd[0])
    preferred = 1 # beurk
    date_created = 0 # no info from firefox
    blacklisted_by_user = 0
    scheme = 0
    the_signon_realm = signon_realm(pwd[0])
    try:
      print str(pwd)
      cursor.execute('INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (to_not_empty_unicode(pwd[0]), to_not_empty_unicode(pwd[2]), to_not_empty_unicode(pwd[3]), to_not_empty_unicode(pwd[5]), to_not_empty_unicode(pwd[4]), to_not_empty_unicode(pwd[6]), to_not_empty_unicode(''), to_not_empty_unicode(the_signon_realm), ssl_valid, preferred, date_created, blacklisted_by_user, scheme))
    except sqlite.IntegrityError, e:
      print "Failed to insert " + str(pwd) + " " + str(e)

  displayLoginCount(cursor)
  connection.commit()

def ssl_value(url):
  if (url is None):
    raise Exception("Invalud argument to ssl_value")
  if url.startswith("https"):
    return 1
  return 0
	
def signon_realm(url):
  import re
  m = re.search('(http[s]?://[^\/]+).*', url)
  if m is None:
    raise Exception("Couldn't find signon_realm in " + url)
  g = m.groups()
  if len(g) == 0:
    raise Exception("Programmer bug. Forgot your group ?")
  if m.group(1) == None:
    raise Exception("Couldn't find signon_realm match in " + url)
  return m.group(1) + "/"

def to_not_empty_unicode(x):
  if x == "" or x == "(null)":
    return ur""
  return unicode(x)

def main(ff_db_csv):
  chrome_db = '/home/jerome/.config/chromium/Default/Web Data'
  tmp_chrome_db = '/tmp/chrome_db'
  x = os.system(ff_dump_exe + " > " + ff_db_csv)
  if (x != 0):
    print "failed to dump Firefox passwords"
    exit(-1)
  
  firefox_pwds = load_ff_pwds(ff_db_csv)
  print "Dumped %s Firefox passwords" % len(firefox_pwds)
  shutil.copy(chrome_db, tmp_chrome_db)
  print "Copied chrome DB"
  
  sync_pwds(firefox_pwds, tmp_chrome_db)
  print "Added Firefox passwords to chrome DB " + tmp_chrome_db
  print "Carefully backup your chrome_db file (" + chrome_db + ") then copy " + tmp_chrome_db + " into it"

if __name__ == '__main__':
  ff_db_csv = '/tmp/pw_dumps.csv'
  try:
    main(ff_db_csv)
  finally:
    if os.access(ff_db_csv, os.F_OK):
      print "deleting temporary file containing firefox passwords"
      os.unlink(ff_db_csv)
