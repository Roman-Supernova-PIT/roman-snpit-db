import uuid
import pytest

from roman_snpit_db.db import CampariLightcurve, DBCon

from basetest import BaseTestDB


class TestCampariLightcurve( BaseTestDB ):

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
        self.cls = CampariLightcurve
        self.safe_to_modify = [ 'collection', 'subset', 'filter', 'filepath' ]
        self.columns = set( self.safe_to_modify )
        self.columns.update( [ 'id', 'provenance_id', 'diaobject_id' ] )
        self.uniques = []
        self.obj1 = CampariLightcurve( id=uuid.uuid4(),
                                       provenance_id='blah1',
                                       diaobject_id=stupid_object,
                                       collection='coll1',
                                       subset='sub1',
                                       filter='a',
                                       filepath='/dev/null' )
        self.dict1 = { k: getattr( self.obj1, k ) for k in self.columns }
        self.obj2 = CampariLightcurve( id=uuid.uuid4(),
                                       provenance_id='blah1',
                                       diaobject_id=stupid_object,
                                       collection='coll2',
                                       subset='sub2',
                                       filter='b',
                                       filepath='/bin/false' )
        self.dict2 = { k: getattr( self.obj2, k ) for k in self.columns }
        self.dict3 = { 'id': uuid.uuid4(),
                       'provenance_id': 'blah1',
                       'diaobject_id': stupid_object,
                       'collection': 'coll3',
                       'subset': 'sub3',
                       'filter': 'c',
                       'filepath': '/bin/true' }
