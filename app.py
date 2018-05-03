# contoh data:
# entries = [
#            {
#                '_id':1,
#                'label': [ 'lorem', 'ipsum', 'dolor' ],
#                'text': [ 'O', 'B-TIME', 'O' ]
#            },
#            {
#                '_id':2,
#                'label': [ 'lorem', ',', 'ipsum', 'dolor' ],
#                'text': [ 'O', 'O', 'B-PLACE', 'I-PLACE' ]
#            },
#            {
#                '_id': 3,
#                'label': ['lorem', 'ipsum', 'dolor', 'sit', '?'],
#                'text': ['B-NAME', 'B-TIME', 'O', 'O', 'O']
#            }
#        ]
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, abort, url_for, jsonify
from pagination import Pagination
from database.md import MongoDB
import os

IS_PROD = os.environ.get('IS_HEROKU', None)
PER_PAGE = 5
COUNT_ALL = 0
if IS_PROD:
    database = MongoDB('')
    COUNT_ALL = database.getAll().count()
else:
    database = MongoDB('config.ini', config_name = 'MONGO_ONLINE')
app = Flask(__name__)

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

def get_count_all():
    return COUNT_ALL

@app.route("/api/<string:id>/<int:index>", methods = ['PUT', 'POST'])
def replace_tag(id,index):
    app.logger.debug(request.get_json())
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
    app.logger.debug("timestamp : "+id)
    time = database.getTimestamp(id)
    return jsonify({'_id':id,'timestamp':time})


def main():
    COUNT_ALL = database.getAll().count()
    print(COUNT_ALL)
    app.run(debug=True)

if __name__ == '__main__':
    main()
