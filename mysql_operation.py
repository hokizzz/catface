# -*- coding: utf-8 -*-
# Time : 2024/12/18 0:18
# Author : lirunsheng
# User : l'r's
# Software: PyCharm
# File : mysql_operation.py
import datetime

import pymysql

class Database:
    def __init__(self, host, user, password, database):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=3306,
            charset = 'utf8'
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

class Cat:
    def __init__(self, db):
        self.db = db

    def add(self, name, time, weight, location=None, image_data=None):
        query = """
        INSERT INTO cat (name, weight, time, location, image_data)
        VALUES (%s, %s, %s, %s, %s)
        """
        print(query)
        params = (name, weight, time, location, image_data)
        self.db.execute_query(query, params)

    def update(self, cat_id, name=None, weight=None, time=None, location=None, image_data=None):
        query = "UPDATE cat SET "
        params = []

        if name is not None:
            query += "name = %s, "
            params.append(name)
        if weight is not None:
            query += "weight = %s, "
            params.append(weight)
        if time is not None:
            query += "time = %s, "
            params.append(time)
        if location is not None:
            query += "location = %s, "
            params.append(location)
        if image_data is not None:
            query += "image_data = %s, "
            params.append(image_data)

        # Remove the last comma and space
        query = query.rstrip(', ')

        query += " WHERE id = %s"
        params.append(cat_id)

        self.db.execute_query(query, tuple(params))

    def query(self, name=None, cat_id=None, latest=False):
        query = "SELECT * FROM cat"
        params = []

        if name:
            query += " WHERE name = %s"
            params.append(name)

        if cat_id:
            query += " AND id = %s"
            params.append(cat_id)

        if latest:
            query += " ORDER BY time DESC LIMIT 1"

        return self.db.fetch_all(query, tuple(params))

class CatFood:
    def __init__(self, db):
        self.db = db

    def add(self, weight, remaining, last_weight, time, food_type):
        query = """
        INSERT INTO cat_food (weight, remaining, last_weight, time, type)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (weight, remaining, last_weight, time, food_type)
        self.db.execute_query(query, params)

    def update(self, food_id, weight=None, remaining=None, last_weight=None, time=None, food_type=None):
        query = "UPDATE cat_food SET "
        params = []

        if weight is not None:
            query += "weight = %s, "
            params.append(weight)
        if remaining is not None:
            query += "remaining = %s, "
            params.append(remaining)
        if last_weight is not None:
            query += "last_weight = %s, "
            params.append(last_weight)
        if time is not None:
            query += "time = %s, "
            params.append(time)
        if food_type is not None:
            query += "type = %s, "
            params.append(food_type)

        # Remove the last comma and space
        query = query.rstrip(', ')

        query += " WHERE id = %s"
        params.append(food_id)

        self.db.execute_query(query, tuple(params))

    def query(self, food_id=None):
        query = "SELECT * FROM cat_food"
        if food_id:
            query += " WHERE id = %s"
            return self.db.fetch_all(query, (food_id,))
        else:
            return self.db.fetch_all(query)

if __name__ == '__main__':
    db = Database(host="120.25.173.40", user="root", password="root_123R", database="face_cat")

    # 创建Cat和CatFood对象
    cat = Cat(db)
    cat_food = CatFood(db)

    # 添加一只猫
    cat.add("Kitty", 5.4, "2024-12-18 10:00:00", "Living Room", None)

    # 查询所有猫
    cats = cat.query()
    print(cats)

    # 更新猫的体重
    cat.update(1, weight=6.0)

    # 添加猫粮
    cat_food.add(1.2, "Yes", 0.8, "2024-12-18 09:00:00", "Dry Food")

    # 查询所有猫粮
    cat_foods = cat_food.query()
    print(cat_foods)

    # 更新猫粮的剩余量
    cat_food.update(1, remaining="No")
