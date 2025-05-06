import logging

import h3

import model
from external.pg.client import PgClient
from external.web.ato.client import get_all_addresses
from logic.cron.calculate_water_parameters_task import calculate_water_parameters_task, save_coordinates, \
    save_aggregated_hexagons_information
from logic.geo.houses import dump_addresses_to_file, read_already_fetched_houses, enrich_with_hexagons, \
    retrieve_address_info
from model.geo import make_hex_id, AddressInfo, Point, Hexagon
from model.water_parameters import Parameter, WaterParameters

logging.basicConfig(level=logging.INFO)

def test_enrich_and_print():
    def enrich_and_print(addresses_and_coordinates, hex_res):
        enriched = enrich_with_hexagons(addresses_and_coordinates, hex_res)

        unique_hex_ids = {obj[make_hex_id(hex_res)] for obj in enriched}
        print(f'\nUnique hexes with hex_res = {hex_res} (len = {len(unique_hex_ids)})')
        for hex_id in unique_hex_ids:
            print(f'\t{hex_id}; hex_childrens={h3.cell_to_children(hex_id)}')


    houses = read_already_fetched_houses()
    print(houses)
    print( f'Total houses = {len(houses)}')
    enrich_and_print(houses, 6)
    enrich_and_print(houses, 7)
    # enrich_and_print(houses, 8)
    # enrich_and_print(houses, 9)

def enrich_and_save():
    addresses = get_all_addresses()
    houses = retrieve_address_info(addresses, geocoder_requests_limit=5)
    dump_addresses_to_file(houses)

def test_avg_parameters():
    calculate_water_parameters_task()

def test_pg_client_select_address_info():
    pg_client = PgClient()
    target = 'Республика Беларусь, г.Минск, Газеты Звязда просп., 42'
    address_info: AddressInfo = pg_client.get_address_info(target)
    assert address_info.address == target
    assert address_info.coordinates == Point(latitude=53.86037, longitude=27.46016)
    assert address_info.water_parameters.smell == Parameter('Запах', 'баллы', 1.5, 2.0)
    assert address_info.water_parameters.taste == Parameter('Привкус', 'баллы', 1.2, 2.0)
    assert address_info.water_parameters.color == Parameter('Цветность', 'градусы', 0.8, 1.5)
    assert address_info.water_parameters.muddiness == Parameter('Мутность', 'мг/дм3', 0.5, 1.0)
    assert address_info.water_parameters.general_mineralization == Parameter('Общая минерализация  ***', 'мг/дм3', 150, 200)

def test_pg_client_select_hex_info():
    pg_client = PgClient()
    target = '871f4e143ffffff'
    hexagon: Hexagon = pg_client.get_info_about_hex(target)
    assert hexagon.hex_id == target
    assert hexagon.hex_resolution == h3.get_resolution(target)
    assert hexagon.hex_color == (148,211,31)
    assert hexagon.avg_water_parameters.smell == Parameter('Запах', 'баллы', 1.5, 2.0)
    assert hexagon.avg_water_parameters.taste == Parameter('Привкус', 'баллы', 1.2, 2.0)
    assert hexagon.avg_water_parameters.color == Parameter('Цветность', 'градусы', 0.8, 1.5)
    assert hexagon.avg_water_parameters.muddiness == Parameter('Мутность', 'мг/дм3', 0.5, 1.0)
    assert hexagon.avg_water_parameters.general_mineralization == Parameter('Общая минерализация  ***', 'мг/дм3', 150, 200)

def test_pg_client_select_all_hexes():
    pg_client = PgClient()
    hexagons: list[Hexagon] = pg_client.get_all_hexes_with_res(7)

    hexagon = hexagons[0]
    target = '871f4e143ffffff'
    assert hexagon.hex_id == target
    assert hexagon.hex_resolution == h3.get_resolution(target)
    assert hexagon.hex_color == (148,211,31)
    assert hexagon.avg_water_parameters.smell == Parameter('Запах', 'баллы', 1.5, 2.0)
    assert hexagon.avg_water_parameters.taste == Parameter('Привкус', 'баллы', 1.2, 2.0)
    assert hexagon.avg_water_parameters.color == Parameter('Цветность', 'градусы', 0.8, 1.5)
    assert hexagon.avg_water_parameters.muddiness == Parameter('Мутность', 'мг/дм3', 0.5, 1.0)
    assert hexagon.avg_water_parameters.general_mineralization == Parameter('Общая минерализация  ***', 'мг/дм3', 150, 200)

    hexagon = hexagons[1]
    target = '871f4e14effffff'
    assert hexagon.hex_id == target
    assert hexagon.hex_resolution == h3.get_resolution(target)
    assert hexagon.hex_color == (148,211,31)

def test_pg_client_insert_hex():
    pg_client = PgClient()
    pg_client.insert_hexagon(
        '8711a0d80ffffff',
        (123, 123, 123),
        WaterParameters(
            smell=Parameter('Запах', 'баллы', 1.5, 2.0),
            taste=Parameter('Привкус', 'баллы', 1.2, 2.0),
            color=Parameter('Цветность', 'градусы', 0.8, 1.5),
            muddiness=Parameter('Мутность', 'мг/дм3', 0.5, 1.0),
            general_mineralization=Parameter('Общая минерализация  ***', 'мг/дм3', 150, 200),
        ))

def test_pg_client_insert_address_info():
    pg_client = PgClient()
    pg_client.insert_address_info(
        'Республика Беларусь, г. Минск, Краснозвездная ул., 14А/6',
        Point(latitude=53.908092, longitude=27.588861),
        None
    )

def test_pg_client_select_all_available_address_info():
    pg_client = PgClient()
    res = pg_client.get_all_address_info()
    assert len(res) == 12

if __name__ == "__main__":
    # test_pg_client_select_address_info()
    # test_pg_client_select_hex_info()
    # test_pg_client_select_all_hexes()
    # test_pg_client_select_all_available_address_info()
    # enrich_and_save()
    # #
    # calculate_water_parameters_task
    # save_coordinates()
    save_aggregated_hexagons_information()

    # test_pg_client_insert_hex()
    # test_pg_client_insert_address_info()
    # test_avg_parameters()

# h3_cell = client.hexagon(address, hex_res)
# nearby_house = client.hexagon_to_nearby_house(h3_cell)
#
# print(coordinates.latitude, ";", coordinates.longitude)
# print(h3_cell)
# print(nearby_house)
#
# client = MinskVodokanalClient()
# print(client.v1_request("Леонида Звезды 42"))
#
# pg_client = PgClient()
# print(pg_client.get_hex("891fb466257ffff"))
