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
        if request['method'] == 'POST':
            data = request['data']
            search = data['search']
            search = site.decode_value(search)

            if not search:
                return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)

            search_result = []
            for memo in site.memos:
                if re.match(search, f'{memo.title}'):
                    search_result.append(memo)
                    continue

                elif memo.text != None:
                    if re.match(search, f'{memo.text}'):
                        search_result.append(memo)
                        continue

                elif memo.list != None:
                        for point in memo.list:
                            if re.match(search, point):
                                search_result.append(memo)
                                break
                            else:
                                continue
                else:
                    continue

            return '200 OK', render('index.html', date=request.get('date', None), objects_list=search_result)
        else:
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
            color = site.decode_value(color)

            if not title:
                return '200 OK', render('create_memo.html', error='Введите название!', date=request.get('date', None))

            new_memo = site.create_memo(title, color, create_date=request.get('date', None), text=site.decode_value(text))
            site.memos.append(new_memo)
            return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)
        else:
            return '200 OK', render('create_memo.html', date=request.get('date', None))


@AppRoute(routes=routes, url='/create_list_memo/')
class CreateListMemo:
    @Debug(name='Create_List_Memo')
    def __call__(self, request):

        if request['method'] == 'POST':
            data = request['data']
            title, color = data.pop('title'), data.pop('color')
            title = site.decode_value(title)
            color = site.decode_value(color)

            if not title:
                return '200 OK', render('create_list_memo.html', error='Введите название!', date=request.get('date', None))

            new_memo = site.create_memo(title, color, create_date=request.get('date', None), list=list(data.values()))
            site.memos.append(new_memo)
            return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)
        else:
            return '200 OK', render('create_list_memo.html', date=request.get('date', None))


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
            try:
                if data['text']:
                    title, text, color = data['title'], data['text'], data['color']
                    title = site.decode_value(title)
                    text = site.decode_value(text)
                    color = site.decode_value(color)

                    if self.memo_id != -1:
                        site.update_memo(self.memo_id, title, color, text)

                    return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)
            except:
                title, color = data.pop('title'), data.pop('color')
                title = site.decode_value(title)
                color = site.decode_value(color)

                if self.memo_id != -1:
                    site.update_memo(self.memo_id, title, color, list=list(data.values()))

                return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.memos)

        else:
            try:
                self.memo_id = int(request['request_params']['id'])
                memo = site.find_memo_by_id(int(self.memo_id))

                return '200 OK', render('memo_page.html',
                                        id=memo.id,
                                        name=memo.title,
                                        text=memo.text,
                                        list=memo.list,
                                        memo_date=memo.create_date,
                                        color=re.search(r'#\w{6}', memo.color)[0],
                                        date=request.get('date', None))
            except KeyError:
                return '200 OK', 'No categories have been added yet'
