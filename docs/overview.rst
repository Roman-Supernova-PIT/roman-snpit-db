.. highlight:: shell

.. contents::
               
.. _overview:
               
========
Overview
========

The Roman SNPIT Database is intended as a database that the PIT will use internally to keep track of data products during the operation of its production pipeline(s).  It is not intended to be public-facing.

Parts of the pipeline will produce outputs that will then be the inputs of another part of the pipeline.  For example, the ``sidecar`` discovery software will produce locations of objects, which then need to be consumed by the ``phrosty`` and ``campari`` lightcurve software in order to know what to build lightcurves of.  The lightcurves produced by that lightcurve software will need to go into whatever supernova fitting software we are using to produce (e.g.) SALT3 parameters.  The output of the fitting software will need to go to the cosmology software, etc.

The purpose of this database is to track all of that.  Each part of the pipeline will use the database to find out what is aviailable from previous parts of the pipeline, and will report to the database what it has produce to be used by later parts of the pipeline.


Usage
=====

At the moment, it's not clear exactly how the database will be used.  It may be that we will all connect to the Postgres backend datbase directly using (for instance) Python's ``psycopg``.  However, it's more likley that there will be a web API front end that provides all the functionality we need.  There are benefits and drawbacks to both methods of operation.  For people who know SQL, it can be frustrating not to just be able to query the database.  However, by putting everything behind a web API, the web server can take care of things like making sure :ref:`provenances <overview-provenance>` are used correctly, and also allow us to work with a database server that cannot be contacted directly from everywhere we might be running in production (which may turn out to be an operational necessity).


.. _overview-provenance:

Provenance
==========

The purpose of the Provenance system is primarily to allow for multiple versions of the same object to live together harmoniously in the database.  Secondarily, it tracks which version of which software was used to create a data product tracked by the database.  This will allow us to track the data products use to build multiple different data releases without having to use a different database for each one.  It will also allow us to have multiple versions of things, e.g. multiple codes that provide transient lightcurve or spectrum classification probabilities.

Provenances are tabulated in the ``provenance`` database table.  Each provenance is defined by a process, a version, parameters, and upstream provenances.  ``process`` is the column that tracks what code is associated with this provenance.  For example for L2 Images which are imported directly from wherever they are kept by the Roman SOC, the process might be "import_l2", or similar.  For lightcurves produced by the phrosty difference imaging forced photometry software, the process might be "phrosty".  ``major`` and ``minor`` are the columns tracking the version of the process.  This presumes `semantic versioning <https://semver.org/>`_, where every code has three period-separated version numbers, a major, a minor, and a patch.  Semantic versioning assumes that any API-breaking changes require an increment of the major version.  Additions to the API or significant bug fixes require an increment of the minor version.  Changes to documentation, or anything else that doesn't change the behvaior of the package (so that the same inputs will yield the same outputs) can just have an increment of the patch version.  A provenance is only defined by the major and minor versions of the software, as the results of the code should never depend on the patch version number.  (Ideally, they don't depend on the minor version number either, but we're hedging our bets.)

The ``params`` column is a JSONB column that tracks parameters of the process.  These can be anything, but is most obviously a dictionary of configuration values.  However, ideally, they should be everything necessary to be able to reproduce the outputs of a process.  For example, for lightcurve-building software, the ``params`` should include all configuration options that define how the software behaves.  However, it sould *not* include things specific to the object or image it's working on.  It also should not include anything specific to the system it's running on (such as base directories for finding files.)  That way, the same version of the same software run with the same configuration on a large number of objects will all be associated with the same provenance.

Upstream provenances are tracked by the ``provenance_upstream`` table.  If the output of a given process depends on the functioning of one or more previous processes, they should be included as the upstream of the current process.  For example, a provenance for software that recenters the position of a supernova by weighting positions measured by lightcurve extraction software should have a provenance from the lightcurve extraction software as its upstream.

