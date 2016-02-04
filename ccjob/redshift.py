import psycopg2
import sys
import os

def upload2redshift(column_name_type, port=5439):

    # `raw_input` is input in Python 3
    if sys.version_info.major == 2:
        input = raw_input

    endpoint = input("Redshift Endpoint: ")
    user = input("Redshift Username: ")
    pw = input("Redshift Password: ")
    dbname = input("Redshift Database Name: ")
    table_name = input("Redshift Table Name: ")

    aws_key = os.getenv("AWS_ACCESS_KEY") or input("AWS_ACCESS_KEY: ")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY") or input("AWS_SECRET_ACCESS_KEY")

    s3_bucket = input("S3 Output Bucket: ")

    conn = psycopg2.connect(
        host=endpoint,
        user=user,
        port=port,
        password=pw,
        dbname=dbname
    )

    cur = conn.cursor()
    columns = ",".join(column_name_type)
    upload = "CREATE TABLE %s (%s); COPY %s FROM \'%s\' CREDENTIALS \'aws_access_key_id=%s;aws_secret_access_key=%s\'" % (table_name, columns, table_name, s3_bucket, aws_key, aws_secret)
    upload = upload + " DELIMITER '\t' region 'us-east-1' TRUNCATECOLUMNS REMOVEQUOTES;"
    cur.execute(upload)
    cur2 = conn.cursor()
    cur2.execute("select query, trim(filename) as file, curtime as updated from stl_load_commits where query = pg_last_copy_id();")
    print("Result of upload:", cur2.fetchall())
    cur2.execute("SELECT * FROM %s LIMIT 10;" % (table_name))
    print("First 10 rows:", cur2.fetchall())
