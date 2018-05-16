# -*- coding: utf-8 -*-
# contoh data:
# entries = [
#            {
#                '_id':1,
#                'label': [ 'lorem', 'ipsum',  'dolor' ],
#                'text' : [ 'O',     'B-TIME', 'O'     ],
#                'timestamp': 2018-03-29 15:11:09.130000,
#                'type': 'bazaar'
#            },
#            {
#                '_id':2,
#                'label': [ 'lorem', ',', 'ipsum',   'dolor'   ],
#                'text' : [ 'O',     'O', 'B-PLACE', 'I-PLACE' ],
#                'timestamp': 2018-05-16 10:40:10.674000,
#                'type': 'pendidikan'
#            },
#            {
#                '_id': 3,
#                'label': [ 'lorem',  'ipsum',  'dolor', 'sit', '?' ],
#                'text' : [ 'B-NAME', 'B-TIME', 'O',     'O',   'O' ],
#                'timestamp': 2018-05-16 10:41:48.999000,
#            }
#        ]

from flask import Flask, render_template, request, abort, url_for, jsonify
from pagination import Pagination
from database.md import MongoDB
from adapter import DataAdapter
import os
import json

IS_PROD = os.environ.get('IS_HEROKU', None)
DEBUG = True
PER_PAGE = 5
COUNT_ALL = 0

app = Flask(__name__)
app.debug = DEBUG

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
    # print(type(entries))
    
    if not entries and page != 1:
        abort(404)
    count = get_count_all()
    pagination = Pagination(page, limit, count)
    return render_template(
        'show_entries.html',
        entries=entries,
        pagination=pagination
    )

@app.route("/test", defaults={'page': 1, 'limit': PER_PAGE})
@app.route("/page/<int:page>/test", defaults={'limit': PER_PAGE})
@app.route("/page/<int:page>/limit/<int:limit>/test")
def test(page, limit):
    entries = get_entries(page, limit)

    if not entries and page != 1:
        abort(404)
    count = get_count_all()
    pagination = Pagination(page, limit, count)

    crf = DataAdapter(entries)
    tested = crf.tag_sents()
    accuracy = crf.evaluate()

    return render_template(
        'show_test.html',
        entries=[get_entries(page, limit), tested],
        pagination=pagination,
        accuracy=accuracy
    )

def get_entries(page, limit):
    if page < 1:
        return []
    
    offset = (page-1)*limit
    
    return database.getEntries(offset, limit)

def get_count_all():
    return COUNT_ALL

@app.route("/api/<string:id>/<int:index>", methods = ['PUT', 'POST'])
def replace_tag(id,index):
    # print(request.get_json())
    json = request.get_json()
    
    data = {'_id':id,'index':index,'tag':json['tag']}
    database.setData(data)
    database.setTimestamp(id)
    return id

@app.route("/api/type/<string:id>/", methods = ['POST'])
@app.route("/api/type/<string:id>/<string:type>", methods = ['POST'])
def set_type(id,type = None):
    if type is None:
        database.removeType(id)
        return id
    database.setType(id,type.lower())
    return id

@app.route("/api/timestamp/<string:id>", methods = ['GET'])
def get_timestamp(id):
    # print("timestamp : "+id)
    time = database.getTimestamp(id)
    return jsonify({'_id':id,'timestamp':time})

@app.route("/refresh")
def train():
    crf = DataAdapter()
    a = database.getTagged()
    crf.train(a)
    return json.dumps({'tagged':a.count(),'success': True}), 200, {'ContentType': 'application/json'}

def main():
    print(COUNT_ALL)
    app.run()


if IS_PROD:
    database = MongoDB('')
    COUNT_ALL = database.getAll().count()
else:
    database = MongoDB('config.ini', config_name='MONGO_ONLINE')
    COUNT_ALL = database.getAll().count()

    if __name__ == '__main__':
        main()
