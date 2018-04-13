# contoh data:
# entries = [
#            {
#                '_id':1,
#                'token_tags':
#                [
#                     {'token':'lorem', 'tag':'O'},
#                     {'token':'ipsum', 'tag':'B-TIME'},
#                     {'token':'dolor', 'tag':'O'},
#                     {'token':',', 'tag':','}
#                ]
#            },
#            {
#                '_id':2,
#                'token_tags':
#                [
#                     {'token':'lorem', 'tag':'O'},
#                     {'token':',', 'tag':','},
#                     {'token':'dolor', 'tag':'B-PLACE'},
#                     {'token':'ipsum', 'tag':'I-PLACE'}
#                ]
#            },
#            {
#                '_id':3,
#                'token_tags':
#                [
#                     {'token':'lorem', 'tag':'B-NAME'},
#                     {'token':'ipsum', 'tag':'B-TIME'},
#                     {'token':'dolor', 'tag':'O'},
#                     {'token':'sit', 'tag':'O'},
#                     {'token':'?', 'tag':'?'}
#                ]
#            }
#        ]
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, abort, url_for, jsonify
from pagination import Pagination
from database.md import MongoDB
import os

IS_PROD = os.environ.get('IS_HEROKU', None)

app = Flask(__name__)
if IS_PROD:
    database = MongoDB('')
else:
    database = MongoDB('config.ini', config_name = 'MONGO_ONLINE')

PER_PAGE = 5
DB = 'datasets'
COLLECTION = 'newdataset0'
COUNT_ALL = database.getAll().count()

@app.context_processor
def color_processor():
    def tag_color(tag=''):
        tags = [
                'B-NAME','I-NAME',
                'B-PLACE','I-PLACE',
                'B-TIME','I-TIME',
                'B-INFO','I-INFO'
              ]
        b_tag = [
                  'btn-danger font-weight-bold','btn-danger',
                  'btn-success font-weight-bold','btn-success',
                  'btn-warning font-weight-bold','btn-warning',
                  'btn-info font-weight-bold','btn-info'
                ]
        for x in range(0,len(tags)):
            if tags[x] == tag:
               return b_tag[x]
        return 'default'
    
    def url_for_other_page(page):
        args = request.view_args.copy()
        args['page'] = page
        return url_for(request.endpoint, **args)
    
    return dict(tag_color=tag_color, url_for_other_page=url_for_other_page)

@app.route("/", defaults={ 'page' : 1, 'limit' : PER_PAGE })
@app.route("/page/<int:page>", defaults={ 'limit' : PER_PAGE })
@app.route("/page/<int:page>/limit/<int:limit>")
def index(page, limit):
    entries = get_entries(page, limit)
    
    if not entries and page != 1:
        abort(404)
    count = get_count_all()
    pagination = Pagination(page, limit, count)
    return render_template(
            'show_entries.html', 
            entries=entries,
            pagination=pagination
            )

def get_entries(page, limit):
    if page < 1:
        return []
    
    offset = (page-1)*limit
    
    return database.getEntries(offset, limit)

#    if page < 1:
#        return []
#    elif page == 1:
#        return database.getEntries(None, limit)
#    return database.getEntries(lastkey, limit)
    
#    db = client[DB]
#    c = db[COLLECTION]
#    entries = c.find().skip(offset).limit(limit)
#    a = database.getEntries(offset, limit)
#    app.logger.debug(type(a))

def get_count_all():
#    db = client[DB]
#    c = db[COLLECTION]
#    return c.find().count()
    return COUNT_ALL

@app.route("/api/<string:id>/<int:index>", methods = ['PUT', 'POST'])
def replace_tag(id,index):
    app.logger.debug(request.get_json())
    json = request.get_json()
    
#    db = client[DB]
#    c = db[COLLECTION]
#    c.update_one({'_id': id},
#                 {
#                    '$set': {'label.'+str(index):tag, 'timestamp':datetime.datetime.now()}
#                 })
    data = {'_id':id,'index':index,'tag':json['tag']}
    database.setData(data)
    database.setTimestamp(id)
    return id

@app.route("/api/timestamp/<string:id>", methods = ['GET'])
def get_timestamp(id):
    app.logger.debug("timestamp : "+id)
#    db = client[DB]
#    c = db[COLLECTION]
#    data = c.find_one({'_id': id})
    time = database.getTimestamp(id)
    return jsonify({'_id':id,'timestamp':time})

if __name__ == '__main__':
    app.run(debug=True)
    