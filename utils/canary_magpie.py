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
from datetime import datetime as dt

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

def get_display_status(client_name):
    query = "SELECT count_pageviews, pixel_orders, ts FROM bazaar_internal_client.nasa_tracking WHERE LOWER(client) = '{}' AND ts >= to_unixtime(current_date - interval '5' day) ORDER BY ts DESC LIMIT 5".format(client_name)
    # print(query)
    conn = create_connection()
    # app.logger.info("executing query...\n%s", query)
    main_object_return = {
        'display_status': '',
        'pixel_status': ''
    }
    display_object_return = {
        'failed_dates': '',
        'failed_pageview_counts': '',
        'avg_pageviews': ''
    }
    pixel_object_return = {
        'failed_dates': '',
        'failed_pixel_orders': '',
        'pixel_orders_daily_avg': ''
    }
    try:
        # Ask pandas to read the query results into a DataFrame for us.
        df = read_sql_query(query, conn)
        result_data = df.to_dict()
        # Get pageview data and check stDeviation
        pageviews = list(result_data['count_pageviews'].values())
        timestamps = list(result_data['ts'].values())
        if any(elem is None for elem in pageviews):
            display_status = 'fail'
        else:
            stdev_pageviews = statistics.stdev(pageviews)
            avg_pageviews = statistics.mean(pageviews)
            display_object_return['avg_pageviews'] = avg_pageviews
            # Find diff of daily pageviews to avg pageviews
            pageviews_diff = [pageview - avg_pageviews for pageview in pageviews]
            # Find pageviews where the standard deviation is greater than 2x
            # Or less than a floor of 15 pageviews
            display_status = 'pass'
            fail_ts = []
            pg_fail_count = []
            for pg_diff in pageviews_diff:
                # Set standard deviation of 1x for Hackathon so we can see fails
                if (abs(pg_diff) > (stdev_pageviews * 2)) or (abs(pg_diff) < 15):
                    display_status = 'fail'
                    fail_ts.append(timestamps[pageviews_diff.index(pg_diff)])
                    pg_fail_count.append(pageviews[pageviews_diff.index(pg_diff)])

            fail_dt = [dt.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in fail_ts]
            display_object_return['failed_dates'] = fail_dt
            display_object_return['failed_pageview_counts'] = pg_fail_count

        # Get pixel data and check stDeviation
        pixel_orders = list(result_data['pixel_orders'].values())
        stdev_pixel = statistics.stdev(pixel_orders)
        avg_pixel = statistics.mean(pixel_orders)
        pixel_object_return['pixel_orders_daily_avg'] = round(avg_pixel)

        # Find diff of daily orders to avg orders
        orders_diff = [orders - avg_pixel for orders in pixel_orders]
        # Find orders where the standard deviation is greater than 2x
        # Or less than a floor of 15 orders
        pixel_status = 'pass'
        pixel_fail_ts = []
        pixel_fail_count = []
        for order_diff in orders_diff:
            # Set standard deviation of 1x for Hackathon so we can see fails
            if (abs(order_diff) > (stdev_pixel * 2)) or (order_diff == 0):
                pixel_status = 'fail'
                pixel_fail_ts.append(timestamps[orders_diff.index(order_diff)])
                pixel_fail_count.append(pixel_orders[orders_diff.index(order_diff)])

        pixel_fail_dt = [dt.fromtimestamp(pts).strftime("%Y-%m-%d") for pts in pixel_fail_ts]
        pixel_object_return['failed_dates'] = pixel_fail_dt
        pixel_object_return['failed_pixel_orders'] = pixel_fail_count

    except DatabaseError as e:
        # app.logger.exception("failed to execute query!")
        return str(e)
    finally:
        # Always clean up after yourself!
        # app.logger.debug("closing connection...")
        conn.close()

    return [display_status, display_object_return], [pixel_status, pixel_object_return]


# if __name__ == "__main__":
#     get_status(client_name)
