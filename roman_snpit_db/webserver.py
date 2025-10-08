import flask
# import flask_session

from roman_snpit_db.baseview import BaseView


# ======================================================================

class MainPage( BaseView ):
    def dispatch_request( self ):
        return flask.render_template( "fastdb_webap.html" )
