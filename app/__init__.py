import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_cors import CORS

from config import Config

login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    login.init_app(app)
    login.login_view = 'auth.login'

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app import routes, models
    app.register_blueprint(routes.bp)

    cache_servers = os.environ.get('MEMCACHIER_SERVERS')
    if cache_servers == None:
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
        cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
        cache.init_app(app,
            config={'CACHE_TYPE': 'saslmemcached',
                    'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                    'CACHE_MEMCACHED_USERNAME': cache_user,
                    'CACHE_MEMCACHED_PASSWORD': cache_pass,
                    'CACHE_OPTIONS': { 'behaviors': {
                        # Faster IO
                        'tcp_nodelay': True,
                        # Keep connection alive
                        'tcp_keepalive': True,
                        # Timeout for set/get requests
                        'connect_timeout': 2000, # ms
                        'send_timeout': 750 * 1000, # us
                        'receive_timeout': 750 * 1000, # us
                        '_poll_timeout': 2000, # ms
                        # Better failover
                        'ketama': True,
                        'remove_failed': 1,
                        'retry_timeout': 2,
                        'dead_timeout': 30}}})
    return app
