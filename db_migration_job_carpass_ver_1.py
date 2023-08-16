import psycopg2, pyodbc, datetime, sys
import psycopg2.extras as extras


# ************************************ READ DATA [ MS-SQL ] ************************************
# con_string_1 = 'Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
con_string_1 = 'DSN=odbc_1'
db_name = 'sanp2018'

cnxn_1 = pyodbc.connect(con_string_1)  # odbc driver system dsn name
cursor_1 = cnxn_1.cursor()

def db_read_data():
    """
    Чтение данных из БД1
    """
    query = f"""
      SELECT top 100
		case when p.guid_prop is null then '' else p.guid_prop end guid,
        --p.guid_prop guid,
        p.id id_enter,
        p.ncar,
        p.dateen,
        p.timeen,
        left( case when p.ntir is null then '' else p.ntir end, 50 ) ntir,
		--case when p.ntir is null then '' else p.ntir end ntir,
        --p.ntir,
		case when p.nkont is null then '' else p.nkont end nkont,
        --p.nkont,
        p.new1 driver,
        p.drv_man,
		case when p.drv_phone is null then '' else p.drv_phone end drv_phone,
        --p.drv_phone,
        p.contact,
        p.rec contact_name,
        b.contact contact_broker,
		case when b.name is null then '' else b.name end broker_name,
        --b.name broker_name, 
        '' as place_n,
        e.dateex,
        e.timeex,
        p.postdate datep,

        'replace_false' posted,
        null post_date,
        'sys' post_user_id,
        'replace_false' was_posted
      FROM (({db_name}.dbo.prop_ent p LEFT OUTER JOIN {db_name}.dbo.prop_ext e ON e.id_ent=p.id)
       LEFT OUTER JOIN {db_name}.dbo.contact c ON  c.contact=p.contact)
       LEFT OUTER JOIN {db_name}.dbo.contact b ON b.contact=c.broker 
       --WHERE 1=1 AND DATEPART(dy,p.postdate)=DATEPART(dy,GETDATE())
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


# ************************************ INSERT DATA [ POSTGRE ] ************************************
conn_2 = psycopg2.connect(
            host='localhost',
            port='5432',
            database='svh_service_db',
            user='postgres',
            password='s2d3f4!@'
        )
cursor_2 = conn_2.cursor()

# print(conn_2, cursor_2)
# sys.exit()

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
