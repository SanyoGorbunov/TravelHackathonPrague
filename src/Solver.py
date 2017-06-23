import requests
from random import randint

class Solver:
    def demo(self, budget, visited_countries):
        flights = self.get_flights('PRG','01/09/2017', '01/10/2017')

        print(len(flights))

        flights_in_budget = list(self.filter_flights_by_budget(flights, budget))

        print(len(flights_in_budget))

        flights_in_non_visited_countries = list(self.filter_flights_by_visited_countries(flights_in_budget, visited_countries))

        print(len(flights_in_non_visited_countries))

        flight_winner_id = self.get_flight_winner_id(len(flights_in_non_visited_countries));

        return flights_in_non_visited_countries[flight_winner_id]


    def get_flights(self, flyFrom, dateFrom, dateTo):
        r = requests.get(
            'https://api.skypicker.com/flights?flyFrom={}&dateFrom={}&dateTo={}&partner=picky'.format(flyFrom, dateFrom, dateTo))
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



t = Solver().demo(40, ['Czech Republic', 'Slovakia'])
print(t['mapIdto'])