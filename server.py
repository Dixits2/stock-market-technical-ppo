from flask import Flask, request
from flask_restful import Resource, Api
import os
import pandas as pd
import datetime

files = [i for i in os.listdir("Stocks") if i.endswith("txt")]
files_testing = [i for i in os.listdir("TestingStocks") if i.endswith("txt")]

current_file = 0

current_file_testing = 0

app = Flask(__name__)
api = Api(app)


class Basic(Resource):
	def get(self):
		global files
		global current_file
		with app.open_resource('Stocks/' + files[current_file]) as f:
			contents = f.read()
			if current_file == (len(files) - 1):
				current_file = 0
			else:
				current_file += 1
			return contents.decode('utf-8')

class Testing(Resource):
	def get(self):
		global files_testing
		global current_file_testing
		with app.open_resource('TestingStocks/' + files_testing[current_file_testing]) as f:
			print(files_testing[current_file_testing])
			contents = f.read()
			if current_file_testing == (len(files_testing) - 1):
				current_file_testing = 0
			else:
				current_file_testing += 1
			return contents.decode('utf-8')
		
api.add_resource(Basic, '/')
api.add_resource(Testing, '/testing')

if __name__ == '__main__':
	 app.run(port='5000')