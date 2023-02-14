# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from cgitb import text
from operator import ge
from typing import Any, Text, Dict, List
from urllib import response
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from api_data import get_flights_data
#
#
class ActionGetData(Action):
    def name(self) -> Text:
         return "action_get_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        source=tracker.get_slot("source")
        destination=tracker.get_slot("destination")
        date=tracker.get_slot("date")

        result = get_flights_data(source,destination,date)

        if source == destination:
          dispatcher.utter_template("utter_same_locations",tracker,board=source,dest=destination)

        if len(result)>0:
          dispatcher.utter_template("utter_book_slots",tracker,date=result[0],arrival=result[1],departure=result[2],flight=result[3],board=result[4],dest=result[5],price=result[6],day=result[7],month=result[8])
        else:
          dispatcher.utter_template("utter_no_flight",tracker,date=date,board=source,dest=destination)
        return []
