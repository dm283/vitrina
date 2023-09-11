import psycopg2, pyodbc, datetime, sys
import psycopg2.extras as extras

conn_2 = psycopg2.connect(
            host='localhost',
            port='5432',
            database='svh_service_db',
            user='postgres',
            password='s2d3f4!#'
        )
cursor_2 = conn_2.cursor()

query_select = """
 select *
  from svh_service_db.public.svh_service_carpass
"""

query_tables_names = """
SELECT table_name
  FROM information_schema.tables
 WHERE table_schema='public'
   --AND table_type='BASE TABLE';
"""

query_delete = """
delete from svh_service_db.public.svh_service_carpass;
commit;
"""

query_drop_table = """
drop table svh_service_db.public.svh_service_message;
commit;
"""
# query_select - 
cursor_2.execute(query_delete)
#dataset = cursor_2.fetchall(); print(dataset)

################
tables = ['django_migrations', 'django_content_type', 'auth_permission', 
'auth_group', 'auth_group_permissions', 'auth_user', 
'auth_user_groups', 'auth_user_user_permissions', 
'django_admin_log', 'django_session', 'svh_service_consignment', 
'svh_service_carpass', 'svh_service_contact', 'svh_service_document', 
'svh_service_message', 'svh_service_uemail', 'svh_service_profile']

tr = list(reversed(tables))

# for t in tr:
#     print(t)
#     query_drop_table = f"""
#         drop table if exists 
#         svh_service_db.public.{t};
#         commit;
#         """
#     cursor_2.execute(query_drop_table)



cursor_2.close()
conn_2.close()
