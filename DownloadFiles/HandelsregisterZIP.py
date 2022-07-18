from datetime import datetime

import pandas as pd

from ProcessAdminRestApi.models.upload_model import ConditionalUpdateMixin
from generic_app.models import *
from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Geschaeftsfuehrer import Geschaeftsfuehrer
from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Gesellschaft import Gesellschaft
from generic_app.submodels.SeleniumDownloadExample.Uploads.CompanyList import CompanyList


class HandelsregisterZIP(Model):

    id = AutoField(primary_key=True)
    company_list = ForeignKey(to=CompanyList, on_delete=CASCADE)
    handelsregister_zip = FileField(null=True, blank=True)
    handelsregister_excel = XLSXField(null=True, blank=True, upload_to='excel')

    def create_excel(self):
        geschaeftsfuehrer_qs = Geschaeftsfuehrer.objects.filter(company_list=self.company_list).values('geschaeftsfuehrer__vorname', 'geschaeftsfuehrer__nachname', 'geschaeftsfuehrer__ort', 'gesellschaft__bezeichnung', 'rollenbezeichnung')
        gesellschafts_qs = Gesellschaft.objects.filter(company_list=self.company_list).values()

        geschaeftsfuehrer_df = pd.DataFrame.from_records(geschaeftsfuehrer_qs)
        gesellschafts_df = pd.DataFrame.from_records(gesellschafts_qs)

        date_time = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f'{date_time}_handelsregister_{self.company_list.period_date.strftime("%Y%m%d")}.xlsx'

        XLSXField.create_excel_file_from_dfs(self=self.handelsregister_excel, path=file_name, data_frames=[geschaeftsfuehrer_df, gesellschafts_df], sheet_names=['Geschaeftsfuehrer', 'Gesellschaften'])

