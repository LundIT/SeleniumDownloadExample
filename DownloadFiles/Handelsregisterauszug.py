import shutil
import time
from datetime import datetime

import xmltodict
from django.core.files import File

from DjangoProcessAdminGeneric.settings import MEDIA_ROOT
from ProcessAdminRestApi.models.upload_model import ConditionalUpdateMixin
from generic_app.models import *
from generic_app.submodels.SeleniumDownloadExample.Uploads.CompanyList import CompanyList

from selenium import webdriver
from selenium.webdriver.common.by import By

class Handelsregisterauszug(Model):

    id = AutoField(primary_key=True)
    company_list = ForeignKey(to=CompanyList, on_delete=CASCADE)
    company_name = TextField(default="")
    handelsregister_auszug = PDFField(null=True, blank=True)
    structured_handelsregister_auszug = FileField(null=True, blank=True)

    driver = None

    buy_pdfs = os.getenv('BUY_PDF')
    if buy_pdfs is not True:
        buy_pdfs = False

    def update(self):
        print(f"Handelsregisterauszug für {self.company_name}")
        if self.driver is None:
            self.driver = self.create_driver(self.company_list)
        if self.company_list.get_chronological:
            self.get_chronological_handelsregister_auszug()
        if self.company_list.get_structured:
            self.get_structured_handelsregister_auszug()
            self.insert_gesellschaft()
            self.insert_beteiligte()



    def get_structured_handelsregister_auszug(self):
        self.get_type_of_handelsregister_auszug(type="Structured")

    def get_chronological_handelsregister_auszug(self):
        self.get_type_of_handelsregister_auszug(type="Chronological")

    @classmethod
    def period_string(cls, period):
        return period.period_date.strftime('%Y%m%d')

    @classmethod
    def downloadDir(cls, period):
        period_string = Handelsregisterauszug.period_string(period)
        return f"{MEDIA_ROOT}//download_chrono//{period_string}"

    @classmethod
    def create_driver(cls, period):
        downloadDir = Handelsregisterauszug.downloadDir(period)
        # Make sure path exists.
        Path(downloadDir).mkdir(parents=True, exist_ok=True)
        # Set Preferences.
        preferences = {"download.default_directory": os.path.abspath(downloadDir),
                       "download.prompt_for_download": False,
                       "directory_upgrade": True,
                       "safebrowsing.enabled": True}
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("prefs", preferences)
        # chromeOptions.add_argument('headless')
        driver = webdriver.Chrome(
            executable_path='C:\\Users\\MaximilianLund\\Downloads\\chromedriver_win32 (2)\\chromedriver.exe',
            options=chromeOptions)
        driver = cls.login_handelsregister(driver)
        return driver

    @classmethod
    def login_handelsregister(cls, driver):
        driver.implicitly_wait(10)
        # LOGIN
        # Step # | name | target | value
        # 1 | open | https://www.handelsregister.de/rp_web/normalesuche.xhtml |
        driver.get("https://www.handelsregister.de/rp_web/normalesuche.xhtml")
        # 2 | setWindowSize | 1289x1031 |
        driver.set_window_size(1289, 1031)
        # 4 | click | css=#loginMenuItem > .ui-menuitem-text |
        driver.find_element(By.CSS_SELECTOR, "#loginMenuItem > .ui-menuitem-text").click()
        # 5 | click | id=loginForm:benutzername |
        driver.find_element(By.ID, "loginForm:benutzername").click()
        # 6 | type | id=loginForm:benutzername | Armira
        driver.find_element(By.ID, "loginForm:benutzername").send_keys(os.getenv('handelsregister_username'))
        # 7 | type | id=loginForm:kennwort |
        driver.find_element(By.ID, "loginForm:kennwort").send_keys(os.getenv('handelsregister_password'))
        # 8 | click | css=.ui-chkbox-box |
        driver.find_element(By.CSS_SELECTOR, ".ui-chkbox-box").click()
        time.sleep(1)
        # 9 | click | css=.ui-button-text |
        driver.find_element(By.CSS_SELECTOR, ".ui-button-text").click()
        return driver

    # arbitrary ID given by the handelsregister for the table entries
    i = 184

    def get_type_of_handelsregister_auszug(self, type):
        downloadDir = Handelsregisterauszug.downloadDir(self.company_list)
        period_string = Handelsregisterauszug.period_string(self.company_list)

        if (type=='Chronological' and (self.handelsregister_auszug.name in ("", None)) or (type=="Structured" and self.structured_handelsregister_auszug.name in ("", None))):

            self.driver.implicitly_wait(10)
            # Getting companies file
            # Step # | name | target | value
            # 1 | open | https://www.handelsregister.de/rp_web/normalesuche.xhtml |
            self.driver.get("https://www.handelsregister.de/rp_web/normalesuche.xhtml")
            # 2 | setWindowSize | 1289x1031 |
            self.driver.set_window_size(1289, 1031)
            # 3 | click | id=form:schlagwoerter |
            self.driver.find_element(By.ID, "form:schlagwoerter").click()
            self.driver.find_element(By.ID, "form:schlagwoerter").clear()
            self.driver.find_element(By.ID, "form:schlagwoerter").send_keys(self.company_name)
            # 5 | click | css=.ui-g:nth-child(3) > .ui-md-12 > label |
            self.driver.find_element(By.CSS_SELECTOR, ".ui-g:nth-child(3) > .ui-md-12 > label").click()
            # 6 | click | css=#form\3A btnSuche > .ui-button-text |
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            self.driver.find_element(By.CSS_SELECTOR, "#form\\3A btnSuche > .ui-button-text").click()
            # 7 | click | id=ergebnissForm:selectedSuchErgebnisFormTable:0:j_idt184:1:popupLink |

            ergebnis = None
            exception = None
            while ergebnis is None and self.i<=190:
                try:
                    if type == 'Chronological':
                        ergebnis = self.driver.find_element(By.ID,
                                                f"ergebnissForm:selectedSuchErgebnisFormTable:0:j_idt{self.i}:1:popupLink")
                    elif type == 'Structured':
                        ergebnis = self.driver.find_element(By.ID,
                                                        f"ergebnissForm:selectedSuchErgebnisFormTable:0:j_idt{self.i}:6:popupLink")
                except Exception as e:
                    print(f"Failed to load ergebnissForm:selectedSuchErgebnisFormTable:0:j_idt{self.i}:1:popupLink for company {self.company_name}")
                    exception = e
                    self.i += 1

            if ergebnis is None:
                raise exception

            ergebnis.click()

            if self.buy_pdfs:
                ### ATTENTION!!! Buys the product!!!
                # 15 | click | css=#form\3Akostenpflichtigabrufen > .ui-button-text |
                self.driver.find_element(By.CSS_SELECTOR,
                                         "#form\\3Akostenpflichtigabrufen > .ui-button-text").click()
            else:
                ### FAKE Download for Tests
                if type == 'Chronological':
                    shutil.copyfile(
                        'generic_app/submodels/SeleniumDownloadExample/Tests/Handelsregisterauszug.pdf',
                        f"{downloadDir}{os.sep}Handelsregisterauszug.pdf")
                elif type == 'Structured':
                    if self.company_name.endswith("KG"):
                        shutil.copyfile('generic_app/submodels/SeleniumDownloadExample/Tests/StructuredHandelsregisterauszug_KG.xml',
                            f"{downloadDir}{os.sep}StructuredHandelsregisterauszug_KG.xml")
                    else:
                        shutil.copyfile('generic_app/submodels/SeleniumDownloadExample/Tests/StructuredHandelsregisterauszug_GmbH.xml',
                                        f"{downloadDir}{os.sep}StructuredHandelsregisterauszug_GmbH.xml")

            time.sleep(1)
            latest_file = '.tmp'
            while latest_file.endswith('.tmp'):
                list_of_files = glob(downloadDir + '/*')
                try:
                    latest_file = max(list_of_files, key=os.path.getctime)
                except FileNotFoundError as e:
                    latest_file = '.tmp'

            ### wait for the files to be completely downloaded
            #file_size = -1
            #while file_size != os.path.getsize(latest_file):
            #    print(f"Waiting 1 sec for file {latest_file}")
            #    time.sleep(1)

            with open(latest_file, 'rb') as f:
                if type=="Chronological":
                    self.handelsregister_auszug.save(f'{period_string}{os.sep}{self.company_name}_{period_string}.pdf',
                                                                File(f))
                elif type=="Structured":
                    with open(latest_file, 'rb') as f:
                        self.structured_handelsregister_auszug.save(f'{period_string}{os.sep}{self.company_name}_{period_string}.xml',
                                                                    File(f))
            self.save()
            CalculationLog(timestamp=datetime.now(), method=f"Type Handelsregisterauszug", message=f"Saved {type} HRGA for {self.company_name} for Date {self.company_list.period_date}").save()

    def insert_gesellschaft(self):
        from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Gesellschaft import Gesellschaft
        self.structured_handelsregister_auszug.seek(0)
        handelsregister_dict = xmltodict.parse(self.structured_handelsregister_auszug)
        bezeichnung = \
        handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Bezeichnung']['Bezeichnung_Aktuell']
        rechtsform = \
        handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Rechtsform']['content']
        strasse = handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Anschrift']['Strasse']
        hausnummer = \
        handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Anschrift']['Hausnummer']
        postleitzahl = \
        handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Anschrift']['Postleitzahl']
        ort = handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Anschrift']['Ort']
        # stammkapital = handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Zusatzangaben']['Kapitalgesellschaft']['Zusatz_GmbH']['Stammkapital']['Zahl']
        # gegenstand_oder_geschaeftszweck = handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Gegenstand_oder_Geschaeftszweck']
        stammkapital = 0
        gegenstand_oder_geschaeftszweck = ""

        Gesellschaft.objects.filter(company_list=self.company_list, bezeichnung=bezeichnung).delete()
        gesellschaft = Gesellschaft(company_list=self.company_list, bezeichnung=bezeichnung, rechtsform=rechtsform, strasse=strasse,
                                    hausnummer=hausnummer, postleitzahl=postleitzahl, ort=ort,
                                    stammkapital=stammkapital,
                                    gegenstand_oder_geschaeftszweck=gegenstand_oder_geschaeftszweck)
        gesellschaft.save()

    def insert_beteiligte(self):
        from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Executive import Executive
        from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Geschaeftsfuehrer import \
            Geschaeftsfuehrer
        self.structured_handelsregister_auszug.seek(0)
        handelsregister_dict = xmltodict.parse(self.structured_handelsregister_auszug)

        from generic_app.submodels.SeleniumDownloadExample.DownloadFiles.Gesellschaft import Gesellschaft
        bezeichnung = \
        handelsregister_dict['XJustiz_Daten']['Fachdaten_Register']['Basisdaten_Register']['Rechtstraeger'][
            'Bezeichnung']['Bezeichnung_Aktuell']
        gesellschaft = Gesellschaft.objects.get(company_list=self.company_list, bezeichnung=bezeichnung)

        daten = handelsregister_dict['XJustiz_Daten']['Grunddaten']['Verfahrensdaten']['Beteiligung']
        for id in range(0, len(daten)):
            beteiligter = daten[id]['Beteiligter']
            if 'Natuerliche_Person' in beteiligter:
                rollenbezeichnung = daten[id]['Rolle']['Rollenbezeichnung'][
                    'content']
                vorname = beteiligter['Natuerliche_Person']['Voller_Name'][
                    'Vorname']
                nachname = beteiligter['Natuerliche_Person']['Voller_Name'][
                    'Nachname']
                if rollenbezeichnung in ['Geschäftsführer(in)', 'Prokurist(in)']:
                    ort = beteiligter['Natuerliche_Person']['Anschrift']['Ort']
                    executives = Executive.objects.filter(vorname=vorname, nachname=nachname)
                    assert len(executives) <= 1, f"Found more than 1 Executive for {vorname} {nachname} in {self}"
                    if len(executives) == 0:
                        executive = Executive(company_list=self.company_list, vorname=vorname, nachname=nachname, ort=ort)
                        executive.save()
                    else:  # len(executives) == 1:
                        executive = executives.first()

                    geschaeftsfuehrer = Geschaeftsfuehrer(company_list=self.company_list, geschaeftsfuehrer=executive,
                                                          gesellschaft=gesellschaft,
                                                          rollenbezeichnung=rollenbezeichnung)
                    geschaeftsfuehrer.save()
