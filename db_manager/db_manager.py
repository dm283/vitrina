# cmd run format:  db_manage.py -[p/m] [-i]
import sys, configparser, psycopg2, pyodbc

config = configparser.ConfigParser(); config.read('config_db.ini', encoding='utf-8')
DB_CONNECTION_STRING = config['db']['db2_connection_string']


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
db = sys.argv[1]
db_connection(db)

if len(sys.argv) > 2 and sys.argv[2] == '-i':
  query = ''
  while query != 'exit':
    query = input('query:  ')
    db_action(query)
else:
  db_action(q)

CURSOR.close()
CONN.close()
