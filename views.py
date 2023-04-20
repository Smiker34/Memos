import re
from framework.templator import render
from patterns.сreational_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug

site = Engine()
logger = Logger('main')

routes = {}


@AppRoute(routes=routes, url='/')
class Memos:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)

class NotFound404:
    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/create_memo/')
class CreateMemo:
    @Debug(name='Create_Memo')
    def __call__(self, request):

        if request['method'] == 'POST':
            data = request['data']
            title, text, color = data['title'], data['text'], data['color']
            title = site.decode_value(title)
            text = site.decode_value(text)
            color = site.decode_value(color)

            if not title:
                return '200 OK', render('create_memo.html', error='Введите название!', date=request.get('date', None))

            new_memo = site.create_memo(title, text, color, create_date=request.get('date', None))
            site.memos.append(new_memo)
            return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)
        else:
            return '200 OK', render('create_memo.html', date=request.get('date', None))


@AppRoute(routes=routes, url='/memo_page/')
class MemoPage:
    memo_id = -1

    @Debug(name='Memo_Page')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            try:
                if data['delete']:
                    site.delete_memo(self.memo_id)
                    return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)
            except:
                pass

            title, text, color = data['title'], data['text'], data['color']
            title = site.decode_value(title)
            text = site.decode_value(text)
            color = site.decode_value(color)

            if self.memo_id != -1:
                site.update_memo(self.memo_id, title, text, color)

            return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)

        else:
            try:
                self.memo_id = int(request['request_params']['id'])
                memo = site.find_memo_by_id(int(self.memo_id))

                return '200 OK', render('memo_page.html',
                                        id=memo.id,
                                        name=memo.title,
                                        text=memo.text,
                                        memo_date=memo.create_date,
                                        color=re.search(r'#\w{6}', memo.color)[0],
                                        date=request.get('date', None))
            except KeyError:
                return '200 OK', 'No categories have been added yet'
