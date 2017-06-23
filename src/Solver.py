import requests

class Solver:
    def demo(self):
        flights = self.get_flights('PRG', 'BRQ','01/09/2017', '01/10/2017')

        print(len(flights))

        flights_in_budget = self.filter_flights_by_budget(flights, 200)

        print(len(list(flights_in_budget)))

        return;

    def get_flights(self, flyFrom, to, dateFrom, dateTo):
        r = requests.get(
            'https://api.skypicker.com/flights?flyFrom={}&to={}&dateFrom={}&dateTo={}&partner=picky'.format(flyFrom, to, dateFrom, dateTo))
        flights = r.json()['data']
        return flights

    def filter_flights_by_budget(self, flights, budget):
        for flight in flights:
            if flight['conversion']['EUR'] < budget: yield flight


Solver().demo()