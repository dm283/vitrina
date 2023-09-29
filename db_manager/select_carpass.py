import configparser

config = configparser.ConfigParser(); config.read('config_db.ini', encoding='utf-8')
DB1_NAME = config['db']['db1_name']
DB2_NAME = config['db']['db2_name']
DB2_SCHEMA = config['db']['db2_schema']

TABLE_FOR_INSERTS_CARPASS = f'{DB2_NAME}.{DB2_SCHEMA}.svh_service_carpass'
COLUMNS_IN_TABLE_FOR_INSERTS_CARPASS = 'guid, id_enter, ncar, dateen, timeen, ntir, nkont, driver, drv_man, dev_phone, \
    contact, contact_name, contact_broker, broker_name, place_n, dateex, timeex, datep, posted, post_date, post_user_id, was_posted'

QUERY_LOAD_DATA_CARPASS = f"""
-- *****  select for carpass  *****
select 
  distinct
	case when p.guid_prop is null then '' else p.guid_prop end    guid,
  p.id                                                          id_enter,
  case when p.ncar is null then '' else p.ncar end              ncar,
  p.dateen                                                      dateen,
  p.timeen                                                      timeen,
  left( case when p.ntir is null then '' else p.ntir end, 50 )  ntir,
	case when p.nkont is null then '' else p.nkont end            nkont,
  case when p.new1 is null then '' else p.new1 end              driver,
  case when p.drv_man is null then '' else p.drv_man end        drv_man,
	case when p.drv_phone is null then '' else p.drv_phone end    drv_phone,
  p.contact                                                     contact,
  case when p.rec is null then '' else p.rec end                contact_name,
  b.contact                                                     contact_broker,
	case when b.name is null then '' else b.name end              broker_name,
  '' as                                                         place_n,
  e.dateex                                                      dateex,
  e.timeex                                                      timeex,

  p.postdate                                                    datep,
  'replace_true'                                                posted,
  getdate()                                                     post_date,
  'sys'                                                         post_user_id,
  'replace_true'                                                was_posted

from (({DB1_NAME}.dbo.prop_ent p left outer join {DB1_NAME}.dbo.prop_ext e ON e.id_ent=p.id)
  left outer join {DB1_NAME}.dbo.contact c on c.contact=p.contact)
  left outer join {DB1_NAME}.dbo.contact b on b.contact=c.broker 
where 1=1 
  --AND DATEPART(dy,p.postdate)=DATEPART(dy,GETDATE())
  --and p.dateen >= '2023-09-01'
  and e.posted > 0
  and p.posted > 0
order by dateen desc
"""
