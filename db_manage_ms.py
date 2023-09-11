import psycopg2, pyodbc, datetime, sys
import psycopg2.extras as extras

con_string_1 ='Driver={ODBC Driver 18 for SQL Server};Server=192.168.0.6;\
Database=AltaSVHDb_2015;Encrypt=no;UID=Alta;PWD=AltApoRTal2022;'
db_name = 'AltaSVHDb_2015'

cnxn_1 = pyodbc.connect(con_string_1)  # odbc driver system dsn name
cursor_1 = cnxn_1.cursor()


query_select_1 = f"""
 select s.ids, count(s.ids)
  FROM  ({db_name}.dbo.reg_sub s INNER JOIN {db_name}.dbo.reg_main m ON m.id=s.main_id) 
   LEFT OUTER JOIN {db_name}.dbo.contact b ON b.contact=s.broker
--where m.date >= '2023-01-01'
--and s.ids = '12205800000001'
group by s.ids
having count(s.ids)>1
--ORDER BY m.date desc
"""

query_select_3 = f"""
select *
 --ids, count(ids)
from {db_name}.dbo.reg_sub
where ids = '12205800000001'
and sub_id is not null
--group by ids
--having count(ids)>1
"""

query_select_2 = f"""
select 
  p.id, count(p.id)
      FROM (({db_name}.dbo.prop_ent p LEFT OUTER JOIN {db_name}.dbo.prop_ext e ON e.id_ent=p.id)
       LEFT OUTER JOIN {db_name}.dbo.contact c ON  c.contact=p.contact)
       LEFT OUTER JOIN {db_name}.dbo.contact b ON b.contact=c.broker 
       --WHERE 1=1 AND DATEPART(dy,p.postdate)=DATEPART(dy,GETDATE())
       where p.dateen >= '2023-09-01'
       --and p.id in ('122561', '127926')
       group by p.id
        having count(p.id)>1
"""

query_tables_names = """
SELECT table_name
  FROM information_schema.tables
 WHERE table_schema='public'
   --AND table_type='BASE TABLE';
"""


# query_select - 
cursor_1.execute(query_select_3)
dataset = cursor_1.fetchall(); #print(dataset)

for r in dataset:
  print(r)
  print()


cursor_1.close()
cnxn_1.close()
