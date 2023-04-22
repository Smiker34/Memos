from quopri import decodestring
from sqlite3 import connect


class Memo:
    auto_id = 0

    def __init__(self, title, text, color, create_date):
        self.id = Memo.auto_id
        Memo.auto_id += 1
        self.title = title
        self.text = text
        if len(color) > 7:
            self.color = color
        else:
            self.color = f'style="background-color: {color};"'
        self.text_color = f'style="color: {color}; filter: invert(100%);"'
        self.create_date = create_date


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
            id, title, text, color, create_date = item
            memo = Memo(title, text, color, create_date)
            memo.id = id
            result.append(memo)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, title, text, color, create_date FROM {self.tablename} WHERE id={id}"
        self.cursor.execute(statement)
        result = self.cursor.fetchone()
        if result:
            return Memo(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (title, text, color, create_date) VALUES (?, ?, ?, ?)"
        self.cursor.execute(statement, (obj.title, obj.text, obj.color, obj.create_date))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET title=?, text=?, color=? WHERE id=?"
        self.cursor.execute(statement, (obj.title, obj.text, obj.color, obj.id))
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
    def create_memo(title, text, color, create_date):
        new_memo = Memo(title, text, color, create_date)
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

    def update_memo(self, id, title=None, text=None, color=None):
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