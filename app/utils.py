from . import   db
from .models import  DatabaseDetail
import sqlalchemy
import pandas as pd




def db_conn1(serverid):
    fromserverdetails = db.session.query(DatabaseDetail).filter(DatabaseDetail.id == serverid).first()
    engine1 = sqlalchemy.create_engine(str(fromserverdetails.conn), convert_unicode=True)
    connection1 = engine1.connect()
    return connection1,engine1

def get_db_values(serverid):
    serverdetails = db.session.query(DatabaseDetail).filter(DatabaseDetail.id == serverid).first()
    return serverdetails

def get_select_query(connection,query,initial=0):
    df = pd.read_sql_query(str(query), connection)
    return df
