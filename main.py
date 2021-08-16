import yaml
import re
import numpy.random as rand


class Intent:
    def __init__(self, name, slots) -> None:
        self.name = name
        self.slots = slots

class Slot:
    def __init__(self, value) -> None:
        self.values = (value,)
    
    def addValue(self, value) -> None:
        if value not in self.values:
            self.values += (value,)
5
slot_map = { 
    "restaurant-pricerange" : "hotel-pricerange",
    "restaurant-area" : "hotel-area",
    "restaurant-bookday" : "hotel-bookday",
    "restaurant-bookpeople" : "hotel-bookpeople",
    "restaurant-food" : "hotel-stars",
    "restaurant-name" : "hotel-name",
    "restaurant-booktime" : "hotel-bookstay",
    "required_info" : "required_info"
}

# Get all values of each slot for every intent

f = open("Model\\data\\nlu.yml")
nlu = yaml.load(f)
f.close()

nlu = filter(lambda x: "intent" in x.keys(), nlu["nlu"])

# The values of the slots of all intents are combined because of the diversity of data.
all_slots = {}

for intent in nlu:
    examples = intent["examples"].split("\n")

    for e in examples:
        slots_in_utter = re.search(r"\[[a-zA-Z0-9]+\]\([a-zA-Z]+[_-][a-zA-Z]+\)", e, re.IGNORECASE)
        if slots_in_utter:
            for r in slots_in_utter.regs:
                [slot_value, slot_name] = e[r[0]:r[1]].split("](")

                if slot_name[:-1] in all_slots:
                    all_slots[slot_name[:-1]].addValue(slot_value[1:])
                else:
                    all_slots[slot_name[:-1]] = Slot(slot_value[1:])

f = open("resources\\restaurant_stories.yml")
res_stories = yaml.load(f)
f.close()

for story in res_stories["stories"]:
    steps = story["steps"]
    for step in steps:
        step_keys = step.keys()
        if "intent" in step_keys:
            # Switch names of find_restaurant and book_restaurant
            match = re.search(r"restaurant", step["intent"], re.IGNORECASE)
            if match:
                step["intent"] = re.sub(r"restaurant", "hotel", step["intent"])

            # Switch restaurant entities to hotel entities
            if "entities" in step_keys:
                entities = step["entities"]
                for e in range(len(entities)):
                    entity_name = list(entities[e].keys())[0]
                    hotel_entity = slot_map[entity_name]
                    hotel_value = rand.choice(all_slots[hotel_entity].values)
                    entities[e] = { hotel_entity : hotel_value }

        else:
            # Switch names of the actions and responses
            action = step["action"]
            match = re.search(r"action", action, re.IGNORECASE)
            if match: # Its an action
                step["action"] = re.sub(r"restaurant", "hotel", action)
            else: # Its a response
                action = action.split("_")
                if action[1] == "ask":
                    hotel_response = "utter_ask"
                    for i in range(2, len(action), 2):
                        slot_name = action[i] + "-" + action[i+1]
                        hotel_entity = "_".join(slot_map[slot_name].split("-"))
                        hotel_response += "_" + hotel_entity
                    step["action"] = hotel_response

# Write the story string
stories = """version: "2.0"

stories:

"""

for story in res_stories["stories"]:
    stories += "- story: {}\n  steps:\n".format(story["story"])
    steps = story["steps"]
    for step in steps:
        if "intent" in step.keys():
            stories += "  - intent: {}\n".format(step["intent"])
            if "entities" in step.keys():
                stories += "    entities:\n"
                for entity in step["entities"]:
                    entity_key = list(entity.keys())[0]
                    stories += "    - {}: {}\n".format(entity_key, entity[entity_key])
        else:
            stories += "  - action: {}\n".format(step["action"])
    stories += "\n\n"

with open("Model\\data\\stories.yml", "w") as f:
    f.write(stories)

# Change the domain file
f = open("resources\\restaurant_domain.yml")
res_domain = yaml.load(f)
f.close()

intents = res_domain["intents"]
for i in range(len(intents)):
    match = re.search(r"restaurant", intents[i])
    if match:
        intents[i] = re.sub(r"restaurant", "hotel", intents[i])

entities = res_domain["entities"]
for i in range(len(entities)):
    entities[i] = slot_map[entities[i]]

res_slots = res_domain["slots"]
slots = []
for key in res_slots.keys():
    slots += [slot_map[key]] 

res_responses = res_domain["responses"]
responses = []
for key in res_responses.keys():
    hotel_response = key
    response_name = key.split("_")
    if response_name[1] == "ask":
        hotel_response = "utter_ask"
        for i in range(2, len(response_name), 2):
            slot_name = response_name[i] + "-" + response_name[i+1]
            hotel_entity = "_".join(slot_map[slot_name].split("-"))
            hotel_response += "_" + hotel_entity
    responses += [hotel_response]

actions = res_domain["actions"]
for i in range(len(actions)):
    match = re.search(r"restaurant", actions[i])
    if match:
        actions[i] = re.sub(r"restaurant", "hotel", actions[i])


domain = """version: "2.0"

"""

domain += "intents:\n"
for i in intents:
    domain += "  - {}\n".format(i)

domain += "\nentities:\n"
for e in entities:
    domain += "  - {}\n".format(e)

domain += "\nslots:\n"
for s in slots:
    domain += "  {}:\n    type: text\n".format(s)

domain += "\nresponses:\n"
for r in responses:
    domain += "  {}:\n  - text: {} response\n".format(r, r)

domain += "\nactions:\n"
for a in actions:
    domain += "  - {}\n".format(a)

with open("Model\\domain.yml", "w") as f:
    f.write(domain)

















    







