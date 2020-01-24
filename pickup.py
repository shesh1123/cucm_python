#!/usr/bin/python3
from os.path import abspath
from suds.client import Client
from urllib.parse import urljoin
from urllib.request import pathname2url
import argparse
import ssl
import suds



parser = argparse.ArgumentParser(description="This programs can be used to extract the Pick-Up-Group using Directory Number.")
parser.add_argument("-dn", type=str, help="Directory Number(s)", nargs='*',default='' )
parser.add_argument("-pkg", type=str, help="Enter pick up group", nargs='*',default='' )
parser.add_argument("-update", help="Update pickup group",action="store_true" )
args = parser.parse_args()


WSDL = urljoin('file:', pathname2url('/home/shesh/script/schema/current/AXLAPI.wsdl'))

# Allow insecure connections
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

CLIENT = Client(WSDL, location='https://%s:8443/axl/' % ('10.10.10.10'),
                username='test', password='test')

#To get pickup group from DN
def get_pickup_group(dn):
    try:
        response = CLIENT.service.listLine(
                    searchCriteria={
                        'pattern': dn
                                   },
                returnedTags={
                    'callPickupGroupName':True
                })
        print(dn,response['return'].line[0].callPickupGroupName.value)
    except Exception:
        print(dn,'All alone in this world !!! ')


#To get pickup group members
def get_pickup_group_members(pickup_grp):
    sql = '''select numplan.dnorpattern from numplan, pickupgrouplinemap, pickupgroup
            where numplan.pkid = pickupgrouplinemap.fknumplan_line and
            pickupgrouplinemap.fkpickupgroup = pickupgroup.pkid and
            pickupgroup.name = \'%s\''''%pickup_grp[0].upper()
    try:
        resp = CLIENT.service.executeSQLQuery(sql)
    except Fault as err:
        print('Error: executeSQLQuery: {err}'.format( err = err ) )

    print( 'Directory Numbers belonging to %s'%pickup_grp[0] )
    print( '==================================================')
    if resp['return']:
        for rowXml in resp[ 'return' ][ 'row' ]:
            print(rowXml[0])
    else:
        print("No DN in this pick up group")

#Update pickup group
def update_pickupgroup():
    pickup_grp=input("Enter pickup group: ")
    num=input("Enter list of DN separated by space : ")
    num_list=num.split()
    if isinstance(num_list,str):
        try:
            resp = CLIENT.service.updateLine(pattern = dn, callPickupGroupName = pickup_grp )
            print( '\nUpdate pickup group response:\n', resp )
        except suds.WebFault as err:
            print(err)
    else:
        for dn in num_list:
            try:
                resp = CLIENT.service.updateLine(pattern = dn, callPickupGroupName = pickup_grp )
                print( '\nUpdate pickup group response:\n', resp )
            except suds.WebFault as err:
                print(err)

if args.dn:
    if isinstance(args.dn,str):
        get_pickup_group(args.dn)
    else:
        for i in args.dn:
            get_pickup_group(i)
elif args.pkg:
    get_pickup_group_members(args.pkg)
elif args.update:
    update_pickupgroup()
