class Helper:

    @staticmethod
    def transform_city_name(name: str):
        city_codes = {
            "тюмень": "tyumen~",
            "екатерибург": "ekaterinburg",
            "казань": "kazan~",
            "москва": "moskva",
        }
        name = name.lower()
        return city_codes[name]
