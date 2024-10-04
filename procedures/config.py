from sqlalchemy.engine import URL
import sqlalchemy
conn_url = URL.create(
            drivername="postgresql",  # Change this to your specific database driver
            username="saleor",
            password="saleor",  # Password with special characters
            host="localhost",
            port=5432,  # Change this to your specific port
            database="credit"
            #"storedProcedure"
            #"postgres"
        )
engine = sqlalchemy.create_engine(conn_url)
# engine = engine.connect()
