import time
import datetime
import pytz
import numpy
import random
import pandas as pd
import gzip
import sys
import argparse
from faker import Faker
from tzlocal import get_localzone

local = get_localzone()


# todo:
# allow writing different patterns (Common Log, Apache Error log etc)
# log rotation


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        try:
            yield self.match
        except StopIteration:
            return

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


# ----------------------------------------------------------------------------------
# Product
dfp = pd.read_csv("Products.csv")
lst_prod_prob = dfp["Probability"]
lst_prod_id = dfp["prod_id"]

# Customer
dfc = pd.read_csv("Customers.csv")
list_cust_prob = dfc["Probability"]
lst_cust_id = dfc["Cust_id"]
# ----------------------------------------------------------------------------------

parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
parser.add_argument("--output", "-o", dest='output_type', help="Write to a Log file, a gzip file or to STDOUT",
                    choices=['LOG', 'GZ', 'CONSOLE'])
parser.add_argument("--log-format", "-l", dest='log_format', help="Log format, Common or Extended Log Format ",
                    choices=['CLF', 'ELF'], default="ELF")
parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int,
                    default=1)
parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str)
parser.add_argument("--sleep", "-s", help="Sleep this long between lines (in seconds)", default=0.0, type=float)

args = parser.parse_args()

log_lines = args.num_lines
file_prefix = args.file_prefix
output_type = args.output_type
log_format = args.log_format

faker = Faker()

# timestr = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(30), "%Y%m%d-%H%M%S")


timestr = time.strftime("%Y%m%d-%H%M%S")
otime = datetime.datetime.now()

outFileName = 'orders_log_' + timestr + '.log' if not file_prefix else file_prefix + '_access_log_' + timestr + '.log'

for case in switch(output_type):
    if case('LOG'):
        f = open(outFileName, 'w')
        break
    if case('GZ'):
        f = gzip.open(outFileName + '.gz', 'w')
        break
    if case('CONSOLE'): pass
    if case():
        f = sys.stdout

response = ["200", "404", "500", "301"]

verb = ["GET", "POST"]

# resources = ["/user/register", "/user/login", "/wp-content", "/wp-admin", "/explore", "/search/tag/list",
#              "/app/main/posts",
#              "/posts/posts/explore", "/apps/cart.jsp?appID="]
resources = ["/app/cart " , "/app/orders "]

ualist = [faker.firefox, faker.chrome, faker.safari, faker.internet_explorer, faker.opera]

flag = True
while flag:
    if args.sleep:
        increment = datetime.timedelta(seconds=args.sleep)
    else:
        increment = datetime.timedelta(seconds=random.randint(5, 10))
    otime += increment

    ip = faker.ipv4_public(network=False, address_class=None)
    dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
    tz = datetime.datetime.now(local).strftime('%z')
    vrb = numpy.random.choice(verb, p=[0.75, 0.25])

    uri = random.choice(resources)
    if uri.find("apps") > 0:
        uri += str(random.randint(1000, 10000))
    # ---------------------------------------------------------------------------------
    # customer details
    cust_id = numpy.random.choice(lst_cust_id, p=list_cust_prob)
    cust_details = dfc.iloc[cust_id, :].to_list()
    cust_nm = cust_details[4]
    gen = cust_details[5]
    age = cust_details[2]

    # product details
    prod_id = numpy.random.choice(lst_prod_id, p=lst_prod_prob)
    prod_details = dfp.iloc[prod_id, :].to_list()
    prod_name = prod_details[1]
    prod_category = prod_details[2]
    prod_price = prod_details[3]
    currency = "USD"
    # ---------------------------------------------------------------------------------

    resp = numpy.random.choice(response, p=[0.9, 0.04, 0.02, 0.04])
    byt = int(random.gauss(5000, 50))
    referer = "https://www.trunaamm.com/" #faker.uri()
    useragent = numpy.random.choice(ualist, p=[0.5, 0.3, 0.1, 0.05, 0.05])()
    if log_format == "CLF":
        f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s\n' % (ip, dt, tz, vrb, uri, resp, byt))
    elif log_format == "ELF":
        f.write(
            '%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s" %s "%s" %s %s %s "%s" "%s" %s \n' % (
             ip, dt, tz, vrb, uri, resp, byt,
            referer, useragent,cust_id, cust_nm, gen, age, prod_id, prod_name, prod_category, prod_price))
    f.flush()

    log_lines = log_lines - 1
    flag = False if log_lines == 0 else True
    if args.sleep:
        time.sleep(args.sleep)
