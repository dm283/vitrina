import sys, os, configparser
from pathlib import Path

config = configparser.ConfigParser()
config_file = os.path.join(Path(__file__).resolve().parent.parent, 'vitrina', 'vitrina', 'config.ini')   
if os.path.exists(config_file):
  config.read(config_file, encoding='utf-8')
else:
  print("error! config file doesn't exist"); sys.exit()
DB1_NAME = config['db']['db1_name']
DB2_NAME = config['db']['db2_name']
DB2_SCHEMA = config['db']['db2_schema']

TABLE_FOR_INSERTS_CONSIGNMENTS = f'{DB2_NAME}.{DB2_SCHEMA}.svh_service_consignment'
COLUMNS_IN_TABLE_FOR_INSERTS_CONSIGNMENTS = 'guid, key_id, contact, contact_name, contact_broker, broker_name, \
nttn, nttn_date, dkd, dkd_date, goods, weight, dater, dateo, id_enter, car, \
d_in, d_out, guid_user, datep, created, updated, posted, post_date, \
post_user_id, was_posted'

QUERY_LOAD_DATA_CONSIGNMENTS = f"""
-- *****  select for consignments  *****
select 
  case when s.guid_sub is null then '' else s.guid_sub end  guid,
  s.ids              					                              key_id, 
  s.receiver     					                                  contact,
  s.rname        					                                  contact_name,
  s.broker        					                                contact_broker, 
  case when b.name is null then '' else b.name end 		      broker_name,
  case when s.sub_id is null then '' else s.sub_id end 		  nttn,
  s.sub_date    					                                  nttn_date, 
  case when s.cmr is null then '' else s.cmr end 		        dkd,
  s.cmr_date   					                                    dkd_date,
  case when s.goods is null then '' else s.goods end 		    goods,
  case when s.weight is null then 0 else s.weight end 		  weight,
  m.date          					                                dater, 
  s.date_out    					                                  dateo, 
  case when m.propusk is null then '' else m.propusk end 	  id_enter,
  m.ncar           					                                car,
  convert( datetime, convert(char(8), m.rdate, 112) + ' ' + 
    convert(CHAR(8), m.rtime, 108) ) 			                  d_in,
  convert( datetime, convert(char(8), m.odate, 112) + ' ' + 
    convert(CHAR(8), m.otime, 108) ) 			                  d_in,

  'sys'               					                            guid_user,
  m.postdate   					                                    datep,
  getdate()                       				                  created,
  getdate()                       				                  updated,
  'replace_true'   					                                posted,
  getdate()           					                            post_date,
  'sys'                    					                        post_user_id,
  'replace_true'   					                                was_posted

from ({DB1_NAME}.dbo.reg_sub s 
    inner join {DB1_NAME}.dbo.reg_main m on m.id=s.main_id) 
    left outer join {DB1_NAME}.dbo.contact b on b.contact=s.broker
where 1=1
    --and m.date >= '2023-09-01'
    and s.sub_id is not null  --cut double recs
order by m.date desc
"""
