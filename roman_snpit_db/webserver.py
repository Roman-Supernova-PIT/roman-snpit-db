__all__ = [ 'setup_flask_app' ]
import flask
import flask_session

from rkwebutil import rkauth_flask

from snpit_util.config import Config
from roman_snpit_db import db
from roman_snpit_db.baseview import BaseView


# ======================================================================

def setup_flask_app( application ):
    global urls

    application.config.from_mapping(
        SECRET_KEY=Config.get().value( 'webserver.flask_secret_key' ),
        SESSION_COOKIE_PATH='/',
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=True,
        SESSION_USE_SIGNER=True,
        SESSION_FILE_DIR=Config.get().value( 'webserver.sessionstore' ),
        SESSION_FILE_THRESHOLD=1000,
    )

    _server_session = flask_session.Session( application )

    dbhost, dbport, dbname, dbuser, dbpasswd = db.get_connect_info()
    rkauth_flask.RKAuthConfig.setdbparams(
        db_host=dbhost,
        db_port=dbport,
        db_name=dbname,
        db_user=dbuser,
        db_password=dbpasswd,
        email_from = Config.get().value( 'webserver.emailfrom' ),
        email_subject = 'roman-snpit-db password reset',
        email_system_name = 'roman-snpit-db',
        smtp_server = Config.get().value( 'webserver.smtpserver' ),
        smtp_port = Config.get().value( 'webserver.smtpport' ),
        smtp_use_ssl = Config.get().value( 'webserver.smtpusessl' ),
        smtp_username = Config.get().value( 'webserver.smtpusername' ),
        smtp_password = Config.get().value( 'webserver.smtppassword' )
    )
    application.register_blueprint( rkauth_flask.bp )

    usedurls = {}
    for url, cls in urls.items():
        if url not in usedurls.keys():
            usedurls[ url ] = 0
            name = url
        else:
            usedurls[ url ] += 1
            name = f'{url}.{usedurls[url]}'

        application.add_url_rule (url, view_func=cls.as_view(name), methods=['GET', 'POST'], strict_slashes=False )


# ======================================================================

class MainPage( BaseView ):
    def dispatch_request( self ):
        return flask.render_template( "romansnpitdb.html" )


# ======================================================================

urls = {
    "/": MainPage
}
