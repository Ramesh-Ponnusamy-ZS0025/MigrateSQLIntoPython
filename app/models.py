from email.policy import default

from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from sqlalchemy.engine import URL
from flask_appbuilder.models.mixins import AuditMixin, FileColumn
from flask_appbuilder.filemanager import get_file_original_name
from flask import Markup, url_for, flash
from sqlalchemy import event
import time
from .qa import process_qa_llm
from app import db

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
    conversion_prompt = Column(Text, nullable=True)
    unittestcase_prompt = Column(Text, nullable=True)

    @hybrid_property
    def conn(self) -> str:
        conn = URL.create(
            drivername=self.dialect,  # Change this to your specific database driver
            username=self.user,
            password=self.password,  # Password with special characters
            host=self.host,
            port=str(self.port),  # Change this to your specific port
            database=self.dbname
        )
        return conn

    @hybrid_property
    def auditconn(self) -> str:

        auditconn = self.dialect + '://' + self.user + ':' + '****' + '@' + self.host + ':' + str(self.port) + '/' + self.dbname
        return str(auditconn)

    def __repr__(self):
        return self.dbname

class ProcedureConversion(Model):
    id = Column(Integer, primary_key=True)
    procedure_name = Column(String(100), nullable=False)
    python_file = Column(String(200), nullable=True)
    testcase_file = Column(String(200), nullable=True)
    sql_code = Column(Text, nullable=True)
    python_code = Column(Text, nullable=True)
    testcase_code = Column(Text, nullable=True)
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

class ModelDetails(Model):
    id = Column(Integer, primary_key=True)
    model = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    api_url = Column(String(255), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    def __repr__(self):
        return self.model

class UploadedFile(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    file = Column(FileColumn, nullable=False)
    additional_inputs = Column(Text, nullable = True)
    acceptance_criteria = Column(FileColumn, nullable=True)
    bdd_style_test_cases = Column(FileColumn, nullable=True)
    test_automation_script = Column(FileColumn, nullable=True)


    def download_file(self):
        return Markup(
            '<a href="'
            + url_for("TestCaseFilesModelView.download", filename=str(self.file))
            + '">Download File</a>'
        )
    def download_acceptance_criteria(self):
        return Markup(
            '<a href="'
            + url_for("TestCaseFilesModelView.download", filename=str(self.acceptance_criteria))
            + '" class="btn btn-primary">'
            + '<i class="fas fa-download"></i>'
            + '</a>'
        )

    def download_bdd_style_test_cases(self):
        return Markup(
            '<a href="'
            + url_for("TestCaseFilesModelView.download", filename=str(self.bdd_style_test_cases))
            + '" class="btn btn-primary">'
            + '<i class="fas fa-download"></i>'
            + '</a>'
        )

    def download_test_automation_script(self):
        return Markup(
            '<a href="'
            + url_for("TestCaseFilesModelView.download", filename=str(self.test_automation_script))
            + '" class="btn btn-primary">'
            + '<i class="fas fa-download"></i>'
            + '</a>'
        )

    def file_name(self):
        return get_file_original_name(str(self.file))


def after_insert(mapper, connection, target):
    # Perform your custom task after a record is inserted
    print('processing')
    ac_file_path,bdd_file_path,java_file_path = process_qa_llm(target.file,target.id)
    connection.execute(
        target.__table__.update().where(target.__table__.c.id == target.id).values(acceptance_criteria=ac_file_path,
                                                                                   bdd_style_test_cases=bdd_file_path,
                                                                                   test_automation_script=java_file_path )
    )
    # flash(f"New file uploaded: {target.filename}", 'info')
    # Any other processing can go here

# Register the event listener
event.listen(UploadedFile, 'after_insert', after_insert)