import colorsys

from model.water_parameters import WaterParameters

# Нормализованные значения параметров (0.0 - 1.0)
# Берём максимальное отклонение среди всех параметров
# Ограничиваем максимальное отклонение 1.0
# Преобразуем отклонение в цвет:
# 0.0 (0%) - зелёный (120° в HSV), 1.0 (100%) - красный (0° в HSV)
# Конвертируем HSV в RGB
def determine_color(water_params: WaterParameters):
    if water_params is None:
        return 184, 183, 174 # grey color

    norm_smell = water_params.smell.norm()
    norm_mineral = water_params.general_mineralization.norm()
    norm_color = water_params.color.norm()
    norm_taste = water_params.taste.norm()
    norm_muddiness = water_params.muddiness.norm()

    max_deviation = max(norm_smell, norm_mineral, norm_color, norm_taste, norm_muddiness)

    max_deviation = min(max_deviation, 1.0)

    hue = (1.0 - max_deviation) * 120.0 / 360.0

    # Фиксированные насыщенность и яркость
    saturation = 0.9
    value = 0.9

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return r, g, b