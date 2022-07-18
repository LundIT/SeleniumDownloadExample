import os
import shutil
import time
from datetime import datetime
import pandas as pd
import xmltodict
from django.core.files import File
from django.db.models import DateField, BooleanField

from DjangoProcessAdminGeneric.settings import MEDIA_ROOT
from ProcessAdminRestApi.models.upload_model import ConditionalUpdateMixin
from generic_app.models import *


class CompanyList(UploadModelMixin, ConditionalUpdateMixin, Model):

    id = AutoField(primary_key=True)
    period_date = DateField()
    company_list = FileField(null=True, blank=True)
    get_chronological = BooleanField(default=False)
    get_structured = BooleanField(default=False)

    # FLAG that is set to determine whether the documents should be purchased or not
    buy_pdfs = False
    # i is the starting ID of the Chrono or Structured Table Item
    i= 184

    def __str__(self):
        return str(self.period_date)


    @ConditionalUpdateMixin.conditional_calculation
    def update(self):
        from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Handelsregisterauszug import Handelsregisterauszug
        companies = pd.read_excel(self.company_list)

        self.i = 184
        driver = Handelsregisterauszug.create_driver(self)
        # create a Handelsregisterauszug objekt for every company.
        # Todo delete handelsregisterauszüge that are no longer mentioned in the companies list
        for company in companies['Companies']:
            downloaded_files = Handelsregisterauszug.objects.filter(company_list=self, company_name=company)
            if downloaded_files.count() == 0:
                downloaded_file = Handelsregisterauszug(company_list=self, company_name=company)
                downloaded_file.save()
                downloaded_file.driver = driver
                downloaded_file.update()
                downloaded_file.save()

        period_string = Handelsregisterauszug.period_string(self)

        if self.get_structured or self.get_chronological:
            try:
                os.remove(os.path.abspath(f"{MEDIA_ROOT}{os.sep}{period_string}.zip"),)
            except OSError:
                pass

            result = shutil.make_archive(f"{MEDIA_ROOT}{os.sep}{period_string}", 'zip', f"{MEDIA_ROOT}{os.sep}{period_string}")

            from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.HandelsregisterZIP import HandelsregisterZIP
            handelsregister_zips = HandelsregisterZIP.objects.filter(company_list=self)
            if len(handelsregister_zips)==1:
                handelsregister_zip = handelsregister_zips.first()
            else:
                handelsregister_zip = HandelsregisterZIP(company_list=self)
                handelsregister_zip.save()

            handelsregister_zip.handelsregister_zip.name = period_string + ".zip"
            handelsregister_zip.save()

            if self.get_structured:
                handelsregister_zip.create_excel()
                handelsregister_zip.save()
