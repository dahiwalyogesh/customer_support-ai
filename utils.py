import csv
import json


def load_kb(path="kb.json"):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_orders(path="orders.csv"):
    orders = []
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            orders.append(row)
    return orders