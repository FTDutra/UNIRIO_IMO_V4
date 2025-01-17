import pandas as pd
from slugify import slugify
from datetime import datetime

class CreateJsonPreparation:
    def __init__(self, form_dict):
        self.form_dict = form_dict
        self.dataset = pd.read_csv('static/dataset/Bin_1.csv')

    def get_data(self, element, expected_type):
        """
        Retorna o valor do elemento do dicionário `form_dict` com base no tipo esperado.

        :param element: A chave do dicionário para recuperar o valor.
        :param expected_type: O tipo esperado do valor (str, int, bool). Padrão é str.
        :return: Valor formatado com base no tipo esperado ou um valor padrão.
        """
        val = self.form_dict.get(element, "")

        if expected_type == str:
            return val if val != "" else ""

        elif expected_type == int:
            try:
                return int(val) if val != "" else 0
            except ValueError:
                return 0

        elif expected_type == bool:
            return 1 if isinstance(val, str) and val.lower() == "on" else 0

        else:
            raise ValueError(f"Tipo esperado {expected_type} não suportado.")

    def structure(self):
        project_info = {
            "PROJECT_NAME": self.get_data("plainTextEditProjectName", expected_type=str),
            "PROJECT_NAME_SLUG": slugify(self.get_data("plainTextEditProjectName", expected_type=str)),
            "BROKER": self.get_data("plainTextEditBrookerName", expected_type=str),
            "CRECI": self.get_data("plainTextEditBrookerCRECI", expected_type=str),
            "BUSINESS_ADDRESS": self.get_data("plainTextEditBrookerBusinessAddress", expected_type=str),
            "HOUSE_ADDRESS": self.get_data("plainTextEditHouseAdress", expected_type=str),
            "HOUSE_OWNER": self.get_data("plainTextEditHouseOwner", expected_type=str),
            "UNIQUE_KEY": "",
            "CREATED_AT": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data = {
            "FURNISHED": self.get_data("itemFURNISHED", expected_type=bool),
            "GOURMET_SPACE": self.get_data("itemGOURMET_SPACE", expected_type=bool),
            "KITCHEN": self.get_data("itemKITCHEN", expected_type=bool),
            "DRESS_ROOM": 1,
            "BALCONY": 1 if (self.get_data("itemBALCONY", expected_type=bool) or self.get_data("itemGOURMET_SPACE", expected_type=bool) or self.get_data("itemGARDEN", expected_type=bool)) else 0,
            "SPORTS_COURT": self.get_data("itemSPORTS_COURT", expected_type=bool),
            "FOOD_COURT": self.get_data("itemFOOD_COURT", expected_type=bool),
            "RECREATION_AREA": self.get_data("itemRECREATION_AREA", expected_type=bool),
            "REST_AREAS": self.get_data("itemREST_AREAS", expected_type=bool),
            "POOL": self.get_data("itemPOOL", expected_type=bool),
            "SAFETY": self.get_data("itemSAFETY", expected_type=bool),
            "VIEW": self.get_data("itemVIEW", expected_type=bool),
            "ACCESSIBILITY": self.get_data("itemACCESSIBILITY", expected_type=bool),
            "WORK_AREAS": self.get_data("itemWORK_AREAS", expected_type=bool),
            "GARAGE": self.get_data("itemGARAGE", expected_type=bool),
            "SUSTAINABILITY": self.get_data("itemSUSTAINABILITY", expected_type=bool),
            "OUTDOOR_AREAS": 1 if (self.get_data("itemOUTDOOR_AREAS", expected_type=bool) or self.get_data("itemGARDEN", expected_type=bool)) else 0,
            "PET_FRIENDLY": self.get_data("itemPET_FRIENDLY", expected_type=bool),
            "MID_END_APARTMENT_AMENITIES": 1 if (self.get_data("itemMID_END_APARTMENT_AMENITIES", expected_type=bool) or self.get_data("itemHIGH_END_APARTMENT_AMENITIES", expected_type=bool)) else 0,
            "HIGH_END_APARTMENT_AMENITIES": self.get_data("itemHIGH_END_APARTMENT_AMENITIES", expected_type=bool),
            "HIGH_END_CONDO_AMENITIES": 1 if self.get_data("itemHIGH_END_APARTMENT_AMENITIES", expected_type=bool) else 0,
            "ZONE_CODE": int(self.dataset.loc[self.dataset['ZONE'] == self.get_data("itemZONE", expected_type=str), 'ZONE_CODE'].iloc[0]),
            "NEIGHBORHOOD_CODE": int(self.dataset.loc[self.dataset['NEIGHBORHOOD'] == self.get_data("itemNEIGHBORHOOD", expected_type=str), 'NEIGHBORHOOD_CODE'].iloc[0]),
            "USABLEAREAS":  self.get_data("itemUSABLEAREAS", expected_type=int),
            "TOTALAREAS":  self.get_data("itemUSABLEAREAS", expected_type=int),
            "PARKINGSPACES":  1 if self.get_data("itemGARAGE", expected_type=bool) else 0,
            "SUITES":  self.get_data("itemSUITES", expected_type=int),
            "BEDROOMS":  self.get_data("itemBEDROOMS", expected_type=int),
            "ELEVATOR":  self.get_data("itemELEVATOR", expected_type=bool),
            "SERVICE_AREA":  self.get_data("itemSERVICE_AREA", expected_type=bool),
            "LAUNDRY":  self.get_data("itemLAUNDRY", expected_type=bool),
            "LUNCH_ROOM":  self.get_data("itemLUNCH_ROOM", expected_type=bool),
            "ESSENTIAL_PUBLIC_SERVICES":  self.get_data("itemESSENTIAL_PUBLIC_SERVICES", expected_type=bool),
            "NEAR_HOSPITAL":  self.get_data("itemNEAR_HOSPITAL", expected_type=bool),
            "NEAR_SHOPPING_CENTER":  self.get_data("itemNEAR_SHOPPING_CENTER", expected_type=bool),
            "COVERAGE":  self.get_data("itemCOVERAGE", expected_type=bool),
            "YEARLY_EXPENSES":  self.get_data("itemIPTU", expected_type=int) + (self.get_data("itemCONDOFEE", expected_type=int) * 12),
            "ZONE": self.get_data("itemZONE", expected_type=str),
            "NEIGHBORHOOD": self.get_data("itemNEIGHBORHOOD", expected_type=str),
            "STREET": self.get_data("itemSTREET", expected_type=str),
            "PRICE_BIN": "Bin_1",
            "STREET_RELEVANCE": float(self.dataset.loc[self.dataset['STREET'] == self.get_data("itemSTREET", expected_type=str), 'STREET_RELEVANCE'].iloc[0])
        }

        structure = {
            "PROJECT_INFO": project_info,
            "DATA": data
        }

        return structure
