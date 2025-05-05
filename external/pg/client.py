import logging
import time
from typing import Optional

import psycopg2

from psycopg2.extras import register_composite
from model.geo import Hexagon
from model.water_parameters import WaterParameters, Parameter
from external.config.pg_config import PgConfig, read_pg_config


def _register_custom_types(conn):
    register_composite("parameter", conn)
    register_composite("water_parameters", conn)  # без этого не распарсим


class PgClient:
    __pg_settings: PgConfig = read_pg_config()

    def __get_db_connection(self):
        return psycopg2.connect(
            dbname=self.__pg_settings.dbname,
            user=self.__pg_settings.username,
            password=self.__pg_settings.password,
        )

    def get_hex(
        self,
        hex_id: str,
    ) -> Optional[Hexagon]:
        conn = None
        try:
            logging.info("Starting conn for SELECT")
            conn = self.__get_db_connection()
            _register_custom_types(conn)

            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT hex_id, created_at, hex_color, water_parameters FROM hexagons WHERE hex_id = %s",
                    (hex_id,),
                )
                result = cursor.fetchone()

                if result:
                    return _parse_hexagon(result)

            return None

        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
                logging.info("Connection for select closed")

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
            __register_custom_types(conn)

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


def _parse_hexagon(db_row) -> Hexagon:
    hex_id, created_at, hex_color, water_params = db_row
    return Hexagon(
        hex_id=hex_id,
        created_at=created_at,
        hex_color=hex_color,
        water_parameters=WaterParameters(
            smell=Parameter(*water_params[0]),
            taste=Parameter(*water_params[1]),
            color=Parameter(*water_params[2]),
            muddiness=Parameter(*water_params[3]),
            general_mineralization=Parameter(*water_params[4]),
        ),
    )


def _get_tuple(param: Parameter):
    return param.name, param.units, param.value, param.max_allowed_concentration
