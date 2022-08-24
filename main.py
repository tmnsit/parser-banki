import requests
from dotenv import dotenv_values
import json
import math
import os


from helper import Helper

config = dotenv_values(".env")


class Parser:
    cities_collection: list
    programs_collection: list
    banks_collection: list

    def get_colletions(self):
        url_collections = config['HOST_SERVER'] + config['PATH_GET_BANK_COLLECTION']
        r = requests.get(url_collections)
        collections_data = r.json()['data']
        self.cities_collection = collections_data['cities']
        self.programs_collection = collections_data['programs']
        self.banks_collection = collections_data['banks']

    def start_parse(self):
        print('Start parsing.....')
        self.get_colletions()
        self.get_new_banks_to_json()
        _banks = self.tranform_data_for_server()
        self.save_finish_file_json({"mortgages": _banks})
        self.send_json_to_server(data=_banks)

    def send_json_to_server(self, data):
        _request_json = json.dumps({"banks": data}, ensure_ascii=False).encode('utf-8')
        url = config['HOST_SERVER'] + config['PATH_SAVE_API']
        r = requests.post(url, data=_request_json,
                          headers={"Content-Type": "application/json; charset=utf-8",
                                   "Accept": "application/json; charset=utf-8"})
        print(r.json())

    def get_new_banks_to_json(self):
        url_new_bank = config['HOST_NEW_BANKS'] + '/products/hypothec/api/group/'
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
        with open('upload/data.json', 'w', encoding='utf-8') as f:
            json.dump(new_banks, f, ensure_ascii=False, indent=4)

    def save_finish_file_json(self, data):
        with open(os.path.dirname(os.path.abspath(__file__)) + '/upload/finish.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_new_banks_from_json(self):
        with open(os.path.dirname(os.path.abspath(__file__)) + '/upload/data.json', 'r', encoding='utf-8') as f:
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
                                    for code in program['codes']:
                                        for _program_key in _mortgages_file[_city_key][_bank_key].keys():
                                            if code.lower().strip() in _program_key.lower().strip():
                                                _new_bank = self.arr_prepair(
                                                    _mortgages_file[_city_key][_bank_key][_program_key], bank_id=bank['id'],
                                                    city_id=city['id'], program_id=program['id'])
                                                banks.append(_new_bank)
        return banks

    def arr_prepair(self, arr_bank, bank_id, city_id, program_id):
        if arr_bank['initial_fee_from'] is None:
            arr_bank['initial_fee_from'] = 0
        if arr_bank['amount_from'] is None:
            arr_bank['amount_from'] = 0
        apart_price_min = round(arr_bank['amount_from'] / (1 - (arr_bank['initial_fee_from'] / 100)))
        apart_price_max = round(arr_bank['amount_to'] / (1 - (95 / 100)))
        term_min = round(arr_bank['period_from'] / 365)
        term_max = round(arr_bank['period_to'] / 365)


        _bank = {
            "id": bank_id,
            "city": city_id,
            "rate": arr_bank['rate_min'],
            "term": {
                "min": term_min,
                "max": term_max
            },
            "apart-price": {
                "min": apart_price_min,
                "max": apart_price_max,
            },
            "amount-of-credit": {
                "min": arr_bank['amount_from'],
                "max": arr_bank['amount_to']
            },
            "first-payment": {
                "min": arr_bank['initial_fee_from'],
                "max": 95
            },
            "programs": [
                program_id
            ],
            "original_name": arr_bank['mortgage_name']
        }
        return _bank


def main():
    parser = Parser()
    parser.start_parse()


if __name__ == '__main__':
    main()
