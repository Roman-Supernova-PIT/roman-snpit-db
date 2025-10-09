CREATE TABLE authuser(
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  username text NOT NULL,
  displayname text NOT NULL,
  email text NOT NULL,
  pubkey text,
  privkey jsonb
);
COMMENT ON TABLE authuser IS 'Users';
COMMENT ON COLUMN authuser.pubkey IS 'RSA public key';
COMMENT ON COLUMN authuser.privkey IS 'RSA private key encrypted with user password';
ALTER TABLE authuser ADD CONSTRAINT pk_authuser PRIMARY KEY (id);
CREATE UNIQUE INDEX ix_authuser_username ON authuser USING btree (username);
CREATE INDEX ix_authuser_email ON authuser USING btree(email);

CREATE TABLE passwordlink(
  id UUID NOT NULL,
  userid UUID NOT NULL,
  expires timestamp with time zone
);
ALTER TABLE passwordlink ADD CONSTRAINT pk_passwordlink PRIMARY KEY (id);
CREATE INDEX ix_passwordlink_userid ON passwordlink USING btree (userid);


CREATE TABLE provenance(
    id UUID PRIMARY KEY,
    environment int DEFAULT NULL,
    env_major int DEFAULT NULL,
    env_minor int DEFAULT NULL,
    process text NOT NULL,
    major int NOT NULL,
    minor int NOT NULL,
    params JSONB );
COMMENT ON TABLE provenance IS 'Data product provenance';
COMMENT ON COLUMN provenance.environment IS 'Environment; see snpit_utils.provenance.Provenance.environments';
COMMENT ON COLUMN provenance.env_major IS 'Semantic major version of environment for this provenance';
COMMENT ON COLUMN provenance.env_minor IS 'Semantic minor version of environment for this provenance';
COMMENT ON COLUMN provenance.id IS 'Unique hash of the provenance';
COMMENT ON COLUMN provenance.process IS 'Name of the process or code associated with this provenace';
COMMENT ON COLUMN provenance.major IS 'Semantic major version of code for this provenance';
COMMENT ON COLUMN provenance.minor IS 'Semantic minor version of code for this provenance';
COMMENT ON COLUMN provenance.params IS 'Parameters that define the process behavior for this provenance';

CREATE TABLE provenance_upstream(
    downstream_id UUID NOT NULL,
    upstream_id UUID NOT NULL,

    PRIMARY KEY (downstream_id,upstream_id)
);
COMMENT ON TABLE provenance_upstream IS 'Upstream linkage table for provenance';
CREATE INDEX ix_prov_upstr_down ON provenance_upstream(downstream_id);
CREATE INDEX ix_prov_upstr_up ON provenance_upstream(upstream_id);
ALTER TABLE provenance_upstream ADD CONSTRAINT fk_prov_upstr_down
  FOREIGN KEY(downstream_id) REFERENCES provenance(id) ON DELETE CASCADE;
ALTER TABLE provenance_upstream ADD CONSTRAINT fk_prov_upstr_up
  FOREIGN KEY(upstream_id) REFERENCES provenance(id) ON DELETE RESTRICT;


-- OK, ok, we're violating database normalization
--   here by having process, which is also in
--   the linked provenance_id.  It's here so
--   we can have a database-ensured unique
--   (tag, process).
CREATE TABLE provenance_tag(
    tag TEXT NOT NULL,
    process TEXT NOT NULL,
    provenance_id UUID NOT NULL
);
ALTER TABLE provenance_tag ADD PRIMARY KEY (tag, process);
ALTER TABLE provenance_tag ADD CONSTRAINT fk_provenance_tag_prov
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
COMMENT ON TABLE provenance_tag IS 'Human readable tags for collections of provenances';
COMMENT ON COLUMN provenance_tag.tag IS 'Human-readable tag';
COMMENT ON COLUMN provenance_tag.process IS 'process of the provenance; must match corresponding provenance process';
COMMENT ON COLUMN provenance_tag.provenance_id IS 'id of the provenance';

