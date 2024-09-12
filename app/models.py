from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, Enum,Text,JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who

"""

class DatabaseDetail(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    dbname = Column(String(100), nullable=False)
    user = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    dialect = Column(Enum("mysql", "mssql+pymssql", "postgresql"))
    status = Column(String(20), default="Yet to start")  # Status: pending, in_progress, completed

    @hybrid_property
    def conn(self) -> str:
        conn = self.dialect + '://' + self.user + ':' + self.password + '@' + self.host + ':' + str(self.port) + '/' + self.dbname
        return str(conn)

    @hybrid_property
    def auditconn(self) -> str:
        auditconn = self.dialect + '://' + self.user + ':' + '****' + '@' + self.host + ':' + str(self.port) + '/' + self.dbname
        return str(auditconn)

    def __repr__(self):
        return self.dbname

class ProcedureConversion(Model):
    id = Column(Integer, primary_key=True)
    procedure_name = Column(String(100), nullable=False)
    python_file = Column(String(200), nullable=False)
    testcase_file = Column(String(200), nullable=False)
    python_code = Column(Text, nullable=False)
    testcase_code = Column(Text, nullable=False)
    # database_id = Column(Integer, nullable=False)  # Foreign Key to DatabaseDetail.id
    database_id = Column(Integer, ForeignKey('database_detail.id'))
    database = relationship("DatabaseDetail")

    def __repr__(self):
        return self.database_id


class GitRepository(Model):
    id = Column(Integer, primary_key=True)
    repo_path = Column(String(255), nullable=False)
    branch_name = Column(String(100), nullable=False)
    username = Column(String(150), nullable=False)
    token = Column(Text, nullable=False)  # Use Text for longer strings
    repo_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    database_id = Column(Integer, ForeignKey('database_detail.id'))
    database = relationship("DatabaseDetail")
    def __repr__(self):
        return f"<GitRepository {self.repo_name} - {self.branch_name}>"

class Audit(Model):
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=True)
    stage = Column(Text, nullable=True)
    database_id = Column(Integer, ForeignKey('database_detail.id'))
    database = relationship("DatabaseDetail")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    def __repr__(self):
        return self.message