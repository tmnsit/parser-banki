class Helper:

    @staticmethod
    def transform_city_name(name: str):
        city_codes = {
            "тюмень": "tyumen~",
            "екатеринбург": "ekaterinburg",
            "казань": "kazan~",
            "москва": "moskva",
            "курган": "kurgan",
        }
        name = name.lower()
        return city_codes[name]
