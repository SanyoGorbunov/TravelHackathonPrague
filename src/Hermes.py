import requests
import traceback
from random import randint
from datetime import datetime, timedelta


# --- Main handler ---

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def confirm(session_attributes, slots, message):
    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ConfirmIntent",
            "message": {
                "contentType": "PlainText",
                "content": message
            },
            "intentName": "ConfirmFlight",
            "slots": slots
        }
    }

    return response;


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def lambda_handler(event, context):
    try:
        session_attributes = {}

        city_name = try_ex(lambda: event['currentIntent']['slots']['Location'])

        date_from = datetime.strptime(try_ex(lambda: event['currentIntent']['slots']['StartDate']), '%Y-%d-%m')

        days = safe_int(try_ex(lambda: event['currentIntent']['slots']['Days']))

        budget = safe_int(try_ex(lambda: event['currentIntent']['slots']['Budget']))

        visited_countries = try_ex(lambda: event['currentIntent']['slots']['VisitedCountries']).split(',')

        flight = Solver().demo(city_name, date_from, days, budget, visited_countries)

        city = flight['mapIdto']

        price = str(flight['conversion']['EUR'])

        session_attributes['booking_token'] = flight['booking_token']

        return confirm(
            session_attributes,
            event['currentIntent']['slots'],
            'The city I have chosen for you is ' + city.title() + '! The ticket price is ' + price + '. Would you like to make a booking?'
        )

    except:
        return close(
            {},
            event['currentIntent']['slots'],
            {
                'contentType': 'PlainText',
                'content': 'Thanks, I have placed your reservation to' + traceback.format_exc()
            }
        )


class Solver:
    def demo(self, city_name, date_from, days, budget, visited_countries):
        airport_code = self.get_airport_code(city_name)

        date_to = date_from + timedelta(days=days)

        flights = self.get_flights(airport_code, date_from, date_to)

        print(len(flights))

        flights_in_budget = list(self.filter_flights_by_budget(flights, budget))

        print(len(flights_in_budget))

        flights_in_non_visited_countries = list(
            self.filter_flights_by_visited_countries(flights_in_budget, visited_countries))

        print(len(flights_in_non_visited_countries))

        flight_winner_id = self.get_flight_winner_id(len(flights_in_non_visited_countries));

        return flights_in_non_visited_countries[flight_winner_id]

    def get_flights(self, flyFrom, dateFrom, dateTo):
        r = requests.get(
            'https://api.skypicker.com/flights?flyFrom={}&dateFrom={}&dateTo={}&partner=picky'.format(flyFrom,
                                                                                                      dateFrom.strftime(
                                                                                                          '%d/%m/%Y'),
                                                                                                      dateTo.strftime(
                                                                                                          '%d/%m/%Y')))
        flights = r.json()['data']
        return flights

    def filter_flights_by_budget(self, flights, budget):
        for flight in flights:
            if flight['conversion']['EUR'] < budget: yield flight

    def filter_flights_by_visited_countries(self, flights, visited_contries):
        for flight in flights:
            if not flight['countryTo']['name'] in visited_contries: yield flight

    def get_flight_winner_id(self, max):
        return randint(0, max - 1)

    def get_airport_code(self, city_name):
        r = requests.get('https://locations.skypicker.com/?term={}'.format(city_name))
        return r.json()['locations'][0]['code']