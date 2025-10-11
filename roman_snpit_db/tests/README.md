To run tests, use the docker compose environment in the Roman-Supernoava-PIT/environment archive, `test-docker-environment` subdirectory.

To run the tests:

* make sure you've pulled the docker image for the SNPIT environment (cpu variant).  This means running one of:

    * `docker pull rknop/roman-snpit-env:cpu`
    * `docker pull registry.nersc.gov/m4385/rknop/roman-snpit-env:cpu`

  where on NERSC you'd replace `docker` with `podman-hpc`.

* cd into `environment/test-docker-environment`

* make sure you've either pulled or build the docker images associated with this package.  Pull with:

    * `DB_DOCKER_ARCHIVE=registry.nersc.gov/m4385/rknop docker compose pull`

   where you may need to substitute `rknop` in place of `registry.nersc.gov/m4385/rknop` if you can't get access to the NERSC container registry.  TODO: document doing this on NERSC with `podman-hpc`.

   However, if you've made any changes, you almost certainly need to build new images.  Accomplis that with:

    * `docker compose build`

   In this case, if you're going to be pushing this up for a PR, you're also going to need to push the new test docker iamges to github.  TODO ROB DOCUMENT THIS PROCEDURE; it's _not_ just `docker push`, you have to edit the docker-compose.yaml file in the environment, which is actually a little bit of a nightmare, and thought needs to be applied to make that better.

* Run the container:

    * `docker compose up -d webserver shell`

  **Note**: If you pulled, rather than built, the docker images, you need to add `DB_DOCKER_ARCHIVE=registry.nersc.gov/m4385/rknop` (or whatever you used when pulling) before `docker compose`

* Assuming everything started up right, get a shell on the container:

    * `docker compose exec -it shell /bin/bash`

  where, again, if you pullsed rather than build the images, you need to add `DB_DOCKER_ARCHIVE=registry.nersc.gov/m4385/rknop` (or whatever you used when pulling) before `docker compose`.

* Inside the container, get your latest and greatest `roman-snpit-db` installed:

    * `cd /home/roman-snpit-db`
    * `pip install -e .[test]`

  (If you're doing complicated things, like Rob is doing all the time when developing this, it's possible you'll also need to do a `pip install -e .[test]` in `/home/snpit_utils`.)

* Run the tests:
   
    * `cd /home/roman-snpit-db/roman_snpit_db/tests`
    * `SNPIT_CONFIG=test_config.yaml pytest -v`

* Do whatever you need to do to make yourself happy

* Exit and shut down the container; just type `exit` in the container, and then outside of the container run:

    * `docker compose down -v`
