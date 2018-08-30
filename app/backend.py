from flask_restful import Resource


class Hello(Resource):
    def get(self):
        return {'hello': 'world'}

    def post(self):
        return {'something': 'else'}