import requests
import json
import time

def try_ex(func):
    try:
        return func()
    except KeyError:
        return None


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': { 'content': message, 'contentType': 'PlainText' }
        }
    }

    return response


def lambda_handler(event,context):
    bookingToken = try_ex(lambda: event['sessionAttributes']['bookingToken'])
    cardNo = try_ex(lambda: event['currentIntent']['slots']['cardNo'])
    session_attributes = {}
    session_attributes['SessionId'] = 'SessionId'

    url = "https://booking-api.skypicker.com/api/v0.1/check_flights?v=2&booking_token={}&bnum=0&pnum=1&affily=otto_%7Bmarket%7D&currency=EUR".format(bookingToken)

    flights_checked, limit = False, 0
    while not flights_checked and limit < 30:
        r = requests.get(url)
        response = r.json()
        flights_checked = response['flights_checked']
        flights_invalid = response['flights_invalid']
        if not flights_checked:
            time.sleep(3)
            limit += 1


    if flights_invalid:
        return close(
        session_attributes,
        'Fulfilled',
        {
            "Not possible to book this flight"
        }
    )

    url = 'https://booking-api.skypicker.com/api/v0.1/save_booking?v=2'
    body = {
        "lang": "en",
        "bags": 1,
        "passengers": [
            {
                "surname": "Jakub",
                "name": "Bares",
                "cardno": "{}".format(cardNo),
                "phone": "+420 603557076",
                "birthday": 504371200,
                "nationality": "CZ",
                "title": "mr",
                "expiration": 1454371200,
                "email": "lubos@skypicker.com"
            }
        ],
        "locale": "en",
        "currency": "czk",
        "booking_token": "{}".format(bookingToken),
        "affily": "affilid",
        "booked_at": "affilid"
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(body), headers=headers)
    return close(
        session_attributes,
        'Fulfilled',
        'Well done. Your flight is booked'
    )