The ``id`` of a provenance is constructed from a hash of all of its other parameters (including the ids of any upstream provenances).  Because it's a hash, that means that two provenances that are functionally the same will always have the same ``id``.  It also means you can determine what the ``id`` of a given provenance is without querying the database.

Provenances can be built using TODO SEE IN USAGE

Many (all?) database tables have a ``provenance_id`` field.  This specifies the software, version of software, and parmaeters that was used to create this database product.  If there is potentially more than one code that could generate a data product (e.g. a supernova classification), it is that data product's provenance that tells you exactly which code was used to produce it.

Provenance and inserting into the database
------------------------------------------

Do it right.


Provenance and searching tables
-------------------------------

Anybody searching database tables needs to be aware of how the provenance system works.  Naively constructing queries just looking at the schema are likely to get you the wrong thing.  For example, if you tried to find the lightcurve for a given object, you might get back a whole bunch of lightcurves, as each was stored with a different provenance.  You need to know the provenance of what you are searching for.

TODO how to figure out the "current" provenance for a given code.


Database Schema
===============

..
    Tables of database schema generated with migrations/schema_to_rst.py

Provenance
----------

**Table:** ``provenance``

Data product provenance

=========== =========== ===== ======== ===============================================================
Column      Type        null? Default  Comment                                                        
=========== =========== ===== ======== ===============================================================
``id``      ``text``    NO    ``None`` Unique hash of the provenance                                  
``process`` ``text``    NO    ``None`` Name of the process or code associated with this provenace     
``major``   ``integer`` NO    ``None`` Semantic major version of code for this provenance             
``minor``   ``integer`` NO    ``None`` Semantic minor version of code for this provenance             
``params``  ``jsonb``   YES   ``None`` Parameters that define the process behavior for this provenance
=========== =========== ===== ======== ===============================================================

**Table:** ``provenance_upstream``

Upstream linkage table for provenance

================= ======== ===== ======== =======
Column            Type     null? Default  Comment
================= ======== ===== ======== =======
``downstream_id`` ``text`` NO    ``None`` None   
``upstream_id``   ``text`` NO    ``None`` None   
================= ======== ===== ======== =======


DiaObject
---------

A DiaObject represents a single supernova (or other transient).  Diaobjects come in "collections" (and, optionally "subsets").  Collectoins are a way of trakcing DiaObjects that come from wildly different sources.  Although this is somewhat redudant with provenance, collections exist as a way of quickly filtering out the set of objects you're interseted in.  For example, the "ou2024" collection holds the transients injected into the OpenUnviverse 2024 simulations.  We may have a collection "rapid_alerts" for transients we learned about from rapid alerts, and another one "sidecar" for transients discovered with our own sidecar subtraction and search software.

**Table:** ``diaobject``

Known transients or simulated transients

