import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('known_ip_db')

table.put_item(
    Item={
        'hostname': 'nba.com',
        'known_ips': set(['123.123.123.123', '157.166.248.245']),
        'lastnotifieddate': '2017-07-01'
     }
)

table.put_item(
    Item={
        'hostname': 'example.com',
        'known_ips': set(['2606:2800:220:1:248:1893:25c8:1946', '93.184.216.34']),
        'lastnotifieddate': '2017-07-01'
     }
)
