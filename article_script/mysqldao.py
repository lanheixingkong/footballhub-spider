import mysql.connector
from DBUtils.PooledDB import PooledDB
import logging; logging.basicConfig(level=logging.INFO)

class MysqlDao:

    def __init__(self, host = "localhost", user = "root", password = "root123", database = "footballhub", charset="utf8"):
        self.__dbconfig = {
            "host": host,
            "database": database,
            "user":   user,
            "password": password
        }
        pool_size = 3
        self.__pool = PooledDB(mysql.connector, pool_size, database=database, user=user, password=password, host=host)
        # self.__cnx = mysql.connector.connect(pool_name = "mypool",
        #                               pool_size = 3,
        #                               **dbconfig)
        # self.__cnxpool = pooling.MySQLConnectionPool(pool_name = "mypool", pool_size = 3, **dbconfig)

    def select(self, sql, args, size=None):
        #logging.info(sql, args)
        # conn = self.__cnxpool.get_connection()

#         conn = mysql.connector.connect(user='root', password = 'root123', database='footballhub')
        # conn = mysql.connector.connect(
        #                                 user = self.__dbconfig['user'],
        #                                 password = self.__dbconfig['password'],
        #                                 database = self.__dbconfig['database'],
        #                                 host = self.__dbconfig['host'])

        conn = self.__pool.connection()
        cur = conn.cursor()
        cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = cur.fetchmany(size)
        else:
            rs = cur.fetchall()
        cur.close()
        conn.close()
        logging.info('rows returned: %s' % len(rs))
        return rs

    def execute(self, sql, args):
        #logging.info(sql)
        # conn = mysql.connector.connect(
        #                                 user = self.__dbconfig['user'],
        #                                 password = self.__dbconfig['password'],
        #                                 database = self.__dbconfig['database'],
        #                                 host = self.__dbconfig['host'])

        conn = self.__pool.connection()
        try:
            cur = conn.cursor()
            cur.execute(sql.replace('?', '%s'), args or ())
            affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
        except BaseException as e:
            conn.close()
            raise
        return affected
