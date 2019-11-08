import psycopg2.pool

"""
[DB_POSTGRESQL]
DATABASE = gv_place
USER = postgres
PASSWORD = 123456
HOST = 192.168.4.32
PORT = 5432
MAX_CONN = 200
MIN_CONN = 5
CITY_TABLE = city
LIMIT_SIZE = 10
"""
database = parse_config.get_config("DB_POSTGRESQL", "DATABASE")
user = parse_config.get_config("DB_POSTGRESQL", "USER")
password = parse_config.get_config("DB_POSTGRESQL", "PASSWORD")
host = parse_config.get_config("DB_POSTGRESQL", "HOST")
port = parse_config.get_config("DB_POSTGRESQL", "PORT")
max_conn = int(parse_config.get_config("DB_POSTGRESQL", "MAX_CONN"))
min_conn = int(parse_config.get_config("DB_POSTGRESQL", "MIN_CONN"))
table = parse_config.get_config("DB_POSTGRESQL", "CITY_TABLE")
limit_size = int(parse_config.get_config("DB_POSTGRESQL", "LIMIT_SIZE"))



simple_conn_pool = psycopg2.pool.SimpleConnectionPool(min_conn, max_conn,
                                                      database=database,
                                                      user=user,
                                                      password=password,
                                                      host=host, port=port)
													  
													  
													  
													  def find_place(place_name, is_dim):
    """查找地名区域

    Args:
        place_name:地名
        is_dim： 是否模糊查询

    Returns:

        geojson: 地名区域

    """

    try:
        conn = simple_conn_pool.getconn()
        cursor = conn.cursor()
        check_formula = re.compile(
            r';|\*|\.|%|=|\?|/|\+|\\|\'|and|exec|insert|select|delete|update|'
            r'count|or|from|drop|grant|alter|chr|mid|master|trancate|char|'
            r'declare|where|union|into|substr|ascii|execute')
        check_result = check_formula.search(place_name)
        if not check_result:
            if is_dim:
                query = "SELECT name FROM \"%s\"  WHERE \"name\" LIKE '%%%s%%' " \
                        "ORDER BY \"gid\" LIMIT %d" % (
                            table, place_name, limit_size)
            else:
                query = "SELECT ST_AsGeoJSON(\"geom\") FROM \"%s\"  " \
                        "WHERE \"name\" = '%s' ORDER BY \"gid\" LIMIT 1;" % (
                            table, place_name)

            cursor.execute(query)

            results = cursor.fetchall()

            if results:
                if is_dim:
                    return True, 0, [result[0] for result in results]
                else:
                    data = json.loads(results[0][0])
                    data['coordinates'] = data['coordinates'][0]

                    if data['type'].lower().find('polygon'):
                        data['type'] = 'Polygon'

                    if data['type'].lower().find('point'):
                        data['type'] = 'Point'

                    return True, 0, data
            else:
                message = "No data was found"
                return False, 1, message
        else:
            message = "Name format error"
            return False, 1, message

    except Exception as ex:
        print(ex)
        message = "Server error"
        return False, 2, message
    finally:
        cursor.close()
        simple_conn_pool.putconn(conn, close=False)