from flask import Flask, render_template, request
from main import get_property_for_sale
import webbrowser

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/listings', methods=['POST'])
def listings():
  zipcode = request.form['zipcode']
  results = get_property_for_sale(zipcode)
  return render_template('listings.html', results=results)


if __name__ == '__main__':
  app.run(debug=True)

webbrowser.open('http://localhost:5000')
