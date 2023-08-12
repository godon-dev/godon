
import psycopg2

class archive_db():

    def __execute(db_info=None, statement=""):
        """ Function wrapping the curoser execute with
            a dedicated connection for the execution."""

        db_connection = None
        try:
            with psycopg2.connect(**db_info) as db_connection:
                # Create table
                with db_connection.cursor() as db_cursor:
                    db_cursor.execute(statement)

        except OperationalError as Error:
            print(f"Error connecting to the database : {Error}")

        finally:
            if db_connection:
                db_connection.close()
                print("Closed connection.")

class queries():

    def create_breeder_table(table_name=None):
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        (
        setting_id bpchar NOT NULL,
        setting_full jsonb NOT NULL,
        setting_result FLOAT NOT NULL,
        PRIMARY KEY (setting_id HASH)
        );
        """

        return query

    def create_trigger(trigger_name=None, table_name=None, function_name=None):
        query = f"""
        CREATE TRIGGER {trigger_name}
        AFTER INSERT ON {table_name}
        FOR EACH ROW
        EXECUTE
        FUNCTION {function_name}
        );
        """

        return query
