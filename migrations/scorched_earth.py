# TODO : wrap this with --do and --really-do options

import roman_snpit_db.db
from snpit_utils.logger import SNLogger

with roman_snpit_db.db.DBCon() as con:
    try:
        for table in roman_snpit_db.db.all_table_names:
            SNLogger.warning( f"Dropping table {table}..." )
            # Yeah, yeah, there's sort of an SQL injection attack here,
            #   though if somebody can edit the code to modify the
            #   all_table_names variable, they could just as easily edit
            #   the code to put whatever SQL in here.  So, using an
            #   f-string on the SQL query below isn't really a worry.
            con.execute_nofetch( f"DROP TABLE IF EXISTS {table} CASCADE" )
        con.commit()
    except Exception:
        SNLogger.exception( "Exception scorching the earth." )
        SNLogger.error( "(Probably) not committing the changes." )
