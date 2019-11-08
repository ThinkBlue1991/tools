import os

import psycopg2.pool

simple_conn_pool = psycopg2.pool.SimpleConnectionPool(10, 100,
                                                      database='sentry',
                                                      user='postgres',
                                                      password='123456',
                                                      host='192.168.4.91',
                                                      port='5433')


def find():
    try:
        conn = simple_conn_pool.getconn()
        cursor = conn.cursor()
        query = "SELECT identifier FROM download_image;"
        cursor.execute(query)

        results = cursor.fetchall()

        name_list = [result[0] for result in results]
        return name_list
        # print(name_list)
    except Exception as ex:
        print(ex)
        return False


if __name__ == "__main__":
    # s3_path = 's3://sentinel-s2-l1c/tiles/50/T/MK/'
    # local_path = '/mnt/volume_1/sentinel2/BJ-shunyi'
    # start = 11
    # end = start + 8
    # name_list = find()
    # if name_list:
    #     date_list = [name[start:end] for name in name_list]
    #
    #     local_date_list = list()
    #
    #     for date in date_list:
    #         if date[4] == "0":
    #             month = date[5]
    #         else:
    #             month = date[4:6]
    #         if date[6] == "0":
    #             day = date[7]
    #         else:
    #             day = date[6:8]
    #         local_date_list.append('_'.join((date[0:4], month, day)))
    #
    #     local_path_list = [os.path.join(local_path, local_date) for local_date
    #                        in local_date_list]
    #
    #     # for i in range(0, len(local_date_list)):
    #     for i in range(0, 1):
    #         s3_path_instance = os.path.join(s3_path,
    #                                         local_date_list[i].replace('_',
    #                                                                    '/'),
    #                                         '0/')
    #
    #         cmd = "aws s3 cp {0} {1} --recursive  --request-payer".format(
    #             s3_path_instance, local_path_list[i])
    #         print(cmd)
    #         os.system(cmd)
    # a = 6
    # b = 11
    # flag_a = (a > 0 and a < 10)
    # flag_b = (b > 0 and b < 10)
    # print(flag_a)
    # print(flag_b)
    # # if flag_a and flag_b: