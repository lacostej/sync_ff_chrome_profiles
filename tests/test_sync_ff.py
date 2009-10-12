from sync_password import *

def test_signon_realm():
  assertEquals(signon_realm('https://www.google.com'), 'https://www.google.com/')
  assertEquals(signon_realm('https://www.google.com/'), 'https://www.google.com/')
  assertEquals(signon_realm('https://www.google.com/aaaa'), 'https://www.google.com/')
  assertEquals(signon_realm('http://www.google.com'), 'http://www.google.com/')
  assertEquals(signon_realm('http://www.google.com/'), 'http://www.google.com/')
  assertEquals(signon_realm('http://www.google.com/aaaa'), 'http://www.google.com/')


def assertEquals(s1, s2):
  print s1 + " " + s2
  assert s1 == s2
