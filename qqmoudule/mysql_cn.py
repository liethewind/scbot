import pymysql,itertools

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
        sqlmsg = (list(itertools.chain.from_iterable(set(result))))
        return sqlmsg
        self.connection.close()

    def czgsh(self,czxx):
        gsh = ["船只id: ","厂商: ","船只: ","中文翻译: ","官网价格: ","游戏币价格: ","船员: ","货物: ","最大速度: ","HP: ","护盾","DPS: ","导弹: ","量子速度: ","量子范围: "]
        xq = ("\n".join([i[0]+str(i[1]) for i in zip(gsh,czxx)]))
        return xq


if __name__ == "__main__":
    cnsql = cn_sql()
    sqls = cnsql.set_sql("select 厂商 from tb_tmp1;")
    xinxi = (','.join(sqls))
    print("船只厂商信息如下: %s" % (xinxi))
