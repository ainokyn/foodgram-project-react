import csv

with open("fruits.csv", "w") as file:
    headings = ["Mango", "Banana", "Apple", "Orange"]
    data_writer = csv.DictWriter(file, fieldnames=headings)
    data_writer.writeheader()
    data_writer.writerow({"Mango": 50, "Banana": 70, "Apple": 30, "Orange": 90})
    data_writer.writerow({"Mango": 3, "Banana": 1, "Apple": 6, "Orange": 4})
