from generic_app.models import *
from generic_app.submodels.SeleniumDownloadExample.Uploads.CompanyList import CompanyList


class Executive(Model):

    id = AutoField(primary_key=True)
    company_list = ForeignKey(to=CompanyList, on_delete=CASCADE)
    vorname = TextField(default="")
    nachname = TextField(default="")
    ort = TextField(default="")