import pymysql

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "weixin"

class MySQL(object):
    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, username=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE):
        try:
            self.db = pymysql.connect(host, username, password, database, port=port, charset='utf8')
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)
    
    def insert(self, table, data):
        keys = ", ".join(data.keys())
        values = ", ".join(['%s']*len(data))
        sql_query = "insert into %s (%s) values (%s)" % (table, keys, values)

        try:
            self.cursor.execute(sql_query, tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()
