from flask.ext.restful import Resource, reqparse
from flask import send_file

file_get_parser = reqparse.RequestParser()
file_get_parser.add_argument('file_path', dest='file_path', type=str,
                             required=True, help="File_path")

# READ CONFIG FILE
config = {}
execfile("config.py", config)


class DownloadResults(Resource):

    def get(self):
        args = file_get_parser.parse_args()
        try:
            response = send_file(args.file_path, as_attachment=True)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Content-Type', 'application/force-download')
            return response
        except Exception as e:
            print e
            return 404



