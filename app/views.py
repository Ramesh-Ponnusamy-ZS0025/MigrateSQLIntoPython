from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi,MasterDetailView
from .models import DatabaseDetail,ProcedureConversion,GitRepository
from . import appbuilder, db
from flask_appbuilder.actions import action
from flask import redirect

from .tasks import convert_procedures_task
from .git_actions import push_to_git


class DatabaseDetailView(ModelView):
    datamodel = SQLAInterface(DatabaseDetail)
    list_columns = ['dbname', 'user', 'host', 'status']
    # related_views = [ContactModelView]

    # @action("convert", "Convert Procedures", confirmation="Are you sure?", icon="fa-play", multiple=False)
    # def convert_procedures(self, item):
    #     # Trigger Celery task to start conversion
    #     convert_procedures_task.apply_async(args=[item.id], countdown=1)
    #     item.status = 'in_progress'
    #     self.datamodel.edit(item)
    #     flash(f"Started procedure conversion for database: {item.dbname}", "info")
    #     return redirect(self.get_redirect())
    @action("migrations", "Start Migration", "Do you really want to?", "fa-rocket")
    def myaction(self, items):
        # for item in items:
        #     print(item.id)
        convert_procedures_task(items)
        """
            do something with the item record
        """
        return redirect(self.get_redirect())


class ProcedureConversionView(ModelView):
    datamodel = SQLAInterface(ProcedureConversion)
    list_columns = ['procedure_name', 'python_file','python_code','testcase_file','testcase_code']
    base_permissions = ['can_show','can_delete']


class GitRepositoryView(ModelView):
    datamodel = SQLAInterface(GitRepository)
    list_columns = ['repo_name', 'branch_name', 'username']
    add_columns = ["repo_path", "branch_name",  "username", "repo_name","token"  ]
    edit_columns = ["repo_path", "branch_name", "username", "repo_name", "token"]
    add_exclude_columns = ["created_at","updated_at"]

    @action("push", "Start Migration", "Do you really want to?", "fa-rocket")
    def pushaction(self, items):
        for item in items:
            print(item.id)
            push_to_git(item.id)

        return redirect(self.get_redirect())


class DatabaseMasterView(MasterDetailView):
    datamodel = SQLAInterface(DatabaseDetail)
    related_views = [GitRepositoryView,ProcedureConversionView]

"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)


    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

"""
    Application wide 404 error handler
"""

class GroupModelView(ModelView):
    datamodel = SQLAInterface(DatabaseDetail)
    related_views = [ProcedureConversionView]

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
    category_icon = "fa-envelope"
)

appbuilder.add_view(
    DatabaseDetailView,
    "List Databases",
    icon = "fa-folder-open-o",
    category = "Databases",
    category_icon = "fa-envelope"
)
appbuilder.add_view(
    ProcedureConversionView,
    "List Procedures",
    icon = "fa-envelope",
    category = "Databases"
)

appbuilder.add_view(
    GitRepositoryView,
    "List Git Repo",
    icon = "fa-folder-open-o",
    category = "Git",
    category_icon = "fa-envelope"
)
appbuilder.add_view(DatabaseMasterView,'Database Jobs',icon='fa fa-sitemap',category='Database Details',category_icon='fa fa-sitemap')
