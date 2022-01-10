#SPDX-License-Identifier: MIT
from tests.test_workers.worker_persistance.util_persistance import *
#from augur.cli import add_repos
#from augur.cli import add_repo_groups


#Function to add repo_groups without starting an augur app instance
def set_up_repo_groups(database_connection):

    df = pd.read_sql(s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups"), database_connection)
    repo_group_IDs = df['repo_group_id'].values.tolist()

    insert_repo_group_sql = s.sql.text("""
    INSERT INTO "augur_data"."repo_groups"("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:repo_group_id, :repo_group_name, '', '', 0, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', '1.0', 'Git', CURRENT_TIMESTAMP);
    """)

    with open(filename) as create_repo_groups_file:
        data = csv.reader(create_repo_groups_file, delimiter=',')
        for row in data:
            logger.info(f"Inserting repo group with name {row[1]} and ID {row[0]}...")
            if int(row[0]) not in repo_group_IDs:
                repo_group_IDs.append(int(row[0]))
                database_connection.execute(insert_repo_group_sql, repo_group_id=int(row[0]), repo_group_name=row[1])
            else:
                logger.info(f"Repo group with ID {row[1]} for repo group {row[1]} already exists, skipping...")



    df = database_connection.execute(s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups"))

    repo_group_IDs = [group[0] for group in df.fetchall()]

    insertSQL = s.sql.text("""
        INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status,
        tool_source, tool_version, data_source, data_collection_date)
        VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
    """)

    with open("tests/test_facade/test_facade_contributor_interface/test_repos.csv") as upload_repos_file:
        data = csv.reader(upload_repos_file, delimiter=',')
        for row in data:
            logger.info(f"Inserting repo with Git URL `{row[1]}` into repo group {row[0]}")
            if int(row[0]) in repo_group_IDs:
                result = database_connection.execute(insertSQL, repo_group_id=int(row[0]), repo_git=row[1])
            else:
                logger.warning(f"Invalid repo group id specified for {row[1]}, skipping.")




def test_create_sha_endpoint_default(database_connection):
    set_up_repo_groups(database_connection)