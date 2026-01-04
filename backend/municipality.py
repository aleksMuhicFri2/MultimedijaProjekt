# defines a new municipality object with necessary data

class Municipality:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.region = None

        # Population (unknown until loaded)
        self.population_young = None
        self.population_working = None
        self.population_old = None
        self.main_demographic = None

        self.area_km2 = None

        # Prices
        self.avg_price_m2_apartment = None
        self.avg_price_m2_house = None
        self.avg_rent_m2 = None

        self.deals_sale_apartment = None
        self.deals_sale_house = None
        self.deals_rent = None

        # IOZ
        self.ioz_ratio = None
        self.insured_total = None
        self.insured_with_ioz = None
        self.insured_without_ioz = None

        # MetaData
        self.latitude = None
        self.longitude = None

        # History (unknown until loaded)
        self.history_sunny_days = None
        self.history_rainy_days = None
        self.history_foggy_days = None
        self.history_avg_aqi = None
        self.history_avg_temp = None

        self.weather_index = None

    def to_dict(self):
        population_total = (self.population_young or 0) + (self.population_working or 0) + (self.population_old or 0)
        population_density = None
        if self.area_km2:
            try:
                population_density = population_total / float(self.area_km2)
            except Exception:
                population_density = None

        return {
            "code": self.code,
            "name": self.name,
            "region": self.region,
            "population_young": self.population_young,
            "population_working": self.population_working,
            "population_old": self.population_old,
            "population_total": population_total,
            "area_km2": self.area_km2,
            "population_density": population_density,
            "main_demographic": self.main_demographic,
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
            "history_avg_temp" : self.history_avg_temp,
            "weather_index" : self.weather_index
        }
