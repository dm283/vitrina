import psycopg2, pyodbc, datetime, sys
import psycopg2.extras as extras


# ************************************ READ DATA [ MS-SQL ] ************************************
# con_string_1 = 'Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
con_string_1 = 'DSN=odbc_1'
db_name = 'sanp2018'

cnxn_1 = pyodbc.connect(con_string_1)  # odbc driver system dsn name
cursor_1 = cnxn_1.cursor()

def db_read_data():
    '''
    Чтение данных из БД1
    '''
    cursor_1.execute(f"""
    select top 1000
    s.ids key_id, 
    s.receiver contact,
    s.rname contact_name,
    s.broker contact_broker, 
    case when b.name is null then '' else b.name end broker_name,
    s.sub_id nttn, 
    s.sub_date nttn_date, 
    case when s.cmr is null then '' else s.cmr end goods,
    0 weight,
    m.date dater, 
    null dateo,
    case when m.propusk is null then '' else m.propusk end id_enter,
    m.ncar car, 
    convert( datetime, convert(char(8), m.rdate, 112) + ' ' + 
        convert(CHAR(8), m.rdate, 108) ) d_in,
    null d_out,
    '' guid_user,
    getdate() datep,
    'replace_false' posted,
    null post_date,
    'sys' post_user_id,
    'replace_false' was_posted

    from ({db_name}.dbo.reg_sub s inner join {db_name}.dbo.reg_main m on m.id=s.main_id) 
    left outer join {db_name}.dbo.contact b on b.contact=s.broker
    order by m.date desc
    """)

    rows = cursor_1.fetchall()  # список кортежей
    return rows
        

def data_handling(data_set):
    '''
    Обработка данных
    '''
    data_set_2 = []
    for t in data_set:
        t_2 = tuple([False if e == 'replace_false' else e for e in t])
        data_set_2.append(t_2)

    return data_set_2


data_set = db_read_data()  
data_set = data_handling(data_set)  # это набор данных загруженный из первой базы данных (и подготовленный для записи)

cursor_1.close()
cnxn_1.close()

# print(data_set)  # check mere reading
# sys.exit()       # check mere reading


# ************************************ INSERT DATA [ MS-SQL ] ************************************
#con_string_2 = 'Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
con_string_2 = 'DSN=odbc_1'

cnxn_2 = pyodbc.connect(con_string_2)  # odbc driver system dsn name
cursor_2 = cnxn_2.cursor()

table_2 = 'svh_service_db_2.dbo.svh_service_consignment'
cols_2 = 'key_id, contact, contact_name, contact_broker, broker_name, nttn, nttn_date, goods, weight, dater, dateo, id_enter, car, d_in, d_out, guid_user, datep, posted, post_date, post_user_id, was_posted'

def db_save_data(data_set):
    '''
    Записывает данные в БД2
    '''
    try:
        cursor_2.executemany(f'insert into {table_2} ({cols_2}) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                             data_set)
        cnxn_2.commit()
        print("Inserts done")
    except Exception as ex:
        print(f"Error: {ex}")
        cnxn_2.rollback()
        
db_save_data(data_set)

cursor_2.close()
cnxn_2.close()


# ************************************ INSERT DATA [ POSTGRE ] ************************************
# conn_2 = psycopg2.connect(
#             host='localhost',
#             port='5432',
#             database='svh_service_db',
#             user='postgres',
#             password='s2d3f4!#'
#         )
# cursor_2 = conn_2.cursor()

# # print(conn_2, cursor_2)
# # sys.exit()

# table_2 = 'svh_service_consignment'
# cols_2 = 'key_id, contact, contact_name, contact_broker, broker_name, nttn, nttn_date, goods, weight, dater, dateo, id_enter, car, d_in, d_out, guid_user, datep, posted, post_date, post_user_id, was_posted'

# query_2 = "INSERT INTO %s(%s) VALUES %%s" % (table_2, cols_2)

# try:
#     extras.execute_values(cursor_2, query_2, data_set)
#     conn_2.commit()
#     print("execute_values() done")
# except (Exception, psycopg2.DatabaseError) as error:
#     print("Error: %s" % error)
#     conn_2.rollback()

# cursor_2.close()
# cnxn_2.close()