CREATE TABLE diaobject(
    id UUID PRIMARY KEY,
    provenance_id UUID NOT NULL,
    name text,
    collection text NOT NULL,
    subset text,
    ra double precision,
    dec double precision,
    tdiscovery double precision,
    tmax double precision,
    tstart double precision,
    tend double precision,
    properties JSONB
);
CREATE INDEX ix_diaobject_q3c ON diaobject (q3c_ang2ipix(ra,dec));
CREATE INDEX ix_diaobject_name ON diaobject(name);
CREATE INDEX ix_diaobject_collection ON diaobject(collection);
ALTER TABLE diaobject ADD CONSTRAINT fk_diaobject_prov
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
CREATE INDEX ix_diaobject_provenance_id ON diaobject(provenance_id);
COMMENT ON TABLE diaobject IS 'Known transients or simulated transients';
COMMENT ON COLUMN diaobject.name IS 'Name or id of the transient within its collection';
COMMENT ON COLUMN diaobject.collection IS 'Collection of transients this is part of';
COMMENT ON COLUMN diaobject.ra IS 'Approx (±1"ish) RA of object; ICRS decimal degrees';
COMMENT ON COLUMN diaobject.dec IS 'Approx (±1"ish) Dec of object; ICRS decimal degrees';
COMMENT ON COLUMN diaobject.tdiscovery IS 'MJD of image where the transient was discovered';
COMMENT ON COLUMN diaobject.tmax IS 'Approx. MJD where transient is at peak flux';
COMMENT ON COLUMN diaobject.tstart IS 'Approx. MJD where the transient lightcurve "starts"';
COMMENT ON COLUMN diaobject.tend IS 'Approx. MJD where the transient lightcurve "ends"';
COMMENT ON COLUMN diaobject.properties IS 'Collection-specific additional properties of the transient';


