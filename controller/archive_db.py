
import psycopg2
import logging
import os

ARCHIVE_DB_CONFIG = dict(user="yugabyte",
                         password="yugabyte",
                         host="yb-tservers.godon.svc.cluster.local", # not ideal, as namespace might change on k8s side
                         port=os.environ.get('YB_TSERVER_SERVICE_SERVICE_PORT_TCP_YSQL_PORT'))

class archive_db():

    @staticmethod
    def execute(db_info=None, query="", with_result=False):
        """ Function wrapping the curoser execute with
            a dedicated connection for the execution."""

        db_connection = None
        try:
            with psycopg2.connect(**db_info) as db_connection:
                # Create table
                with db_connection.cursor() as db_cursor:
                    db_cursor.execute(query)

                    if with_result:
                        result =  db_cursor.fetchall()
                        return result

        except psycopg2.OperationalError as Error:
            logging.error(f"Error connecting to the database : {Error}")
            logging.error(f"Database Info: {db_info}")

        finally:
            if db_connection:
                db_connection.close()
                print("Closed connection.")

class queries():

    @staticmethod
    def create_database(breeder_id=None):
        query = f"""
        CREATE DATABASE {breeder_id}
        """
        return query

