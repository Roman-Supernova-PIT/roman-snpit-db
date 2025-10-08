import uuid
import pytest

from roman_snpit_db.db import DiaObjectPosition, DBCon

from basetest import BaseTestDB


class TestDiaObjectPosition( BaseTestDB ):

    @pytest.fixture( scope="class" )
    def stupid_provenances( self ):
        try:
            with DBCon() as con:
                con.execute_nofetch( "INSERT INTO provenance(id,environment,env_major,env_minor,"
                                     "process,major,minor) VALUES ('blah1',0,0,0,'foo',0,0)" )
                con.commit()
            yield True
        finally:
            with DBCon() as con:
                con.execute_nofetch( "DELETE FROM provenance WHERE id='blah1'" )
                con.commit()


    @pytest.fixture( scope="class" )
    def stupid_object( self, stupid_provenances ):
        try:
            objid = uuid.uuid4()
            with DBCon() as con:
                con.execute_nofetch( "INSERT INTO diaobject(id,provenance_id,name,collection) "
                                     "VALUES(%(id)s,'blah1','foo','bar')",
                                     { 'id': objid } )
                con.commit()
            yield objid
        finally:
            with DBCon() as con:
                con.execute_nofetch( "DELETE FROM diaobject WHERE id=%(id)s", { 'id': objid } )
                con.commit()


    @pytest.fixture
    def basetest_setup( self, stupid_provenances, stupid_object ):
        self.cls = DiaObjectPosition
        self.safe_to_modify = [ 'ra', 'ra_err', 'dec', 'dec_err', 'ra_dec_covar', 'calculated_at' ]
        self.columns = set( self.safe_to_modify )
        self.columns.update( [ 'id', 'diaobject_id', 'provenance_id' ] )
        self.uniques = []
        self.obj1 = DiaObjectPosition( id=uuid.uuid4(),
                                       provenance_id='blah1',
                                       diaobject_id=stupid_object,
                                       ra=128.,
                                       dec=42.,
                                       ra_err=0.001,
                                       dec_err=0.001,
                                       ra_dec_covar=1e-6 )
        self.dict1 = { k: getattr( self.obj1, k ) for k in self.columns }
        self.obj2 = DiaObjectPosition( id=uuid.uuid4(),
                                       provenance_id='blah1',
                                       diaobject_id=stupid_object,
                                       ra=64.,
                                       dec=-13.,
                                       ra_err=0.002,
                                       dec_err=0.002,
                                       ra_dec_covar=2e-6 )
        self.dict2 = { k: getattr( self.obj2, k ) for k in self.columns }
        self.dict3 = { 'id': uuid.uuid4(),
                       'provenance_id': 'blah1',
                       'diaobject_id': stupid_object,
                       'ra': 23.,
                       'dec': -42.,
                       'ra_err': 0.003,
                       'dec_err': 0.003 }
