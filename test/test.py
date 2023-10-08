import csv

input_file = 'data/input/test_sample_10/way_points.csv'
output_file = 'data/input/test_sample_8/way_points2.csv'

with open(input_file, mode='r') as input_csvfile, open(output_file, mode='w', newline='') as output_csvfile:
    csv_reader = csv.DictReader(input_csvfile)
    fieldnames = csv_reader.fieldnames

    csv_writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()

    for row in csv_reader:
        x = int(row['x']) * 500
        y = int(row['y']) * 500

        row['x'] = x
        row['y'] = y

        csv_writer.writerow(row)

