from flask import Flask, send_file, request
from flask_restx import Api, Resource, Namespace, reqparse, fields
from werkzeug.datastructures import FileStorage
from audio import convert

app = Flask(__name__)

api = Api(app,
          version='1.0',
          title='2d to 8d convert',
          description='Convert 2d audi to 8d',
          license='MIT',
          doc='/docs/',

          )

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)
upload_parser.add_argument('period', type=int, required=True)
upload_parser.add_argument('outputName', type=str, required=True)

# upload = api.model("convert", {
#     "period": fields.Integer,
#     "outputName": fields.String
# })


@api.route('/convert')
class Convert(Resource):
    @api.expect(upload_parser)
    @api.doc("upload file")
    def post(self):
        args = upload_parser.parse_args()
        file = args['file']
        period = args['period']
        if period == "" or 0:
            period = 200
        outputName = args['outputName']
        if outputName == "":
            outputName = file.filename[:-4] + ' - 8D.mp3'
        if outputName[-4:] != '.mp3':
            outputName += '.mp3'
        # if outputName[-4:] != '.mp3':
        #     outputName += '.mp3'
        # if output_name[-4:] != '.mp3':
        #     output_name += '.mp3'
        file.save(file.filename)
        convert(file.filename, outputName, int(period))
        return send_file(outputName, as_attachment=True)


@api.route("/hello")
class Index(Resource):
    def get(self):
        return 'Hello World!'


if __name__ == '__main__':
    app.run()
