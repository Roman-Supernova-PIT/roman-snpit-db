import uuid
import pytest

from roman_snpit_db.db import DiaObject

from basetest import BaseTestDB


class TestDiaObject( BaseTestDB ):

    @pytest.fixture
    def basetest_setup( self, stupid_provenance ):
        self.cls = DiaObject
        self.safe_to_modify = [ 'name', 'collection', 'subset', 'ra', 'dec',
                                'tdiscovery', 'tmax', 'tstart', 'tend', 'properties' ]
        self.columns = set( self.safe_to_modify )
        self.columns.update( [ 'id', 'provenance_id' ] )
        self.uniques = []
        self.obj1 = DiaObject( id=uuid.uuid4(),
                               provenance_id=stupid_provenance,
                               name='obj1',
                               collection='coll1',
                               subset='sub1',
                               ra=128.,
                               dec=42.,
                               tdiscovery=60015.,
                               tmax=60030.,
                               tstart=60010.,
                               tend=60060. )
        self.dict1 = { k: getattr( self.obj1, k ) for k in self.columns }
        self.obj2 = DiaObject( id=uuid.uuid4(),
                               provenance_id=stupid_provenance,
                               name='obj2',
                               collection='coll2',
                               subset='sub2',
                               ra=64.,
                               dec=-13.,
                               tdiscovery=60016.,
                               tmax=60031.,
                               tstart=60011.,
                               tend=60061. )
        self.dict2 = { k: getattr( self.obj2, k ) for k in self.columns }
        self.dict3 = { 'id': uuid.uuid4(),
                       'provenance_id': stupid_provenance,
                       'name': 'obj3',
                       'collection': 'coll3',
                       'subset': 'sub3',
                       'ra': 23.,
                       'dec': -42.,
                       'tdiscovery': 60017.,
                       'tmax': 60032.,
                       'tstart': 60012.,
                       'tend': 60062. }