CREATE TABLE diaobject_position(
    id UUID PRIMARY KEY,
    diaobject_id UUID NOT NULL,
    provenance_id UUID NOT NULL,
    ra double precision,
    ra_err double precision,
    dec double precision,
    dec_err double precision,
    ra_dec_covar double precision,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE diaobject_position ADD CONSTRAINT fk_objpos_diaobject
  FOREIGN KEY(diaobject_id) REFERENCES diaobject(id) ON DELETE CASCADE;
CREATE INDEX ix_objpos_diaobject ON diaobject_position(diaobject_id);
ALTER TABLE diaobject_position ADD CONSTRAINT fk_objpos_provenance
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
CREATE INDEX ix_diaobject_prov ON diaobject_position(provenance_id);
COMMENT ON TABLE diaobject_position IS 'Calculated positions for a diaobject';
COMMENT ON COLUMN diaobject_position.ra IS 'RA in ICRS decimal degrees';
COMMENT ON COLUMN diaobject_position.dec IS 'Dec in ICRS decimal degrees';
COMMENT ON COLUMN diaobject_position.ra_err IS 'Uncertainty on RA';
COMMENT ON COLUMN diaobject_position.dec_err IS 'Uncertainty on Dec';
COMMENT ON COLUMN diaobject_position.ra_dec_covar IS 'Covariance between RA and Dec';
COMMENT ON COLUMN diaobject_position.calculated_at IS 'Time when this position was calculculated';


CREATE TABLE diaobject_classification(
  id UUID PRIMARY KEY,
  diaobject_id UUID NOT NULL,
  provenance_id UUID NOT NULL,
  class_id int,
  probability real
);
CREATE UNIQUE INDEX ix_objclass_spec ON diaobject_classification(diaobject_id,provenance_id,class_id);
CREATE INDEX ix_objclass_classid ON diaobject_classification(class_id);
ALTER TABLE diaobject_classification ADD CONSTRAINT fk_objclass_diaobject
  FOREIGN KEY(diaobject_id) REFERENCES diaobject(id) ON DELETE CASCADE;
CREATE INDEX ix_objclass_diaobject ON diaobject_classification(diaobject_id);
ALTER TABLE diaobject_classification ADD CONSTRAINT fk_objclass_provenance
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE CASCADE;
CREATE INDEX ix_objclass_provenance ON diaobject_classification(provenance_id);
COMMENT ON TABLE diaobject_classification IS 'diaobject classification types and probabilities';


CREATE TABLE l2image(
    id UUID PRIMARY KEY,
    provenance_id UUID NOT NULL,
    collection text NOT NULL,
    subset text,
    pointing int,
    sca int,
    filter text NOT NULL,
    ra double precision NOT NULL,
    dec double precision NOT NULL,
    ra_corner_00 real NOT NULL,
    ra_corner_01 real NOT NULL,
    ra_corner_10 real NOT NULL,
    ra_corner_11 real NOT NULL,
    dec_corner_00 real NOT NULL,
    dec_corner_01 real NOT NULL,
    dec_corner_10 real NOT NULL,
    dec_corner_11 real NOT NULL,
    filepath text NOT NULL,
    extension text[],
    width smallint,
    height smallint,
    format smallint NOT NULL,
    mjd_start double precision NOT NULL,
    exptime real NOT NULL,
    properties JSONB
);
CREATE INDEX ix_l2image_collection ON l2image(collection);
CREATE INDEX ix_l2image_pointing ON l2image(pointing);
CREATE INDEX ix_l2image_sca ON l2image(sca);
CREATE INDEX ix_l2image_filter ON l2image(filter);
CREATE UNIQUE INDEX ix_l2image_spec ON l2image(provenance_id,collection,pointing,sca,filter);
CREATE INDEX ix_l2image_q3c ON l2image (q3c_ang2ipix(ra,dec));
CREATE INDEX ix_l2image_ra00 ON l2image (ra_corner_00);
CREATE INDEX ix_l2image_ra01 ON l2image (ra_corner_01);
CREATE INDEX ix_l2image_ra10 ON l2image (ra_corner_10);
CREATE INDEX ix_l2image_ra11 ON l2image (ra_corner_11);
CREATE INDEX ix_l2image_dec00 ON l2image (dec_corner_00);
CREATE INDEX ix_l2image_dec01 ON l2image (dec_corner_01);
CREATE INDEX ix_l2image_dec10 ON l2image (dec_corner_10);
CREATE INDEX ix_l2image_dec11 ON l2image (dec_corner_11);
CREATE UNIQUE INDEX ix_l2image_filepath ON l2image(filepath);
CREATE INDEX lx_l2image_mjd ON l2image(mjd_start);
ALTER TABLE l2image ADD CONSTRAINT fk_l2image_prov
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
CREATE INDEX ix_l2image_provenance_id ON l2image(provenance_id);
COMMENT ON TABLE l2image IS 'L2 image';
COMMENT ON COLUMN l2image.collection IS 'Collection this image is part of';
COMMENT ON COLUMN l2image.pointing IS 'Pointing of the exposure this image is from';
COMMENT ON COLUMN l2image.sca IS 'SCA of this image';
COMMENT ON COLUMN l2image.ra_corner_00 IS 'RA of pixel (0,0)';
COMMENT ON COLUMN l2image.ra_corner_01 IS 'RA of pixel (0,height-1)';
COMMENT ON COLUMN l2image.ra_corner_10 IS 'RA of pixel (width-1,0)';
COMMENT ON COLUMN l2image.ra_corner_11 IS 'RA of pixel (width-1,height-1)';
COMMENT ON COLUMN l2image.dec_corner_00 IS 'Dec of pixel (0,0)';
COMMENT ON COLUMN l2image.dec_corner_01 IS 'Dec of pixel (0,height-1)';
COMMENT ON COLUMN l2image.dec_corner_10 IS 'Dec of pixel (width-1,0)';
COMMENT ON COLUMN l2image.dec_corner_11 IS 'Dec of pixel (width-1,height-1)';


CREATE TABLE summed_image(
    id UUID PRIMARY KEY,
    provenance_id UUID NOT NULL,
    collection text NOT NULL,
    subset text NOT NULL,
    filter text NOT NULL,
    ra double precision NOT NULL,
    dec double precision NOT NULL,
    ra_corner_00 real NOT NULL,
    ra_corner_01 real NOT NULL,
    ra_corner_10 real NOT NULL,
    ra_corner_11 real NOT NULL,
    dec_corner_00 real NOT NULL,
    dec_corner_01 real NOT NULL,
    dec_corner_10 real NOT NULL,
    dec_corner_11 real NOT NULL,
    filepath text NOT NULL,
    extension text[],
    width smallint,
    height smallint,
    format smallint NOT NULL,
    mjd_start double precision NOT NULL,
    mjd_end double precision NOT NULL,
    properties JSONB
);
CREATE INDEX ix_sumim_collection ON summed_image(collection);
CREATE INDEX ix_sumim_filter ON summed_image(filter);
CREATE INDEX ix_sumim_q3c ON summed_image(q3c_ang2ipix(ra,dec));
CREATE INDEX ix_sumim_ra00 ON summed_image(ra_corner_00);
CREATE INDEX ix_sumim_ra01 ON summed_image(ra_corner_01);
CREATE INDEX ix_sumim_ra10 ON summed_image(ra_corner_10);
CREATE INDEX ix_sumim_ra11 ON summed_image(ra_corner_11);
CREATE INDEX ix_sumim_dec00 ON summed_image(dec_corner_00);
CREATE INDEX ix_sumim_dec01 ON summed_image(dec_corner_01);
CREATE INDEX ix_sumim_dec10 ON summed_image(dec_corner_10);
CREATE INDEX ix_sumim_dec11 ON summed_image(dec_corner_11);
CREATE UNIQUE INDEX ix_sumim_filepath ON summed_image (filepath);
CREATE INDEX lx_sumim_mjd_start ON summed_image(mjd_start);
CREATE INDEX lx_sumim_mjd_end ON summed_image(mjd_end);
ALTER TABLE summed_image ADD CONSTRAINT fk_sumim_prov
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
CREATE INDEX ix_sumim_prov ON summed_image(provenance_id);
COMMENT ON TABLE summed_image IS 'image that is a sum of L2 images';

CREATE TABLE summed_image_component(
    summed_image_id UUID NOT NULL,
    l2image_id UUID NOT NULL,

    PRIMARY KEY (summed_image_id, l2image_id)
);
ALTER TABLE summed_image_component ADD CONSTRAINT fk_sumcomp_sumim
  FOREIGN KEY(summed_image_id) REFERENCES summed_image(id) ON DELETE CASCADE;
CREATE INDEX ix_sumcomp_sumim ON summed_image_component(summed_image_id);
ALTER TABLE summed_image_component ADD CONSTRAINT fk_sumcomp_compim
  FOREIGN KEY(l2image_id) REFERENCES l2image(id) ON DELETE RESTRICT;
CREATE INDEX ix_sumpcom_compim ON summed_image_component(l2image_id);
COMMENT ON TABLE summed_image_component IS 'summed_image linkage table';


CREATE TABLE phrosty_lightcurve(
    id UUID PRIMARY KEY,
    provenance_id UUID NOT NULL,
    collection text NOT NULL,
    subset text,
    diaobject_id UUID NOT NULL,
    filter text NOT NULL,
    filepath text NOT NULL
);
CREATE INDEX phrosty_collection ON phrosty_lightcurve(collection);
CREATE INDEX phrosty_filter ON phrosty_lightcurve(filter);
CREATE INDEX phrosty_filepath ON phrosty_lightcurve(filepath);
CREATE UNIQUE INDEX phrosty_spec ON phrosty_lightcurve(provenance_id,diaobject_id,collection,subset);
ALTER TABLE phrosty_lightcurve ADD CONSTRAINT fk_phrosty_prov
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
CREATE INDEX ix_phrosty_prov ON phrosty_lightcurve(provenance_id);
ALTER TABLE phrosty_lightcurve ADD CONSTRAINT fk_phrosty_diaobject
  FOREIGN KEY(diaobject_id) REFERENCES diaobject(id) ON DELETE RESTRICT;
CREATE INDEX ix_phrosty_diaobject ON phrosty_lightcurve(diaobject_id);
COMMENT ON TABLE phrosty_lightcurve IS 'Lightcurves produced by phrosty';


CREATE TABLE campari_lightcurve(
    id UUID PRIMARY KEY,
    provenance_id UUID NOT NULL,
    collection text NOT NULL,
    subset text,
    diaobject_id UUID NOT NULL,
    filter text NOT NULL,
    filepath text NOT NULL
);
CREATE INDEX campari_collection ON campari_lightcurve(collection);
CREATE INDEX campari_filter ON campari_lightcurve(filter);
CREATE INDEX campari_filepath ON campari_lightcurve(filepath);
CREATE UNIQUE INDEX campari_spec ON campari_lightcurve(provenance_id,diaobject_id,collection,subset);
ALTER TABLE campari_lightcurve ADD CONSTRAINT fk_campari_prov
  FOREIGN KEY(provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT;
CREATE INDEX ix_campari_prov ON campari_lightcurve(provenance_id);
ALTER TABLE campari_lightcurve ADD CONSTRAINT fk_campari_diaobject
  FOREIGN KEY(diaobject_id) REFERENCES diaobject(id) ON DELETE RESTRICT;
CREATE INDEX ix_campari_diaobject ON campari_lightcurve(diaobject_id);
COMMENT ON TABLE campari_lightcurve IS 'Lightcurves produced by campari';
