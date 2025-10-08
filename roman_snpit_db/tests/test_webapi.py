from roman_snpit_db.db import DBCon


def test_create_get_provenance( dbclient ):
    try:
        provdata = { "id": "blah",
                     "environment": 0,
                     "env_major": 1,
                     "env_minor": 1,
                     "process": "test_process",
                     "major": 42,
                     "minor": 13,
                     "params": { "foo": "bar" }
                    }
        res = dbclient.send( "createprovenance", provdata )
        assert res[ "status" ] == "ok"

        newprov = dbclient.send( f"getprovenance/{provdata['id']}" )
        assert 'upstreams' in newprov
        for k, v in newprov.items():
            assert ( k == 'upstreams' ) or ( provdata[k] == v )

    finally:
        with DBCon() as con:
            con.execute( "DELETE FROM provenance WHERE id='blah'" )
            con.commit()
