#SPDX-License-Identifier: MIT
import pytest
import docker
import subprocess
from workers.worker_peristance import *
from tests.test_workers.test_data import *


def poll_database_connection(database_string):
    print("Attempting to create db engine")
    
    db = s.create_engine(database_string, poolclass=s.pool.NullPool,
      connect_args={'options': '-csearch_path={}'.format('augur_data')})
    
    return db
    


@pytest.fixture
def set_up_database():
    #Create client to docker daemon
    client = docker.from_env()
    
    print("Building a container")
    #Build the test database from the dockerfile and download
    #Postgres docker image if it doesn't exist.
    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    image = client.images.build(path=f"{ROOT_AUGUR_DIR}/util/docker/database/", pull=True)
    
    #Start a container and detatch
    #Wait until the database is ready to accept connections
    databaseContainer = client.containers.run(image, command=None, ports={'5432/tcp': 5432}, detatch=True)
    
    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            "augur", "augur", "172.17.0.1", 5432, "test"
    )
    
    #Get a database connection object from postgres to test connection and pass to test when ready
    db = poll_database_connection(DB_STR)
    
    attempts = 0
    
    while attempts < 15:
        result = subprocess.Popen(f"psql -d {DB_STR} -c \"select now()\"")
        text = result.communicate()[0]
        connectionStatus = result.returncode
        print(connectionStatus)
        if connectionStatus == 0:
            break
        
        attempts += 1
        
    #Setup complete, return the database object
    yield db
    
    #Cleanup the docker container by killing it.
    databaseContainer.kill()
    

@py



def test_enrich_data_primary_keys():
    pass