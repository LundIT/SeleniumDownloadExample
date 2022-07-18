from generic_app.models import *
from generic_app.submodels.SeleniumDownloadExample.Uploads.CompanyList import CompanyList


class Gesellschaft(Model):

    id = AutoField(primary_key=True)
    company_list = ForeignKey(to=CompanyList, on_delete=CASCADE)
    bezeichnung = TextField(default='')
    rechtsform = TextField(default='')
    strasse = TextField(default='')
    hausnummer = TextField(default='')
    postleitzahl = TextField(default='')
    ort = TextField(default='')
    stammkapital = TextField(default='')
    gegenstand_oder_geschaeftszweck = TextField(default='')