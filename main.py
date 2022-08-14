import requests
from dotenv import dotenv_values
import json

from helper import Helper
from models.bank import Bank, Program, City

config = dotenv_values(".env")

url_old_bank = config['HOST_OLD_BANKS'] + '/api/mortgage'
url_old_filter = config['HOST_OLD_BANKS'] + '/api/mortgage/filter'
url_new_bank = config['HOST_NEW_BANKS'] + '/products/hypothec/api/group/'


cities = {}
programs = {}
mortgages = {}


def get_item_banks():
    r = requests.get(url_old_bank)
    banks_json = r.json()['data']
    for bank in banks_json:
        _programs = list[Program]
        _arr_programs = bank['programs']
        _city_name = bank['city']
        del bank['city']
        bank['programs'] = []
        _bank_row = json.dumps(bank, ensure_ascii=False, indent=4)
        _bank_entity = Bank.parse_raw(_bank_row)
        for program_key in _arr_programs:
            if _bank_entity.program is None:
                _bank_entity.program = []
            _bank_entity.program.append(programs[program_key])
        _bank_entity.city = cities[_city_name]
        mortgages[_bank_entity.id] = _bank_entity


def parse_old():
    r = requests.get(url_old_filter)
    filter_json = r.json()['data']
    for item in filter_json:
        if item['name'] == 'program':
            for option in item['options']:
                row = json.dumps(option, ensure_ascii=False, indent=4)
                programs[option['value']] = Program.parse_raw(row)
        if item['name'] == 'city_id':
            for option in item['options']:
                option['code'] = Helper.transform_city_name(option['text'])
                row = json.dumps(option, ensure_ascii=False, indent=4)
                cities[option['text']] = City.parse_raw(row)
    r.close()
    return programs




def get_new_banks_to_json(cities):
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

    count_page = 1
    city_names = []
    for city_key in cities:
        code_path = Helper.transform_city_name(city_key)
        new_banks = {}
        while (True):
            print(f"stage:{count_page}")
            url = f"{url_new_bank}{code_path}/"
            payload['page'] = count_page
            r = requests.get(url, headers=headers, params=payload)
            bank_json = r.json()
            r.close()
            if len(bank_json['grouped_table']) == 0:
                break
            for row_bank in bank_json['grouped_table']:
                for ipoteka in row_bank['credit_result_rows']:
                    if not city_key in new_banks:
                        new_banks[city_key] = {}
                    if not ipoteka['bank_name'] in new_banks[city_key]:
                        new_banks[city_key][ipoteka['bank_name']] = []
                new_banks[city_key][ipoteka['bank_name']].append(ipoteka)
            count_page = count_page + 1

        with open('upload/data.json', 'w', encoding='utf-8') as f:
            json.dump(new_banks, f, ensure_ascii=False, indent=4)
        city_names.append(city_key)


def get_new_banks_from_json():
    with open('upload/data.json', 'r', encoding='utf-8') as f:
        ipoteka = json.load(f)
        print(ipoteka)


def main():
    print('start parser...')
    parse_old()
    get_item_banks()
    # getNewBanksToJson(cities)
    # ipoteka = get_new_banks_from_json()
    # print(jsonServer)



if __name__ == '__main__':
    main()
