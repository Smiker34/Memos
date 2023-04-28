import re
from quopri import decodestring
from sqlite3 import connect


class Memo:
    auto_id = 0

    def __init__(self, title, color, create_date, text=None, list=None):
        self.id = Memo.auto_id
        Memo.auto_id += 1
        self.title = title
        self.text = text
        self.color = f'style="background-color: {color};"'
        self.text_color = f'style="color: {color}; filter: invert(100%);"'
        self.create_date = create_date
        self.list = list


class MemoMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'memos'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, title, text, color, list, create_date = item
            if list == 'None':
                memo = Memo(title, re.search(r'#\w{6}', color)[0], create_date, text)
            else:
                memo = Memo(title, re.search(r'#\w{6}', color)[0], create_date, text, list[1:-1].replace("'", '').split(','))
            memo.id = id
            result.append(memo)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, title, text, color, list, create_date FROM {self.tablename} WHERE id={id}"
        self.cursor.execute(statement)
        result = self.cursor.fetchone()
        if result:
            return Memo(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (title, text, color, list, create_date) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(statement, (obj.title, obj.text, obj.color, f'{obj.list}', obj.create_date))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET title=?, text=?, color=?, list=? WHERE id=?"
        self.cursor.execute(statement, (obj.title, obj.text, obj.color, f'{obj.list}', obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id={obj.id}"
        self.cursor.execute(statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('patterns.sqlite')
mapper = MemoMapper(connection)


class Engine:
    def __init__(self):
        self.memos = mapper.all()

    @staticmethod
    def create_memo(title, color, create_date, text=None, list=None):
        new_memo = Memo(title, color, create_date, text, list)
        mapper.insert(new_memo)
        return new_memo

    def get_memo(self, title):
        for item in self.memo:
            if item.title == title:
                return item
        return None

    def find_memo_by_id(self, id):
        for item in self.memos:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    def update_memo(self, id, title=None, color=None, text=None, list=None):
        for item in self.memos:
            print('item', item.id)
            if item.id == id:
                if title:
                    item.title = title
                if text:
                    item.text = text
                if color:
                    item.color = f'style="background-color: {color};"'
                    item.text_color = f'style="color: {color}; filter: invert(100%);"'
                if list:
                    item.list = list
            mapper.update(item)

    def delete_memo(self, id):
        for item in self.memos:
            print('item', item.id)
            if item.id == id:
                mapper.delete(item)
                self.memos.pop(self.memos.index(item))

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')