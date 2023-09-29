import sys, configparser, psycopg2, pyodbc, psycopg2.extras as extras

config = configparser.ConfigParser()
config.read('config_db.ini', encoding='utf-8')
DB1_CONNECTION_STRING = config['db']['db1_connection_string']
DB2_CONNECTION_STRING = config['db']['db2_connection_string']
DB1_NAME = config['db']['db1_name']
DB2_NAME = config['db']['db2_name']
DB1_TYPE = config['db']['db1_type']
DB2_TYPE = config['db']['db2_type']

from select_consignments import TABLE_FOR_INSERTS_CONSIGNMENTS, COLUMNS_IN_TABLE_FOR_INSERTS_CONSIGNMENTS, QUERY_LOAD_DATA_CONSIGNMENTS
from select_carpass import TABLE_FOR_INSERTS_CARPASS, COLUMNS_IN_TABLE_FOR_INSERTS_CARPASS, QUERY_LOAD_DATA_CARPASS

TABLE_FOR_INSERTS = TABLE_FOR_INSERTS_CARPASS
COLUMNS_IN_TABLE_FOR_INSERTS = COLUMNS_IN_TABLE_FOR_INSERTS_CARPASS
QUERY_LOAD_DATA = QUERY_LOAD_DATA_CARPASS


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
        print('ok ' + f'retrieved [{len(data_set)}] rows')
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


def db_insert_data(conn, cursor, data_set, db_type, table, columns):
    #  inserts data_set into database
    print('inserting data set to database ..... ', end='')
    try:
        if db_type == '-p':
            #  insert actions for Postgre database
            query_insert_data = "insert into %s(%s) values %%s" % (table, columns)
            extras.execute_values(cursor, query_insert_data, data_set)
            conn.commit()

        if db_type == '-m':
            #  insert actions for MS-SQL database
            q_str = str()
            for i in range(len(columns.split(','))):
                q_str += '?,'
            q_str = q_str[:-1]
            query_insert_data = f'insert into {table} ({columns}) values ({q_str})'
            cursor.executemany(query_insert_data, data_set)   
            conn.commit()         

        print('ok')

    except(Exception) as err:
        print('error'); print(err)
        conn.rollback()
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
# conn_2, cursor_2 = db_connection(DB2_CONNECTION_STRING, DB2_TYPE)
# #print(conn_2, cursor_2); sys.exit()
# db_insert_data(data_set, DB2_TYPE, TABLE_FOR_INSERTING_DATA, COLUMNS_IN_TABLE_FOR_INSERTING_DATA)
# cursor_2.close(); conn_2.close()


# ************************************ INSERT DATA [ MS-SQL ] ************************************
conn_2, cursor_2 = db_connection(DB2_CONNECTION_STRING, DB2_TYPE)
# print(conn_2, cursor_2); sys.exit()
db_insert_data(conn_2, cursor_2, data_set, DB2_TYPE, TABLE_FOR_INSERTS, COLUMNS_IN_TABLE_FOR_INSERTS)
cursor_2.close(); conn_2.close()
