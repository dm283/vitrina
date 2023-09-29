import psycopg2, pyodbc, datetime, sys
import psycopg2.extras as extras

# ************************************ READ DATA [ MS-SQL ] ************************************
#  LOCAL DEVELOPMENT
# con_string_1 = 'DSN=odbc_1'
# db_name = 'sanp2018'

#  GUZHON
con_string_1 ='Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;\
Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
db_name = 'AltaSVHDb_2015'

cnxn_1 = pyodbc.connect(con_string_1)  # odbc driver system dsn name
cursor_1 = cnxn_1.cursor()

def db_read_data():
    """
    Чтение данных из БД1
    """
    query = f"""
      SELECT 
        distinct
		case when p.guid_prop is null then '' else p.guid_prop end guid,
        p.id id_enter,
        case when p.ncar is null then '' else p.ncar end ncar,
        p.dateen,
        p.timeen,
        left( case when p.ntir is null then '' else p.ntir end, 50 ) ntir,
		case when p.nkont is null then '' else p.nkont end nkont,
        case when p.new1 is null then '' else p.new1 end driver,
        case when p.drv_man is null then '' else p.drv_man end drv_man,
		case when p.drv_phone is null then '' else p.drv_phone end drv_phone,
        p.contact,
        case when p.rec is null then '' else p.rec end contact_name,
        b.contact contact_broker,
		case when b.name is null then '' else b.name end broker_name,
        '' as place_n,
        e.dateex,
        e.timeex,
        p.postdate datep,
        'replace_true' posted,
        null post_date,
        'sys' post_user_id,
        'replace_true' was_posted
      FROM (({db_name}.dbo.prop_ent p LEFT OUTER JOIN {db_name}.dbo.prop_ext e ON e.id_ent=p.id)
       LEFT OUTER JOIN {db_name}.dbo.contact c ON  c.contact=p.contact)
       LEFT OUTER JOIN {db_name}.dbo.contact b ON b.contact=c.broker 
       WHERE 1=1 
       --AND DATEPART(dy,p.postdate)=DATEPART(dy,GETDATE())
       and p.dateen >= '2023-09-01'
       and e.posted > 0
       and p.posted > 0
      ORDER BY dateen DESC
    """

    cursor_1.execute(query)

    rows = cursor_1.fetchall()  # список кортежей
    return rows
        

def data_handling(data_set):
    """
    Обработка данных
    """
    data_set_2 = []
    for t in data_set:
        t_2 = tuple([True if e == 'replace_true' else e for e in t])
        data_set_2.append(t_2)

    return data_set_2


data_set = db_read_data()  
data_set = data_handling(data_set)  # это набор данных загруженный из первой базы данных (и подготовленный для записи)

cursor_1.close()
cnxn_1.close()

# for r in data_set:
#     print(r)

# print(data_set); sys.exit()       # check just reading


# ************************************ INSERT DATA [ POSTGRE ] ************************************
conn_2 = psycopg2.connect(
            host='192.168.0.121',
            port='5432',
            database='svh_service_db',
            user='postgres',
            password='s2d3f4!#'
        )
cursor_2 = conn_2.cursor()

# print(conn_2, cursor_2); sys.exit()

table_2 = 'svh_service_carpass'
cols_2 = 'guid, id_enter, ncar, dateen, timeen, ntir, nkont, driver, drv_man, dev_phone, \
    contact, contact_name, contact_broker, broker_name, place_n, dateex, timeex, datep, posted, post_date, post_user_id, was_posted'

query_2 = "INSERT INTO %s(%s) VALUES %%s" % (table_2, cols_2)

try:
    extras.execute_values(cursor_2, query_2, data_set)
    conn_2.commit()
    print("execute_values() done")
except (Exception, psycopg2.DatabaseError) as error:
    print("Error: %s" % error)
    conn_2.rollback()

cursor_2.close()
conn_2.close()


# ************************************ INSERT DATA [ MS-SQL ] ************************************
#con_string_2 = 'Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
# con_string_2 = 'DSN=odbc_1'

# cnxn_2 = pyodbc.connect(con_string_2)  # odbc driver system dsn name
# cursor_2 = cnxn_2.cursor()

# table_2 = 'svh_service_db_2.dbo.svh_service_carpass'
# cols_2 = 'guid, id_enter, ncar, dateen, timeen, ntir, nkont, driver, drv_man, dev_phone, \
#     contact, contact_name, contact_broker, broker_name, place_n, dateex, timeex, datep, posted, post_date, post_user_id, was_posted'

# def db_save_data(data_set):
#     """
#     Записывает данные в БД2
#     """
#     try:
#         cursor_2.executemany(f'insert into {table_2} ({cols_2}) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', 
#                              data_set)
#         cnxn_2.commit()
#         print("Inserts done")
#     except Exception as ex:
#         print(f"Error: {ex}")
#         cnxn_2.rollback()
        
# db_save_data(data_set)

# cursor_2.close()
# cnxn_2.close()
