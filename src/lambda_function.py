import os
import json
import boto3
import base64


MAX_BYTES = 400_000
table = boto3.resource('dynamodb').Table(os.environ["TABLE_NAME"])

def respond(body, status=200):
    return {
        'statusCode': status,
        'headers': {
            "content-type": "application/json; charset=utf-8",
            "cache-control": "no-store"
        },
        'body': body if isinstance(body, str) else json.dumps(body),
    }

def lambda_handler(event, context):
    email = 'solo'
    method = event['requestContext']['http']['method']

    if method == 'GET':
        item = table.get_item(Key={"email": email}).get("Item")
        return respond(item["state"] if item else "null")

    if method == 'PUT':
        body = event.get('body') or ""
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode("utf-8")
        if len(body.encode("utf-8")) > MAX_BYTES:
            return respond({"error": "Payload too large"}, 413)
        try:
            json.loads(body)
        except ValueError:
            return respond({"error": "Body is not valid JSON"}, 400)
        table.put_item(Item={"email": email, "state": body})
        return respond({"ok": True})

    return respond({"error": "Method not allowed"}, 405)
