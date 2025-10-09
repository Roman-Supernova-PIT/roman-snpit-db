import uuid
import pytest

from roman_snpit_db.db import PhrostyLightcurve

from basetest import BaseTestDB


class TestPhrostyLightcurve( BaseTestDB ):

    @pytest.fixture
    def basetest_setup( self, stupid_provenance, stupid_object ):
        self.cls = PhrostyLightcurve
        self.safe_to_modify = [ 'collection', 'subset', 'filter', 'filepath' ]
        self.columns = set( self.safe_to_modify )
        self.columns.update( [ 'id', 'provenance_id', 'diaobject_id' ] )
        self.uniques = []
        self.obj1 = PhrostyLightcurve( id=uuid.uuid4(),
                                       provenance_id=stupid_provenance,
                                       diaobject_id=stupid_object,
                                       collection='coll1',
                                       subset='sub1',
                                       filter='a',
                                       filepath='/dev/null' )
        self.dict1 = { k: getattr( self.obj1, k ) for k in self.columns }
        self.obj2 = PhrostyLightcurve( id=uuid.uuid4(),
                                       provenance_id=stupid_provenance,
                                       diaobject_id=stupid_object,
                                       collection='coll2',
                                       subset='sub2',
                                       filter='b',
                                       filepath='/bin/false' )
        self.dict2 = { k: getattr( self.obj2, k ) for k in self.columns }
        self.dict3 = { 'id': uuid.uuid4(),
                       'provenance_id': stupid_provenance,
                       'diaobject_id': stupid_object,
                       'collection': 'coll3',
                       'subset': 'sub3',
                       'filter': 'c',
                       'filepath': '/bin/true' }
