
from api import create_app
from flask_restful import Api
from .modelos import db
from .vistas import VistaSignUp, VistaTarea, VistaTareas, VistaUsuariosTarea, VistaLogIn
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
cors = CORS(app)

api = Api(app)
api.add_resource(VistaTareas, '/api/tasks')
api.add_resource(VistaTarea, '/api/tasks/<int:id_task>')
api.add_resource(VistaSignUp, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaUsuariosTarea, '/api/files/<string:filename>')
jwt = JWTManager(app)