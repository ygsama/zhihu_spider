#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql

class SQLUtil(object):

    def __init__(self):
        db = pymysql.connect(host="localhost", user="root", password="root", db="zhihu", charset="utf8")
        self.db = db


    def insert_mysql(self, topic_params, topic_task_params):
        topic_params_sql = 'INSERT INTO topic(id, name, update_time)VALUES ("%s", "%s", "%s")'
        topic_task_params_sql = 'INSERT INTO topic_task(father_id, father_name, child_id, child_name, update_time)VALUES ("%s", "%s", "%s", "%s", "%s")'
        try:
            cursor = self.db.cursor()
            for i in topic_params:
                cursor.execute(topic_params_sql % i)
            for i in topic_task_params:
                cursor.execute(topic_task_params_sql % i)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
            self.db.close()
        finally:
            pass


    def select_topic(self, id):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM topic_task WHERE father_id="%s"' % id)
        for c in cursor:
            return True
        return False

if __name__ == '__main__':
    sql_helper = SQLUtil()
    if sql_helper.select_topic("192551432"):
        print("add")