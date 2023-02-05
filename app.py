from flask import Flask, request
import pymongo
from bson.objectid import ObjectId
from cerberus import Validator

schema = {"name": {"type": "string"}, "description": {"type": "string"}}
validator:Validator = Validator(schema)

app = Flask(__name__)

# connect to mongoDB

client = pymongo.MongoClient("mongodb+srv://jenaide:Tamlin100@simpleapi.6yi3q3p.mongodb.net/?retryWrites=true&w=majority")
task_database = client['task_database']
task_collection = task_database['task_collection']

def serialize(mongo_row):
    mongo_row['_id'] = str(mongo_row['_id'])
    return mongo_row

@app.route('/')
def hello():
    return "hello world"

@app.route('/tasks', methods=['GET', 'POST'])
def tasks_view():

    if request.method == 'GET':
        task_cursor = task_collection.find({})
        tasks = []
        for task in task_cursor:
            tasks.append(serialize(task))
        return tasks

    if request.method == 'POST':
        data = request.get_json()
        is_valid = validator.validate(data)
        if is_valid == False:
            return validator.errors
        # insert_one modifies the input object to set the _id when you don't put an _id
        task_collection.insert_one(data)
        serialize(data)
        return data

@app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_view(task_id):
    _task_id = ObjectId(task_id)
    if request.method == 'GET':
        task = task_collection.find_one({"_id":_task_id})
        return serialize(task)
    
    if request.method == 'PUT':
        new_task = request.get_json()
        task_collection.update_one({"_id": _task_id}, {"$set":new_task})
        return new_task
    
    if request.method == 'DELETE':
        task_collection.delete_one({"_id": _task_id})
        return {"response": True}
    
if __name__ == '__main__':
    app.run(debug=True)