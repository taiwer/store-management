import sqlite3

conn = sqlite3.connect("material_management.db")
conn.text_factory = str
cur = conn.cursor()

cur.execute(
    "create table if not exists material(material_id varchar(32) primary key,material_name varchar(100),spec varchar(100),unit varchar(10),per_price varchar(20), pos varchar(32),ori_num float,now_num float)")

cur.execute(
    "create table if not exists in_log(date_time int,material_id varchar(32),material_name varchar(100),spec varchar(100),in_num float, per_price varchar(20),pos varchar(32), total_price varchar(100),user_man varchar(20),agree_man varchar(20), in_log_id INTEGER PRIMARY KEY AUTOINCREMENT)")

cur.execute(
    "create table if not exists out_log(date_time int,material_id varchar(32),material_name varchar(100),spec varchar(100),out_num float,per_price varchar(20), pos varchar(32),total_price varchar(100), user_man varchar(20),agree_man varchar(20), out_log_id INTEGER PRIMARY KEY AUTOINCREMENT)")

conn.commit()
cur.close()
conn.close()
