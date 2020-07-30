import pymysql

class cn_sql:
    def __init__(self):
        self.dbname = 'sc'
        self.user = 'root'
        self.password = '1761586273'
        self.host = '127.0.0.1'
        self.port = 3307
        self.connection = pymysql.connect(db=self.dbname,user=self.user,password=self.password,host=self.host,port=self.port,charset='utf8')

    def set_sql(self,sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        # result = cursor.fetchone()
        result = cursor.fetchall()
        print(result)
        self.connection.close()

if __name__ == "__main__":
    cnsql = cn_sql()
    cnsql.set_sql("select 船只,船只中文翻译 from tb_tmp1 where 厂商 = '圣盾';")
