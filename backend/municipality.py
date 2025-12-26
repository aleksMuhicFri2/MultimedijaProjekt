
# defines a new municipality object with necessary data

class Municipality:
    def __init__(self, code, name):
        self.code = code          # "061"
        self.name = name          # "Ljubljana"
        self.region = None

        # Population
        self.population_young = 0
        self.population_working = 0
        self.population_old = 0

        # Prices
        self.avg_price_m2_apartment = None
        self.avg_price_m2_house = None
        self.avg_rent_m2 = None

        self.deals_sale_apartment = 0
        self.deals_sale_house = 0
        self.deals_rent = 0

        # IOZ (health insurance) data
        self.ioz_ratio = None
        self.insured_total = None
        self.insured_with_ioz = None
        self.insured_without_ioz = None

        # MetaData
        self.latitude = None
        self.longitude = None

        self.history_sunny_days = 0
        self.history_rainy_days = 0
        self.history_foggy_days = 0
        self.history_avg_aqi = 0.0
        self.history_avg_temp = 0.0

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "region": self.region,
            "population_young": self.population_young,
            "population_working": self.population_working,
            "population_old": self.population_old,
            "avg_price_m2_apartment": self.avg_price_m2_apartment,
            "avg_price_m2_house": self.avg_price_m2_house,
            "avg_rent_m2": self.avg_rent_m2,
            "deals_sale_apartment": self.deals_sale_apartment,
            "deals_sale_house": self.deals_sale_house,
            "deals_rent": self.deals_rent,
            "ioz_ratio": self.ioz_ratio,
            "insured_total": self.insured_total,
            "insured_with_ioz": self.insured_with_ioz,
            "insured_without_ioz": self.insured_without_ioz,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "history_sunny_days" : self.history_sunny_days,
            "history_rainy_days" : self.history_rainy_days,
            "history_foggy_days" : self.history_foggy_days,
            "history_avg_aqi" : self.history_avg_aqi,
            "history_avg_temp" : self.history_avg_temp
        }
