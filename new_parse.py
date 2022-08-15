import requests
from dotenv import dotenv_values
import json

from helper import Helper

config = dotenv_values(".env")
url_collections = config['HOST_COLLECTION'] + '/api/mortgage/collection'
url_new_bank = config['HOST_NEW_BANKS'] + '/products/hypothec/api/group/'


class Parser:
    cities_collection: list
    programs_collection: list
    banks_collection: list

    def get_colletions(self):
        r = requests.get(url_collections)
        collections_data = r.json()['data']
        self.cities_collection = collections_data['cities']
        self.programs_collection = collections_data['programs']
        self.banks_collection = collections_data['banks']

    def start_parse(self):
        print('Start parsing.....')
        self.get_colletions()
        # self.get_new_banks_to_json()
        self.tranform_data_for_server()

    def get_new_banks_to_json(self):
        payload = {
            "source": "submenu_hypothec",
            "sort": "popular",
            "order": "desc",
            "isRefinance": 0
        }
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }
        city_names = []
        new_banks = {}

        for _city in self.cities_collection:
            count_page = 1
            _city_code = Helper.transform_city_name(_city["name"].lower())
            while True:
                print(f"stage:{count_page}")
                url = f"{url_new_bank}{_city_code}/"
                payload['page'] = count_page
                r = requests.get(url, headers=headers, params=payload)
                bank_json = r.json()
                r.close()

                if len(bank_json['grouped_table']) == 0:
                    break
                for row_bank in bank_json['grouped_table']:
                    for ipoteka in row_bank['credit_result_rows']:
                        _city_name = _city["name"].lower()
                        if not _city_name in new_banks:
                            new_banks[_city_name] = {}
                        if not ipoteka['bank_name'].lower() in new_banks[_city_name]:
                            new_banks[_city_name][ipoteka['bank_name'].lower()] = {}
                        new_banks[_city_name][ipoteka['bank_name'].lower()][
                            ipoteka['mortgage_name'].lower()] = ipoteka
                count_page = count_page + 1
                city_names.append(_city_name)
        with open('upload/data_new.json', 'w', encoding='utf-8') as f:
            json.dump(new_banks, f, ensure_ascii=False, indent=4)



    def get_new_banks_from_json(self):
        with open('upload/data_new.json', 'r', encoding='utf-8') as f:
            _ipoteka = json.load(f)
            return _ipoteka



    def tranform_data_for_server(self):
        _mortgages_file = self.get_new_banks_from_json()
        banks = []
        for city in self.cities_collection:
            _city_name = city['name'].lower()
            for _city_key in _mortgages_file.keys():
                if _city_name in _city_key:
                    for bank in self.banks_collection:
                        _bank_name = bank['name'].lower()
                        for _bank_key in _mortgages_file[_city_key].keys():
                            if _bank_name in _bank_key:
                                for program in self.programs_collection:
                                    _program_name = program['name'].lower()
                                    for _program_key in _mortgages_file[_city_key][_bank_key].keys():
                                        if _program_name in _program_key:
                                            banks.append(_mortgages_file[_city_key][_bank_key][_program_key])
        print(banks[0])
        exit()


parser = Parser()
parser.start_parse()
