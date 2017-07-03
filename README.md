# DNS History for AWS Lambda

Lambda function with dynamodb backend to maintain history of IP addresses returned for third party hosted DNS records

# Ideas for future improvements / roadmap

Finish SNS topic integration with string replacement in published messages, more options for notifications, how often, how many per day etc.

Possibly tie this in with API gateway and give it a web front end which would open up the possibility of better functoinality such as making it easy to add new urls to poll, view hostname history without knowing how to query dynamodb, etc

Deploy end project with cloudformation




