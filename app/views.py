import time

from flask import render_template, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi,MasterDetailView
from .models import DatabaseDetail,ProcedureConversion,GitRepository, ModelDetails, Audit,UploadedFile
from . import appbuilder, db
from flask_appbuilder.actions import action
from flask import redirect

from .tasks import convert_procedures_task
from .git_actions import push_to_git


class ProcedureConversionView(ModelView):
    datamodel = SQLAInterface(ProcedureConversion)
    list_columns = ['procedure_name', 'python_file','testcase_file']
    base_permissions = ['can_show','can_delete']
    add_exclude_columns = ['python_code','testcase_code']

class ModelDetailsView(ModelView):
    datamodel = SQLAInterface(ModelDetails)
    list_columns = ['model', 'api_url','is_default']
    add_exclude_columns = ["created_at"]


class AuditView(ModelView):
    datamodel = SQLAInterface(Audit)
    list_columns = ['message', 'stage','database']
    # base_permissions = ['can_delete']

class GitRepositoryView(ModelView):
    datamodel = SQLAInterface(GitRepository)
    list_columns = ['repo_name', 'branch_name', 'username']
    add_columns = ["database","repo_path", "branch_name",  "username", "repo_name","token"  ]
    edit_columns = ["repo_path", "branch_name", "username", "repo_name", "token"]
    add_exclude_columns = ["created_at","updated_at"]


"""
    Application wide 404 error handler
"""


class GroupModelView(ModelView):
    datamodel = SQLAInterface(DatabaseDetail)
    related_views = [GitRepositoryView,ProcedureConversionView]
    list_columns = ['dbname', 'user', 'host', 'status']

    @action("migrations", "Start Migration", "Do you really want to?", "fa-rocket")
    def myaction(self, items):
        # for item in items:
        #     print(item.id)
        convert_procedures_task(items)
        resp ='Convertion completed successfully! Please check the procedures list'
        # time.sleep(2)
        flash(resp,"info")
        """
            do something with the item record
        """
        return redirect(self.get_redirect())

class DatabaseMasterView(MasterDetailView):
    datamodel = SQLAInterface(DatabaseDetail)
    related_views = [GitRepositoryView,ProcedureConversionView]

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()

appbuilder.add_view(
    GroupModelView,
    "List Databases Group",
    icon = "fa-folder-open-o",
    category = "Databases",
    category_icon='fa fa-bitbucket'
)
# appbuilder.add_view(
#     ModelDetailsView,
#     "List Models",
#     icon = "fa-folder-open-o",
#     category = "Models",
#     # category_icon = "fa-envelope"
# )
appbuilder.add_view(
    AuditView,
    "List Audit",
    icon = "fa-folder-open-o",
    category = "Audit",
    # category_icon = "fa-envelope"
)

class TestCaseFilesModelView(ModelView):
    datamodel = SQLAInterface(UploadedFile)
    label_columns = {"id":"Id", "file": "File Name", "download_acceptance_criteria": "Acceptance Criteria",
                     "download_bdd_style_test_cases": "BDD style test cases",
                     "download_test_automation_script": "Test Automation Script"}
    add_columns = [ "name","file"]
    edit_columns = [ "name","file"]
    list_columns = ["id" ,"file_name", "download_acceptance_criteria","download_bdd_style_test_cases","download_test_automation_script"]
    show_columns = ["file_name", "download"]

appbuilder.add_view_no_menu(GitRepositoryView, endpoint=None, static_folder=None)
appbuilder.add_view_no_menu(ProcedureConversionView, endpoint=None, static_folder=None)


appbuilder.add_separator("Databases")
appbuilder.add_view(DatabaseMasterView,'Database Jobs',icon='fa fa-sitemap',category='Databases',category_icon='fa fa-sitemap')

appbuilder.add_view(TestCaseFilesModelView,'TestCases ', category='QA')
