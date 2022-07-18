from generic_app.models import *
from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Executive import Executive
from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Gesellschaft import Gesellschaft
from generic_app.submodels.SeleniumDownloadExample.Uploads.CompanyList import CompanyList


class Geschaeftsfuehrer(Model):

    id = AutoField(primary_key=True)
    company_list = ForeignKey(to=CompanyList, on_delete=CASCADE)
    geschaeftsfuehrer = ForeignKey(to=Executive, on_delete=CASCADE)
    gesellschaft = ForeignKey(to=Gesellschaft, on_delete=CASCADE)
    rollenbezeichnung = TextField(default='')