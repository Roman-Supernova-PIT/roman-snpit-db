__all__ = [ 'setup_flask_app' ]
import flask
import flask_session

from rkwebutil import rkauth_flask

from snpit_utils.config import Config
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

class GetProvenance( BaseView ):
    def get_upstreams( self, prov, con ):
        rows, cols = con.execute( "SELECT p.* FROM provenance p "
                                  "INNER JOIN provenance_upstream u ON u.upstream_id=p.id "
                                  "WHERE u.downstream_id=%(id)s",
                                  { 'id': prov['id'] } )
        if ( rows is None ) or ( len(rows) == 0 ):
            prov[ 'upstreams' ] = {}
        else:
            prov[ 'upstreams' ] = [ { cols[i]: row[i] for i in range( len(cols) ) } for row in rows ]
            for prov in prov[ 'upstreams' ]:
                self.get_upstreams( prov, con )


    def do_the_things( self, provid ):
        with db.DBCon() as con:
            rows, cols = con.execute( "SELECT * FROM provenance WHERE id=%(id)s", { 'id': provid } )
            if len(rows) == 0:
                return f"Unknown provenance {provid}", 500
            if len(rows) > 1:
                return f"Database corruption!  More than one provenance with id {provid}!", 500
            prov = { cols[i]: rows[0][i] for i in range( len(cols) ) }
            self.get_upstreams( prov, con )

        return prov


# ======================================================================

class CreateProvenance( BaseView ):
    def do_the_things( self ):
        if not flask.request.is_json:
            return "Expected JSON payoad", 500
        data = flask.request.json
        if 'upstreams' in data:
            upstream_ids = [ p['id'] for p in data['upstreams'] ]
            del data['upstreams']
        elif 'upstream_ids' in data:
            upstream_ids = data['upstream_ids']
            del data['upstream_ids']
        else:
            upstream_ids = []

        prov = db.Provenance( **data )
        with db.DBCon() as dbcon:
            prov.insert( dbcon=dbcon.con, nocommit=True, refresh=False )
            for uid in upstream_ids:
                dbcon.execute( "INSERT INTO provenance_upstream(downstream_id,upstream_id) "
                               "VALUES (%(down)s,%(up)s)",
                               { 'down': prov.id, 'up': uid } )
            dbcon.commit()

        return { "status": "ok" }



# ======================================================================

urls = {
    "/": MainPage,
    "/getprovenance/<provid>": GetProvenance,
    "/createprovenance": CreateProvenance
}
