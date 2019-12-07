import os
import json
import boto3
import logging
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb') 
table_name = os.environ["DYNAMO_TABLE_NAME"]
dynamotable = dynamodb.Table(table_name)

click_type_yes = os.environ["CLICK_TYPE_YES"]
click_type_no  = os.environ["CLICK_TYPE_NO"]
click_type_end = os.environ["CLICK_TYPE_END"]

iot_publish_topic = os.environ["IOT_TOPIC"]

def lambda_handler(event, context):
    
    click_type = save_answer(event)
    if click_type == click_type_end:
        result = count_answer()
        publishTopic(result)
        return {
            'statusCode': 200,
            'body': {'click_type': click_type, 'result': result}
        }
    else:
        return {
            'statusCode': 200,
            'body': {'click_type': click_type}
        }

def save_answer(event):
    click_type = event["deviceEvent"]["buttonClicked"]["clickType"]
    reported_time = event["deviceEvent"]["buttonClicked"]["reportedTime"]
    
    dynamotable.put_item(
        Item={
            "click_type":    click_type,
            "reported_time": reported_time
       }
    )    
    
    return click_type

def count_answer():
    ansLst = get_answers()
    yesCnt = 0
    noCnt  = 0
    for ans in ansLst:
        if ans["click_type"] == click_type_yes:
            yesCnt+=1
        else:
            noCnt+=1
    totalCnt = yesCnt + noCnt
    score = (yesCnt * 100) // totalCnt
    result = { 'score': score, 'detail': { 'total': totalCnt, 'yes': yesCnt, 'no': noCnt } }
    logger.info(json.dumps(result))
    return result
    
def get_answers():
    queryData = dynamotable.query(
        KeyConditionExpression = Key("click_type").eq(click_type_end),
        ScanIndexForward = False,
        Limit = 2
    )
    logger.info("queryData: " + json.dumps(queryData))
    
    to_time   = queryData["Items"][0]["reported_time"]
    from_time = queryData["Items"][1]["reported_time"] if queryData["Count"] == 2 else None
    logger.info("to_time:   " + to_time)
    logger.info("from_time: " + from_time)
    
    keyCondition = (Key("click_type").eq(click_type_yes) | Key("click_type").eq(click_type_no))
    if from_time == None:
        keyCondition = keyCondition & Key("reported_time").gt(from_time)
    else:
        keyCondition = keyCondition & Key("reported_time").between(from_time, to_time)

    ansLst = dynamotable.scan(
        FilterExpression = keyCondition
    )
    logger.info("ansLst: " + json.dumps(ansLst))
    
    return ansLst["Items"]
    
def publishTopic(result):
    iot = boto3.client('iot-data')
    try:
        iot.publish(
            topic=iot_publish_topic,
            qos=0,
            payload=json.dumps(result, ensure_ascii=False)
        )
        print("Publish to AWS IoT: OK")
    except Exception as e:
        print("Publish to AWS IoT: Error")
        print(e)
    
    