class Config:
    def __init__(self) -> None:
        # Premise secrets

        self.PROJECT_NAME = "EI 3.12"
        self.SOURCE_DB = "ecoinvent-3.12-cutoff"
        self.SOURCE_VERSION = "3.12"
        self.KEY = "tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo="

        # SDF columns

        self.sdf_cols = [
            "from activity name",
            "from reference product",
            "from location",
            "from categories",
            "from database",
            "from key",
            "to activity name",
            "to reference product",
            "to location",
            "to categories",
            "to database",
            "to key",
            "flow type",
        ]

        # AD scenario parameters

        self.feed_products = [
            "alfalfa-grass silage",
            "maize silage",
            "hay",
            "barley grain",
            "maize grain",
            "oat grain",
            "wheat grain",
            "soybean",
            "wheat bran",
            "rape meal",
            "protein feed",
            "straw",
        ]

        self.primary_crop_products = [
            "alfalfa-grass silage",
            "maize grain",
            "hay",
            "barley grain",
            "maize grain",
            "oat grain",
            "wheat grain",
            "soybean",
            "rape",
            "straw",
        ]

        self.N_fertilizer_to_scale = [
            "ammonia",
            "ammonium",
            "manure",
            "nitrogen",
            "potassium nitrate",
            "market for urea",
            "packaging, for fertilisers",
            "NPK",
        ]

        self.CO2_NAME = "Carbon dioxide, fossil"
        self.CH4_NAME = "Methane, non-fossil"
        self.N2O_NAME = "Dinitrogen monoxide"

        # AM scenario parameters

        self.diesel_combustion_flows = [
            "Ammonia",
            "Benzene",
            "Benzo(a)pyrene",
            "Carbon dioxide, fossil",
            "Carbon monoxide, fossil",
            "Dinitrogen monoxide",
            "Dioxins",
            "Heat, waste",
            "Methane, fossil",
            "Nitrogen oxides",
            "NMVOC",
            "PAH",
            "Particulate Matter",
            "Sulfur dioxide",
        ]

        self.CALORIFIC_VALUE_DIESEL = 42.8  # MJ/kg

        self.CONVERSION_FACTOR_kWh_to_MJ = 3.6  # kWh/MJ

        self.efficiency_diesel_tractor = 0.35

        self.efficiency_electric_tractor = 0.85
