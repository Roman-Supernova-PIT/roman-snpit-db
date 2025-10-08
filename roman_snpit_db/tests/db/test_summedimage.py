import uuid
import pytest

from roman_snpit_db.db import SummedImage, DBCon

from basetest import BaseTestDB


class TestSummedImage( BaseTestDB ):

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


    @pytest.fixture
    def basetest_setup( self, stupid_provenances ):
        self.cls = SummedImage
        self.safe_to_modify = [ 'collection', 'subset', 'filter',
                                'ra', 'dec', 'ra_corner_00', 'ra_corner_01', 'ra_corner_10', 'ra_corner_11',
                                'dec_corner_00', 'dec_corner_01', 'dec_corner_10', 'dec_corner_11',
                                'filepath', 'extension', 'width', 'height', 'format', 'mjd_start',
                                'mjd_end', 'properties' ]
        self.columns = set( self.safe_to_modify )
        self.columns.update( [ 'id', 'provenance_id' ] )
        self.uniques = []
        self.obj1 = SummedImage( id=uuid.uuid4(),
                                 provenance_id='blah1',
                                 collection='coll1',
                                 subset='sub1',
                                 filter='a',
                                 ra=1.,
                                 dec=1.,
                                 ra_corner_00=1.,
                                 ra_corner_01=1.,
                                 ra_corner_10=1.,
                                 ra_corner_11=1.,
                                 dec_corner_00=1.,
                                 dec_corner_01=1.,
                                 dec_corner_10=1.,
                                 dec_corner_11=1.,
                                 filepath='l2image1',
                                 width=1024,
                                 height=1024,
                                 format=1,
                                 mjd_start=60000.,
                                 mjd_end=60010. )
        self.dict1 = { k: getattr( self.obj1, k ) for k in self.columns }
        self.obj2 = SummedImage( id=uuid.uuid4(),
                                 provenance_id='blah1',
                                 collection='coll2',
                                 subset='sub2',
                                 filter='b',
                                 ra=2.,
                                 dec=2.,
                                 ra_corner_00=2.,
                                 ra_corner_01=2.,
                                 ra_corner_10=2.,
                                 ra_corner_11=2.,
                                 dec_corner_00=2.,
                                 dec_corner_01=2.,
                                 dec_corner_10=2.,
                                 dec_corner_11=2.,
                                 filepath='l2image2',
                                 width=1025,
                                 height=1025,
                                 format=2,
                                 mjd_start=60001.,
                                 mjd_end=60011. )
        self.dict2 = { k: getattr( self.obj2, k ) for k in self.columns }
        self.dict3 = { 'id': uuid.uuid4(),
                       'provenance_id': 'blah1',
                       'collection': 'coll3',
                       'subset': 'sub3',
                       'filter': 'c',
                       'ra': 3.,
                       'dec': 3.,
                       'ra_corner_00': 3.,
                       'ra_corner_01': 3.,
                       'ra_corner_10': 3.,
                       'ra_corner_11': 3.,
                       'dec_corner_00': 3.,
                       'dec_corner_01': 3.,
                       'dec_corner_10': 3.,
                       'dec_corner_11': 3.,
                       'filepath': 'l2image3',
                       'width': 1026,
                       'height': 1026,
                       'format': 3,
                       'mjd_start': 60002.,
                       'mjd_end': 60012. }
