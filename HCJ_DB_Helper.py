# encoding:utf-8
# name:mod_db.py
'''
使用方法：1.在主程序中先实例化DB Mysql数据库操作类。
      2.使用方法:db=database()  db.fetch_all("sql")
'''
import MySQLdb.cursors

import MySQLdb
from DBUtils.PooledDB import PooledDB
DBNAME = 'A_healthy_recipes'
DBHOST = '47.101.169.42'
DBUSER = 'zx'
DBPWD = '12345678'
DBCHARSET = 'utf8'
DBPORT = 3306


# 数据库操作类
class HCJ_database:
    # 注，python的self等于其它语言的this
    def __init__(self, log=None,dbname=None, dbhost=None,DictCursor=False):
        self._logger = log
        self._DictCursor=DictCursor
        # 这里的None相当于其它语言的NULL
        if dbname is None:
            self._dbname = DBNAME
        else:
            self._dbname = dbname
        if dbhost is None:
            self._dbhost = DBHOST
        else:
            self._dbhost = dbhost

        if  self._DictCursor:
            self._cursorclass=MySQLdb.cursors.DictCursor
        else:
            self._cursorclass=MySQLdb.cursors.Cursor
        self._dbuser = DBUSER
        self._dbpassword = DBPWD
        self._dbcharset = DBCHARSET
        self._dbport = int(DBPORT)
        self._conn = self.connectMySQL()  # 判断是否连接


        if (self._conn):
            self._cursor = self._conn.cursor()

    def Is_Database_Connected(self):
        if (self._conn.ping()):
            return True
        else:
            return False

    # 数据库连接
    def connectMySQL(self):
        conn = False
        try:
            conn = MySQLdb.connect(host=self._dbhost,
                                   user=self._dbuser,
                                   passwd=self._dbpassword,
                                   db=self._dbname,
                                   port=self._dbport,
                                   cursorclass=self._cursorclass,
                                   charset=self._dbcharset,
                                   )
        except:
            conn = False
        return conn

    # 获取查询结果集
    def do_sql(self, sql):
        res = ''
        if self._conn:
            try:
                self._cursor.execute(sql)
                res = self._cursor.fetchall()
                self._conn.commit()

            except :
                res = False
                self._logger.warn("query database exception,sql= %s" % (sql))
        return res

        # 获取查询结果集

    def do_sql_one(self, sql):
        res = ''

        if (self._conn):
            try:
                self._cursor.execute(sql)
                res = self._cursor.fetchone()
                self._conn.commit()
            except :
                res = False
                self._logger.warn("query database exception,sql= %s,%s" % (sql))
        return res

    def upda_sql(self, sql):
        flag = False
        if (self._conn):
            try:
                self._cursor.execute(sql)
                self._conn.commit()
                flag = True
            except :
                flag = False
                self._logger.warn("query database exception,sql= %s,%s" % (sql))
        return flag

    # 关闭数据库连接
    def close(self):
        if (self._conn):

            try:
                self._conn.close()
                if (type(self._cursor) == 'object'):
                    self._cursor.close()
                if (type(self._conn) == 'object'):
                    print("close")
                    self._conn.close()
            except :
                self._logger.warn("close database exception, %s,%s" % ( type(self._cursor), type(self._conn)))
class HCJ_MySQL:
    pool = None
    limit_count = 3  # 最低预启动数据库连接数量

    def __init__(self,log=None,dbname=None,dbhost=None):
        if dbname is None:
            self._dbname = DBNAME
        else:
            self._dbname = dbname
        if dbhost is None:
            self._dbhost = DBHOST
        else:
            self._dbhost = dbhost

        self._dbuser = DBUSER
        self._dbpassword = DBPWD
        self._dbcharset = DBCHARSET
        self._dbport = int(DBPORT)
        self._logger = log
        self.is_connect_first = False
        try:
            self.pool = PooledDB(MySQLdb, self.limit_count, host=self._dbhost, user=self._dbuser, passwd=self._dbpassword, db=self._dbname,
                             port=self._dbport, charset=self._dbcharset, use_unicode=True)
        except:
            if self._logger != None:
                self._logger.warn("无法连接数据库")
            else:
                print ("无法连接数据库")
            self.is_connect_first=True
    def ping(self):
        print (self.pool)
    def do_sql(self, sql):
        res = ''
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close()
            conn.close()
        except :
            res=False

        return res
    def do_sql_one(self, sql):
        res = ''
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchone()
            cursor.close()
            conn.close()
        except :
            res=False

        return res
    def upda_sql(self, sql):
        res = ''
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
        except :
            res = False

        return res



    def insert(self, table, sql):
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
            return {'result': True, 'id': int(cursor.lastrowid)}
        except Exception as err:
            conn.rollback()
            return {'result': False, 'err': err}
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    sql = "SELECT `picture`,`details` FROM `recipe_details` WHERE `recipe_name` like '%虾仁%' "
    print(sql)
    db=HCJ_database()
    t=db.do_sql(sql)
    print(t)
    pass