============== ==================== ===== ======== ==========================================================
Column         Type                 null? Default  Comment                                                   
============== ==================== ===== ======== ==========================================================
``name``       ``text``             YES   ``None`` Name or id of the transient within its collection         
``collection`` ``text``             NO    ``None`` Collection of transients this is part of                  
``ra``         ``double precision`` YES   ``None`` Approx (±1"ish) RA of object; ICRS decimal degrees        
``dec``        ``double precision`` YES   ``None`` Approx (±1"ish) Dec of object; ICRS decimal degrees       
``tdiscovery`` ``double precision`` YES   ``None`` MJD of image where the transient was discovered           
``tmax``       ``double precision`` YES   ``None`` Approx. MJD where transient is at peak flux               
``tstart``     ``double precision`` YES   ``None`` Approx. MJD where the transient lightcurve "starts"       
``tend``       ``double precision`` YES   ``None`` Approx. MJD where the transient lightcurve "ends"         
``properties`` ``jsonb``            YES   ``None`` Collection-specific additional properties of the transient
============== ==================== ===== ======== ==========================================================


DiaObjectPosition
------------------

The `diaobject` table has an ra and dec.  Those values should be considered approximate, as they represent the position the object was originally found at.  When we are building lightcurves, we will be able to determine more accurate (and more precise) positions by looking at the object on all of the images where it was detected.  Rather than try to update the `diaobject` table (which would then raise complicated issues of tracking provenance), better-measured positions are stored in a separate table.  Software that wants the "best" position for an object should link to this table, and filter on the provenance they want to use.

TODO discuss provenance and diaobject may not be unique, calculated field.

**Table:** ``diaobject_position``

Calculated positions for a diaobject

================= ============================ ===== ========= =========================================
Column            Type                         null? Default   Comment                                  
================= ============================ ===== ========= =========================================
``ra``            ``double precision``         YES   ``None``  RA in ICRS decimal degrees               
``ra_err``        ``double precision``         YES   ``None``  Uncertainty on RA                        
``dec``           ``double precision``         YES   ``None``  Dec in ICRS decimal degrees              
``dec_err``       ``double precision``         YES   ``None``  Uncertainty on Dec                       
``ra_dec_covar``  ``double precision``         YES   ``None``  Covariance between RA and Dec            
``calculated_at`` ``timestamp with time zone`` YES   ``now()`` Time when this position was calculculated
================= ============================ ===== ========= =========================================



DiaObjectClassification
-----------------------

**Table:** ``diaobject_classification``

diaobject classification types and probabilities

================= =========== ===== ======== =======
Column            Type        null? Default  Comment
================= =========== ===== ======== =======
``id``            ``uuid``    NO    ``None`` None   
``diaobject_id``  ``uuid``    NO    ``None`` None   
``provenance_id`` ``text``    NO    ``None`` None   
``class_id``      ``integer`` YES   ``None`` None   
``probability``   ``real``    YES   ``None`` None   
================= =========== ===== ======== =======




L2Image
-------

This table represents an L2 image from the Roman SOC that we (somehow) know about.  An L2 image for a given provenance is uniquely defined by its ``pointing`` and ``sca``.  The ``pointing`` is the specific exposure of the telescope.  (TODO: figure out what Roman will really call these and the format in which we're going to get this information.)  The ``sca`` for this image.  Assuming we have all the data, for a given provenance and collection, there will be 18 ``l2image`` rows for each ``pointing`` (one for each of the 18 SCAs).

**Table:** ``l2image``

L2 image

================= ==================== ===== ======== ===========================================
Column            Type                 null? Default  Comment                                    
================= ==================== ===== ======== ===========================================
``id``            ``uuid``             NO    ``None`` None                                       
``provenance_id`` ``text``             NO    ``None`` None                                       
``collection``    ``text``             NO    ``None`` Collection this image is part of           
``subset``        ``text``             YES   ``None`` None                                       
``pointing``      ``integer``          YES   ``None`` Pointing of the exposure this image is from
``sca``           ``integer``          YES   ``None`` SCA of this image                          
``filter``        ``text``             NO    ``None`` None                                       
``ra``            ``double precision`` NO    ``None`` None                                       
``dec``           ``double precision`` NO    ``None`` None                                       
``ra_corner_00``  ``real``             NO    ``None`` RA of pixel (0,0)                          
``ra_corner_01``  ``real``             NO    ``None`` RA of pixel (0,height-1)                   
``ra_corner_10``  ``real``             NO    ``None`` RA of pixel (width-1,0)                    
``ra_corner_11``  ``real``             NO    ``None`` RA of pixel (width-1,height-1)             
``dec_corner_00`` ``real``             NO    ``None`` Dec of pixel (0,0)                         
``dec_corner_01`` ``real``             NO    ``None`` Dec of pixel (0,height-1)                  
``dec_corner_10`` ``real``             NO    ``None`` Dec of pixel (width-1,0)                   
``dec_corner_11`` ``real``             NO    ``None`` Dec of pixel (width-1,height-1)            
``filepath``      ``text``             NO    ``None`` None                                       
``extention``     ``ARRAY``            YES   ``None`` None                                       
``width``         ``smallint``         YES   ``None`` None                                       
``height``        ``smallint``         YES   ``None`` None                                       
``format``        ``smallint``         NO    ``None`` None                                       
``mjd_start``     ``double precision`` NO    ``None`` None                                       
``exptime``       ``real``             NO    ``None`` None                                       
``properties``    ``jsonb``            YES   ``None`` None                                       
================= ==================== ===== ======== ===========================================


SummedImage
-----------

If we build our own deep references, or summed images for other purposes, they are tracked here.  The current design of the table assumes that we'll only ever be summing L2 images to make summed images.
**Table:** ``summed_image``

image that is a sum of L2 images

================= ==================== ===== ======== =======
Column            Type                 null? Default  Comment
================= ==================== ===== ======== =======
``id``            ``uuid``             NO    ``None`` None   
``provenance_id`` ``text``             NO    ``None`` None   
``collection``    ``text``             NO    ``None`` None   
``subset``        ``text``             NO    ``None`` None   
``filter``        ``text``             NO    ``None`` None   
``ra``            ``double precision`` NO    ``None`` None   
``dec``           ``double precision`` NO    ``None`` None   
``ra_corner_00``  ``real``             NO    ``None`` None   
``ra_corner_01``  ``real``             NO    ``None`` None   
``ra_corner_10``  ``real``             NO    ``None`` None   
``ra_corner_11``  ``real``             NO    ``None`` None   
``dec_corner_00`` ``real``             NO    ``None`` None   
``dec_corner_01`` ``real``             NO    ``None`` None   
``dec_corner_10`` ``real``             NO    ``None`` None   
``dec_corner_11`` ``real``             NO    ``None`` None   
``filepath``      ``text``             NO    ``None`` None   
``extention``     ``ARRAY``            YES   ``None`` None   
``width``         ``smallint``         YES   ``None`` None   
``height``        ``smallint``         YES   ``None`` None   
``format``        ``smallint``         NO    ``None`` None   
``mjd_start``     ``double precision`` NO    ``None`` None   
``mjd_end``       ``double precision`` NO    ``None`` None   
``properties``    ``jsonb``            YES   ``None`` None   
================= ==================== ===== ======== =======


**Table:** ``summed_image_component``

summed_image linkage table

=================== ======== ===== ======== =======
Column              Type     null? Default  Comment
=================== ======== ===== ======== =======
``summed_image_id`` ``uuid`` NO    ``None`` None   
``l2image_id``      ``uuid`` NO    ``None`` None   
=================== ======== ===== ======== =======


PhrostyLightcurve
-----------------

This table tracks output of the phrosty difference-imaging forced photometry software.  Each lightcurve will have a file associated with it holding all of the output information from phrosty.  (TODO: determine and document that format.)  This table allows you to find those files.

**Table:** ``phrosty_lightcurve``

Lightcurves produced by phrosty

================= ======== ===== ======== =======
Column            Type     null? Default  Comment
================= ======== ===== ======== =======
``id``            ``uuid`` NO    ``None`` None   
``provenance_id`` ``text`` NO    ``None`` None   
``collection``    ``text`` NO    ``None`` None   
``subset``        ``text`` YES   ``None`` None   
``diaobject_id``  ``uuid`` NO    ``None`` None   
``filter``        ``text`` NO    ``None`` None   
``filepath``      ``text`` NO    ``None`` None   
================= ======== ===== ======== =======


CampariLightcurve
-----------------

This table tracks output of the campari scene-modelling software, and works similarly to the ``phrosty_lightcurve`` table.


**Table:** ``campari_lightcurve``

Lightcurves produced by campari

================= ======== ===== ======== =======
Column            Type     null? Default  Comment
================= ======== ===== ======== =======
``id``            ``uuid`` NO    ``None`` None   
``provenance_id`` ``text`` NO    ``None`` None   
``collection``    ``text`` NO    ``None`` None   
``subset``        ``text`` YES   ``None`` None   
``diaobject_id``  ``uuid`` NO    ``None`` None   
``filter``        ``text`` NO    ``None`` None   
``filepath``      ``text`` NO    ``None`` None   
================= ======== ===== ======== =======
