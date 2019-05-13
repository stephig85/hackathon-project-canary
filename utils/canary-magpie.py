from concurrent.futures import as_completed
from os import environ
from time import time
import boto3
import sys
import statistics
from pandas import DataFrame, read_sql_query
from pandas.io.sql import DatabaseError
from pyathena import connect
from pyathena.async_cursor import AsyncCursor
import json
from datetime import datetime

AWS_REGION = environ.get("AWS_REGION", "us-east-1")
BV_NEXUS_ACCOUNT = "774013277495"
IS_DEPLOYED = environ.get("BVFLYNN_VPC") is not None

ATHENA_BUCKET = "s3://aws-athena-query-results-{}-{}/".format(BV_NEXUS_ACCOUNT, AWS_REGION)
sts_client = boto3.client("sts")

def get_raven_athena_credentials():
    # When the app is deployed (e.g. to flynn or an EC2 instance), assume the Raven-Athena role. When the app is not
    # deployed (i.e. running locally), allow the app to use the developer's credentials (e.g. from ~/.aws/credentials)
    # by returning no access key and no session token.
    # https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
    credentials = {"AccessKeyId": None, "SecretAccessKey": None, "SessionToken": None}
    if IS_DEPLOYED:
        role_arn = "arn:aws:iam::{}:role/Raven-Athena".format(BV_NEXUS_ACCOUNT)
        # The session name isn't really important so long as it is reasonably descriptive and is unique per session.
        role_session_name = APP_NAME + str(time())
        assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name)
        credentials = assumed_role["Credentials"]
    return credentials

def create_connection():
    # Create a database connection based on all of the environment information set above.
    # app.logger.info("creating connection...")
    aws_credentials = get_raven_athena_credentials()
    return connect(
        s3_staging_dir=ATHENA_BUCKET,
        region_name=AWS_REGION,
        aws_access_key_id=aws_credentials["AccessKeyId"],
        aws_secret_access_key=aws_credentials["SecretAccessKey"],
        aws_session_token=aws_credentials["SessionToken"],
    )

def get_status():
    client_name = sys.argv[1] if sys.argv[1] else None

    query = "SELECT count_pageviews, pixel_orders, ts FROM bazaar_internal_client.nasa_tracking WHERE LOWER(client) = '{}' AND ts >= to_unixtime(current_date - interval '10' day) ORDER BY ts DESC LIMIT 10".format(client_name)
    # print(query)
    conn = create_connection()
    # app.logger.info("executing query...\n%s", query)
    main_object_return = {
        'failed_dates': ''
    }
    try:
        # Ask pandas to read the query results into a DataFrame for us.
        df = read_sql_query(query, conn)
        result_data = df.to_dict()
        pageviews = list(result_data['count_pageviews'].values())
        timestamps = list(result_data['ts'].values())
        stdev_pageviews = statistics.stdev(pageviews)
        avg_pageviews = statistics.mean(pageviews)
        # Find diff of daily pageviews to avg pageviews
        pageviews_diff = [pageview - avg_pageviews for pageview in pageviews]
        # Find pageviews where the standard deviation is greater than 2x
        # Or less than a floor of 15 pageviews
        display_status = ('pass')
        fail_ts = []
        for pg_diff in pageviews_diff:
            if abs(pg_diff) > (stdev_pageviews * 2):
                display_status = 'fail'
                fail_ts.append(timestamps[pageviews_diff.index(pg_diff)])
            elif abs(pg_diff) < 15:
                display_status = 'fail'
                fail_ts.append(timestamps[pageviews_diff.index(pg_diff)])

        fail_dt = [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in fail_ts]
        main_object_return['failed_dates'] = fail_dt
        # pixel = list(result_data['pixel_orders'].values())
        # stdev_pixel = statistics.stdev(pixel)
        # avg_pixel = statistics.mean(pixel)

    except DatabaseError as e:
        # app.logger.exception("failed to execute query!")
        final_return_object = str(e)
    finally:
        # Always clean up after yourself!
        # app.logger.debug("closing connection...")
        conn.close()

    final_return_object = [display_status, main_object_return]
    print(final_return_object)
    return final_return_object


if __name__ == "__main__":
    get_status()
