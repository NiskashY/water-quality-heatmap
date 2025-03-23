from dataclasses import dataclass


@dataclass
class Parameter:
    name: str
    units: str  # units represented in russian language
    value: float
    max_allowed_concentration: float


@dataclass
class WaterParameters:
    smell: Parameter
    taste: Parameter
    color: Parameter
    muddiness: Parameter  # мутность
    general_mineralization: Parameter
    # rigidity: Parameter  # жесткость
    # water_gene_indicator: Parameter  # Водородный показатель
    # fe_sum: Parameter  # железо Fe (суммарно)
    # mn_sum: Parameter  # марганец Mn (сумамарно)
    # ammonia: Parameter  # Аммиаак (по азоту)
    # no2: Parameter  # Нитриты
    # no3: Parameter  # Нитраты
    # chloride: Parameter  # Хлориды CI
    # petroleum_products: Parameter  # Нетфепродукты
    # surface_active_substances: Parameter  # Поверхностно активные вещества
    # sulfates: Parameter  # Сульфаты SO4
    # chlorine_total_suffered: Parameter  # Хлор суммарный остатончый
