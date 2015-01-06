#!/usr/bin/env python3

import renren
import os, sys
import sqlite3
import shelve
import account_config

def generate_cookie(username, password):
  r = renren.RenRen()
  r.login(username, password)
  r.saveCookie('cookie.dat')

def update_feed(feed):
  s = shelve.open('feed.db')

  for i in feed:
    if i['id'] not in s:
      print('inserting item', i['id'])
      s[i['id']] = i
  
  s.sync()
  s.close()

def main(args):
  if len(args) >= 2:
    if args[1] == 'login':
      username = account_config.username
      password = account_config.password
      generate_cookie(username, password)
    elif args[1] == 'update_feed':
      r = renren.RenRen()
      r.loginByCookie('cookie.dat')
      feed = r.get_feed()
      update_feed(feed)
    elif args[1] == 'show_feed':
      r = renren.RenRen()
      r.loginByCookie('cookie.dat')
      feed = r.get_feed()
      print(feed)
    else:
      print('Unknown command')
      exit(-1)
  else:
    print('Command required')

if __name__ == '__main__':
  main(sys.argv)
