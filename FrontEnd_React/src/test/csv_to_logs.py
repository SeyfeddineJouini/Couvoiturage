import csv

def filter_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['email', 'password']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in reader:
            writer.writerow({field: row[field] for field in fieldnames})

# Utilisation de la fonction pour filtrer le fichier CSV
filter_csv('users.csv', 'filtered_users.csv')