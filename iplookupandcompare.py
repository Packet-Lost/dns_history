import boto3
import socket
import datetime

definedhostname = 'example.com'
region = 'us-east-1'
snstopicarn = 'arn:aws:sns:us-east-1:444455556666:MyTopic'
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('known_ip_db')


def lambda_handler(event, context):
    #lookup all returning ips from the hostname both ipv4 and ipv6
    resolvedips = list( map( lambda x: x[4][0], socket.getaddrinfo(definedhostname, 80, type=socket.SOCK_STREAM)))
    print("The IPs returned from making a connection to {} were {}".format(definedhostname, resolvedips))

    #query documented past IPs from dynamo and display them in print log output
    knownips = getknownipsfromdynamo()
    print("{} are the stored previous ip addresses of {}".format(knownips, definedhostname))

    newlydiscoveredips = set()

    #iterate through all returned ips, only take possible action on verified valid IPs
    for ip in resolvedips:
        if validipcheck(ip):
            if ip in knownips:
                print("{} is an already known host IP address of {}".format(ip, definedhostname))
            else:
                print("{} is not found in known host IP addresses of {} and will be added to the update set".format(ip, definedhostname))
                newlydiscoveredips.add(ip)
        else:
            print("Skipping {} as it failed valid ip check".format(ip))

    #if new ips are found we are updating the list in dynamo with one call and conditionally notifying an SNS topic
    if newlydiscoveredips:
        print("New IPs were discovered and will be added to database")
        newlydiscoveredips.update(knownips)
        print ("The new list of known ips for {} will be updated to {}".format(definedhostname, newlydiscoveredips))
        updatedynamohostiplist(newlydiscoveredips)
        lastnotification = getlastnotifieddate()
        print ("Last Notification was sent on {}".format(lastnotification))
        if lastnotification == datetime.date.today().strftime('%Y-%m-%d'):
            print("Alert was already sent today, will not notify again until tomorrow.")
        else:
            sns = boto3.client('sns', region_name=region)
            sns.publish(TopicArn=snstopicarn,
                        Subject='DNS History for a {} was updated'.format(definedhostname),
                        Message='New IPs found for {}, the documented IPs are now {}'
                                'This email message only fires once per day, '
                                'per polled URL'.format(definedhostname, newlydiscoveredips))
            updatelastnotifieddate(datetime.date.today().strftime('%Y-%m-%d'))
    else:
        print("No new valid IP addresses discovered for {}".format(definedhostname))

#will attempt to check ip addresses for validity, both ipv4 and ipv6
def validipcheck(addr):
    print("Checking to see if {} is a valid IP... ".format(addr))
    try:
        socket.inet_aton(addr)
        print("{} is a valid IPv4 IP".format(addr))
        return True
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, addr)
            print("{} is a valid IPv6 IP".format(addr))
            return True
        except socket.error:
            return False
        print("{} is not a valid IPv4 or IPv6 IP Address".format(addr))
        return False

def getknownipsfromdynamo():
    response = table.get_item(Key={'hostname': definedhostname})
    return response['Item']['known_ips']

def updatedynamohostiplist(newiplist):
    table.update_item(
        Key={
            'hostname': definedhostname
        },
        UpdateExpression='SET known_ips = :val1',
        ExpressionAttributeValues={
            ':val1': set(newiplist)
        }
    )

def getlastnotifieddate():
    response = table.get_item(Key={'hostname': definedhostname})
    return response['Item']['lastnotifieddate']

def updatelastnotifieddate(newdatestring):
    table.update_item(
        Key={
            'hostname': definedhostname
        },
        UpdateExpression='SET lastnotifieddate = :val1',
        ExpressionAttributeValues={
            ':val1': newdatestring
        }
    )

#this is for running/iterating in local python environments
#lambda_handler("testevent","datapoint")