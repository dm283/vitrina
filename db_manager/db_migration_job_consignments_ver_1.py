import sys, configparser, psycopg2, pyodbc, psycopg2.extras as extras

config = configparser.ConfigParser()
config.read('config_db.ini', encoding='utf-8')
DB1_CONNECTION_STRING = config['db']['db1_connection_string']
DB2_CONNECTION_STRING = config['db']['db2_connection_string']
DB1_NAME = config['db']['db1_name']
DB2_NAME = config['db']['db2_name']
DB1_TYPE = '-m'
DB2_TYPE = '-p'

TABLE_FOR_INSERTING_DATA = 'svh_service_consignment'
COLUMNS_IN_TABLE_FOR_INSERTING_DATA = 'guid, key_id, contact, contact_name, contact_broker, broker_name, \
nttn, nttn_date, dkd, dkd_date, goods, weight, dater, dateo, id_enter, car, \
d_in, d_out, guid_user, datep, created, updated, posted, post_date, \
post_user_id, was_posted'

QUERY_LOAD_DATA = f"""
-- *****  select for consignments  *****
select 
  case when s.guid_sub is null then '' else s.guid_sub end  guid,
  s.ids              					                    key_id, 
  s.receiver     					                        contact,
  s.rname        					                        contact_name,
  s.broker        					                        contact_broker, 
  case when b.name is null then '' else b.name end 		    broker_name,
  case when s.sub_id is null then '' else s.sub_id end 		nttn,
  s.sub_date    					                        nttn_date, 
  case when s.cmr is null then '' else s.cmr end 		    dkd,
  s.cmr_date   					                            dkd_date,
  case when s.goods is null then '' else s.goods end 		goods,
  case when s.weight is null then 0 else s.weight end 		weight,
  m.date          					                        dater, 
  s.date_out    					                        dateo, 
  case when m.propusk is null then '' else m.propusk end 	id_enter,
  m.ncar           					                        car,
  convert( datetime, convert(char(8), m.rdate, 112) + ' ' + 
    convert(CHAR(8), m.rtime, 108) ) 			            d_in,
  convert( datetime, convert(char(8), m.odate, 112) + ' ' + 
    convert(CHAR(8), m.otime, 108) ) 			            d_in,
  'sys'               					                    guid_user,
  m.postdate   					                            datep,
  getdate()                       				            created,
  getdate()                       				            updated,
  'replace_true'   					                        posted,
  getdate()           					                    post_date,
  'sys'                    					                post_user_id,
  'replace_true'   					                        was_posted

from ({DB1_NAME}.dbo.reg_sub s 
    inner join {DB1_NAME}.dbo.reg_main m on m.id=s.main_id) 
    left outer join {DB1_NAME}.dbo.contact b on b.contact=s.broker
where 1=1
    --and m.date >= '2023-09-01'
    and s.sub_id is not null  --cut double recs
order by m.date desc
"""


def db_connection(db_connection_string, db_type):
    #  creates connection to database
    print(db_connection_string)
    print('connecting to database ..... ', end='')
    try:
        if db_type == '-p':
            conn = psycopg2.connect(db_connection_string)  # postgre database
        elif db_type == '-m':
            conn = pyodbc.connect(db_connection_string)     # ms-sql database
        cursor = conn.cursor()
        print('ok')
    except(Exception) as err:
        print('error database connection'); print(err)
        sys.exit()

    return conn, cursor


def db_read_data(cursor, query):
    #  loads data from db1
    print('retrieving data ..... ', end='')
    try:
        cursor.execute(query)
        data_set = cursor_1.fetchall()  # список кортежей
        print('ok' + f'retrieved [{len(data_set)}] rows')
    except(Exception) as err:
        print('error'); print(err)
        sys.exit()

    return data_set
        

def data_handling(data_set):
    #  handles a data_set   ( True - only for Postgre, 1 - for MS-SQL )
    print('handling data ..... ', end='')
    data_set_handled = []
    try:
        for t in data_set:
            t_2 = tuple([True if e == 'replace_true' else e for e in t])
            data_set_handled.append(t_2)
        print('ok')
    except(Exception) as err:
        print('error'); print(err)
        sys.exit()        

    return data_set_handled


def db_insert_data(data_set, db_type, table, columns):
    #  inserts data_set into database
    print('inserting data set to database ..... ', end='')
    try:
        if db_type == '-p':
            #  insert actions for Postgre database
            query_insert_data = "insert into %s(%s) values %%s" % (table, columns)
            extras.execute_values(cursor_2, query_insert_data, data_set)
            conn_2.commit()

        if db_type == '-m':
            #  insert actions for MS-SQL database
            pass

        print('ok')

    except(Exception) as err:
        print('error'); print(err)
        conn_2.rollback()
        sys.exit() 


# ************************************ READ DATA [ MS-SQL ] ************************************
conn_1, cursor_1 = db_connection(DB1_CONNECTION_STRING, DB1_TYPE)
data_set = db_read_data(cursor_1, QUERY_LOAD_DATA)
data_set = data_handling(data_set)  # это набор данных загруженный из первой базы данных (и подготовленный для записи)
cursor_1.close(); conn_1.close()

# for r in data_set:
#     print(r)
# print(data_set)
#sys.exit()       # check just reading


# ************************************ INSERT DATA [ POSTGRE ] ************************************
conn_2, cursor_2 = db_connection(DB2_CONNECTION_STRING, DB2_TYPE)
#print(conn_2, cursor_2); sys.exit()
db_insert_data(data_set, DB2_TYPE, TABLE_FOR_INSERTING_DATA, COLUMNS_IN_TABLE_FOR_INSERTING_DATA)
cursor_2.close(); conn_2.close()


# ************************************ INSERT DATA [ MS-SQL ] ************************************
#con_string_2 = 'Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
# con_string_2 = 'DSN=odbc_1'

# cnxn_2 = pyodbc.connect(con_string_2)  # odbc driver system dsn name
# cursor_2 = cnxn_2.cursor()

# table_2 = 'svh_service_db_2.dbo.svh_service_consignment'
# cols_2 = 'guid, key_id, contact, contact_name, contact_broker, broker_name, nttn, nttn_date, dkd, dkd_date, goods, weight, \
#     dater, dateo, id_enter, car, d_in, d_out, guid_user, datep, created, updated, posted, post_date, post_user_id, was_posted'

# def db_save_data(data_set):
#     """
#     Save data into DB-2
#     """
#     try:
#         cursor_2.executemany(f'insert into {table_2} ({cols_2}) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', 
#                              data_set)
#         cnxn_2.commit()
#         print("Inserts done")
#     except Exception as ex:
#         print(f"Error: {ex}")
#         cnxn_2.rollback()
        
# db_save_data(data_set)

# cursor_2.close()
# cnxn_2.close()
