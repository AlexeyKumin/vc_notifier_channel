import sqlite3

class SQLighter:

    def __init__(self, database):
        # подключаемся к БД и сохраняем курсор соединения
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_last_post(self):
        # получаем последний добавленный пост в таблицу
        with self.connection:
            return self.cursor.execute("SELECT MAX(id), link FROM `last_posts`").fetchall()[0][1]

    def table_is_empty(self):
        # проверяем таблицу на пустоту
        with self.connection:
            result = self.cursor.execute('SELECT count(*) FROM `last_posts`').fetchall()[0][0]
            return not bool(result)

    def add_new_post(self, link):
        # добавляем новый пост
        with self.connection:
            return self.cursor.execute("INSERT INTO `last_posts` (`link`) VALUES(?)", (link,))

    def close(self):
        self.connection.quit()