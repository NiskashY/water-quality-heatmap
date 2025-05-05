import logging
import time
from typing import Optional

import psycopg2
from psycopg2.extras import register_composite

from external.config.pg_config import PgConfig, read_pg_config
from model.geo import Hexagon, AddressInfo, Point
from model.water_parameters import WaterParameters, Parameter


def _register_custom_types(conn):
    register_composite("parameter", conn)
    register_composite("water_parameters", conn)  # без этого не распарсим
    register_composite("color", conn)
    register_composite("geo_point", conn)


class PgClient:
    __pg_settings: PgConfig = read_pg_config()

    def __get_db_connection(self):
        return psycopg2.connect(
            dbname=self.__pg_settings.dbname,
            user=self.__pg_settings.username,
            password=self.__pg_settings.password,
        )

    def __select_query(self, query: str, *kwargs):
        conn = None
        try:
            logging.debug("Starting conn for SELECT")
            conn = self.__get_db_connection()
            _register_custom_types(conn)

            with conn.cursor() as cursor:
                cursor.execute(query, (*kwargs,),)
                result = cursor.fetchall()
                return result
        except Exception as e:
            logging.error(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
                logging.debug("Connection for select closed")

    def get_address_info(self, address: str) -> Optional[AddressInfo]:
        query = "SELECT created_at, address, coordinates, water_parameters FROM address_info WHERE address = %s"
        result = self.__select_query(query, address)
        assert len(result) < 2
        return _parse_address_info(result[0]) if result else None


    def get_info_about_hex(self, hex_id: str) -> Optional[Hexagon]:
        query = "SELECT created_at, hex_id, hex_resolution, hex_color, avg_water_parameters FROM hexagons WHERE hex_id = %s"
        result = self.__select_query(query, hex_id)
        return _parse_hexagon(result[0]) if result else None

    def get_all_hexes_with_res(self, hex_resolution: int) -> list[Hexagon]:
        query = "SELECT created_at, hex_id, hex_resolution, hex_color, avg_water_parameters FROM hexagons WHERE hex_resolution = %s"
        result = self.__select_query(query, hex_resolution)
        return [_parse_hexagon(res) for res in result]

    def insert(
        self,
        hex_id: str,
        hex_color: str,
        water_parameters: WaterParameters,
    ):
        conn = None
        try:
            logging.info("Starting conn for INSERT")
            conn = self.__get_db_connection()
            _register_custom_types(conn)

            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO hexagons (hex_id, created_at, water_parameters)
                    VALUES (%s, %s, ROW(%s, %s, %s, %s, %s)::water_parameters)
                    """,
                    (
                        hex_id,
                        int(time.time()),
                        hex_color,
                        _get_tuple(water_parameters.smell),
                        _get_tuple(water_parameters.taste),
                        _get_tuple(water_parameters.color),
                        _get_tuple(water_parameters.muddiness),
                        _get_tuple(water_parameters.general_mineralization),
                    ),
                )
                conn.commit()
        except Exception as e:
            logging.WARN(f"Insertion error occurred {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                logging.info("Connection for insert closed")

def _parse_tuple(s: str) -> tuple[int, int, int]:
    x, y, z = s.strip("()").split(",")
    return int(x), int(y), int(z)


def _parse_parameter(name, units, value, max_allowed_concentration):
    return Parameter(name, units, float(value), float(max_allowed_concentration))

def _parse_water_params(db_water_params) -> WaterParameters:
    return WaterParameters(
            smell=_parse_parameter(*db_water_params[0]),
            taste=_parse_parameter(*db_water_params[1]),
            color=_parse_parameter(*db_water_params[2]),
            muddiness=_parse_parameter(*db_water_params[3]),
            general_mineralization=_parse_parameter(*db_water_params[4]),
        )

def _parse_hexagon(db_row) -> Hexagon:
    created_at, hex_id, hex_resolution, hex_color, water_params = db_row
    return Hexagon(
        created_at=created_at,
        hex_id=hex_id,
        hex_resolution=hex_resolution,
        hex_color=_parse_tuple(hex_color),
        avg_water_parameters=_parse_water_params(water_params)
    )

def _parse_address_info(db_row) -> AddressInfo:
    created_at, address, coordinates, water_params = db_row
    return AddressInfo(
        created_at=created_at,
        address=address,
        coordinates=Point(latitude=float(coordinates[0]), longitude=float(coordinates[1])),
        water_parameters=_parse_water_params(water_params)
    )


def _get_tuple(param: Parameter):
    return param.name, param.units, param.value, param.max_allowed_concentration
