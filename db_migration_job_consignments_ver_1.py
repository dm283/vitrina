import psycopg2, pyodbc, datetime, sys
import psycopg2.extras as extras


# ************************************ READ DATA [ MS-SQL ] ************************************
#  LOCAL DEVELOPMENT
con_string_1 = 'DSN=odbc_1'
db_name = 'sanp2018'

#  GUZHON
# con_string_1 ='Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;\
# Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
# db_name = 'AltaSVHDb_2015'

print('CONNECT TO DB-1 ..... ', end='')
cnxn_1 = pyodbc.connect(con_string_1)
cursor_1 = cnxn_1.cursor()
print('OK')

# query = f"""
# -- *****  select for consignments  *****

# SELECT TOP 100
# case when s.guid_sub is null then '' else s.guid_sub end         	guid,
# s.ids              					key_id, 
# s.receiver     					contact,
# s.rname        					contact_name,
# s.broker        					contact_broker, 
# case when b.name is null then '' else b.name end 		broker_name,
# case when s.sub_id is null then '' else s.sub_id end 		nttn,
# s.sub_date    					nttn_date, 
# case when s.cmr is null then '' else s.cmr end 		dkd,
# s.cmr_date   					dkd_date,
# case when s.goods is null then '' else s.goods end 		goods,
# s.weight       					weight,
# m.date          					dater, 
# s.date_out    					dateo, 
# case when m.propusk is null then '' else m.propusk end 	id_enter,
# m.ncar           					car,
# convert( datetime, convert(char(8), m.rdate, 112) + ' ' + 
#        convert(CHAR(8), m.rtime, 108) ) 			d_in,
# convert( datetime, convert(char(8), m.odate, 112) + ' ' + 
#        convert(CHAR(8), m.otime, 108) ) 			d_in,
# 'sys'               					guid_user,

# m.postdate   					datep,
# getdate()                       				created,
# getdate()                       				updated,
# 'replace_true'   					posted,
# getdate()           					post_date,
# 'sys'                    					post_user_id,
# 'replace_true'   					was_posted

# FROM  ({db_name}.dbo.reg_sub s INNER JOIN {db_name}.dbo.reg_main m ON m.id=s.main_id) 
#    LEFT OUTER JOIN {db_name}.dbo.contact b ON b.contact=s.broker
# ORDER BY m.date
# """

query = f"""
-- *****  select for consignments  *****

SELECT 
--TOP 100
case when s.guid_sub is null then '' else s.guid_sub end         	guid,
s.ids              					key_id, 
s.receiver     					contact,
s.rname        					contact_name,
s.broker        					contact_broker, 
case when b.name is null then '' else b.name end 		broker_name,
case when s.sub_id is null then '' else s.sub_id end 		nttn,
s.sub_date    					nttn_date, 
case when s.cmr is null then '' else s.cmr end 		dkd,
s.cmr_date   					dkd_date,
case when s.goods is null then '' else s.goods end 		goods,
s.weight       					weight,
m.date          					dater, 
s.date_out    					dateo, 
case when m.propusk is null then '' else m.propusk end 	id_enter,
m.ncar           					car,
convert( datetime, convert(char(8), m.rdate, 112) + ' ' + 
       convert(CHAR(8), m.rtime, 108) ) 			d_in,
convert( datetime, convert(char(8), m.odate, 112) + ' ' + 
       convert(CHAR(8), m.otime, 108) ) 			d_in,
'sys'               					guid_user,

m.postdate   					datep,
getdate()                       				created,
getdate()                       				updated,
'replace_true'   					posted,
getdate()           					post_date,
'sys'                    					post_user_id,
'replace_true'   					was_posted

FROM  ({db_name}.dbo.reg_sub s INNER JOIN {db_name}.dbo.reg_main m ON m.id=s.main_id) 
   LEFT OUTER JOIN {db_name}.dbo.contact b ON b.contact=s.broker
where m.date >= '2023-09-01'
 and s.sub_id is not null  --  cut double recs
--and s.ids != '12205800000001'  -- duble ids!
ORDER BY m.date desc
"""

def db_read_data():
    """
    Load data from DB-1
    """
    cursor_1.execute(query)

    rows = cursor_1.fetchall()  # список кортежей
    return rows
        

def data_handling(data_set):
    """
    Handle the data
    """
    data_set_2 = []
    for t in data_set:
        t_2 = tuple([True if e == 'replace_true' else e for e in t])
        data_set_2.append(t_2)

    return data_set_2

print('READ DATA ..... ', end='')
data_set = db_read_data()  
print('OK') 
print('HANDLING DATA ..... ', end='')
data_set = data_handling(data_set)  # это набор данных загруженный из первой базы данных (и подготовленный для записи)
print('OK')
print(f'[{len(data_set)}] ROWS WAS READ')

cursor_1.close()
cnxn_1.close()

# for r in data_set:
#     print(r)

# print(data_set)  # check mere reading
# sys.exit()       # check mere reading


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


# ************************************ INSERT DATA [ POSTGRE ] ************************************
print('CONNECT TO DB-2 ..... ', end='')
conn_2 = psycopg2.connect(
            host='localhost',
            port='5432',
            database='svh_service_db',
            user='postgres',
            password='s2d3f4!@'
        )
cursor_2 = conn_2.cursor()
print('OK')

# print(conn_2, cursor_2)
# sys.exit()

table_2 = 'svh_service_consignment'
cols_2 = 'guid, key_id, contact, contact_name, contact_broker, broker_name, \
nttn, nttn_date, dkd, dkd_date, goods, weight, dater, dateo, id_enter, car, \
d_in, d_out, guid_user, datep, created, updated, posted, post_date, \
post_user_id, was_posted'

query_2 = "INSERT INTO %s(%s) VALUES %%s" % (table_2, cols_2)

print('SAVE DATA TO DB-2 ..... ', end='')
try:
    extras.execute_values(cursor_2, query_2, data_set)
    conn_2.commit()
    print("OK")
except (Exception, psycopg2.DatabaseError) as error:
    print("Error: %s" % error)
    conn_2.rollback()

cursor_2.close()
conn_2.close()
