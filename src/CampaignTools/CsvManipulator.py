import csv
import os


def create_csv_file(path, columns):
    if not os.path.isfile(path):
        campaign_csv = open(path, "w")
        campaign_csv.write(columns + "\n")
        campaign_csv.close()


def count_csv_rows(file_path):
    with open(file_path, mode='r', newline='') as info_file:
        return sum(1 for _ in info_file) - 1


def update_csv(file_path, identifier, info):
    identifier = str(identifier)

    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file.readlines())

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for line in reader:
            if line[0] == identifier:
                writer.writerow(info)
            else:
                writer.writerow(line)
