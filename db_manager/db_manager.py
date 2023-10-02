# cmd run format:  db_manage.py [-i]
import sys, os, configparser, psycopg2, pyodbc
from pathlib import Path

config = configparser.ConfigParser()
config_file = os.path.join(Path(__file__).resolve().parent.parent, 'vitrina', 'vitrina', 'config.ini')   
if os.path.exists(config_file):
  config.read(config_file, encoding='utf-8')
else:
  print("error! config file doesn't exist"); sys.exit()
DB_CONNECTION_STRING = config['db']['db2_connection_string']
DB_TYPE = config['db']['db2_type']


def db_connection(db):
  #  connects to database with defined in db argument type
  global CONN, CURSOR
  print(DB_CONNECTION_STRING)
  print('connect to database ..... ', end='')
  try:
    if db == '-p':
      CONN = psycopg2.connect(DB_CONNECTION_STRING)  # postgre database
    elif db == '-m':
      CONN = pyodbc.connect(DB_CONNECTION_STRING)     # ms-sql database
    CURSOR = CONN.cursor()
    print('ok')
  except(Exception) as err:
    print('error database connection'); print(err)
    sys.exit()


def db_action(query):
  #  makes action in database
  try:
    CURSOR.execute(query)
    if 'select ' in query:
      dataset = CURSOR.fetchall(); 
      # print(dataset)
      for n, r in enumerate(dataset):
        print(f'[{n}] ', r); print()
      print(f'retrieved [{len(dataset)}] rows'); print()
    else:
      CONN.commit()
      print('done. commited successfully.')

  except(Exception) as err:
    print('error: ', err)


#  set of queries
q = """
select * from svh_service_document
"""

q = """
select table_name from information_schema.tables where table_schema='public' --and table_type='base table';
"""

# ******************* main actions *******************
#db = sys.argv[2]
db = DB_TYPE
db_connection(db)

if len(sys.argv) > 1 and sys.argv[1] == '-i':
  query = ''
  while query != 'exit':
    query = input('query:  ')
    db_action(query)
else:
  db_action(q)

CURSOR.close()
CONN.close()
