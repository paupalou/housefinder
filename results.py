from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_DBNAME'] = 'housefinder'
app.config['MONGO_CONNECT'] = False
app.debug = True
mongo = PyMongo(app, config_prefix='MONGO')

# filters params values
filter_fields = ['price', 'meters', 'rooms']
filter_types = ['lt', 'gt']


@app.route('/')
def all():
    houses = mongo.db.houses.find()
    return render_template('list.html', items=houses, results=houses.count())


@app.route('/<filter>/<type>/<int:quantity>')
def filter_results(filter, type, quantity):
    def _check_params(errors):
        if filter not in filter_fields:
            errors.append('Filter introduced is not correct')
            return False
        if type not in filter_types:
            errors.append('Type introduced is not correct')
            return False
        if not isinstance(quantity, int):
            errors.append('Quantity is not numeric')
            return False
        return True

    errors = []
    if _check_params(errors):
        condition = {filter: {'$'+type: quantity}}
        houses = mongo.db.houses.find(condition)
        results = houses.count()
    else:
        houses = []
        results = 0
    return render_template(
            'list.html',
            items=houses,
            errors=errors,
            results=results
            )


if __name__ == '__main__':
    app.run()
