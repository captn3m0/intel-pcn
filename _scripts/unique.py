import csv

def remove_duplicates(input_file):
    seen_keys = set()
    cleaned_data = []

    with open(input_file, 'r', newline='', encoding='utf-8') as csv_input:
        reader = csv.reader(csv_input)
        header = next(reader)  # Read the header

        cleaned_data.append(header)

        i = 0
        for row in reader:
            i+=1
            primary_key = row[0]
            if primary_key not in seen_keys:
                seen_keys.add(primary_key)
                cleaned_data.append(row)
        print("Input Count= ", i)

        return cleaned_data

def fix_date(input_file):
    cleaned_data = []
    with open(input_file, 'r', newline='', encoding='utf-8') as csv_input:
        reader = csv.reader(csv_input)
        header = next(reader)

        cleaned_data.append(header)

        for row in reader:
            m,d,y = str(row[1]).split('/')
            row[1] = f'{y}-{m}-{d}'
            cleaned_data.append(row)

        return cleaned_data
    
if __name__ == "__main__":
    input_file = "_data/pcn.csv"
    output_file = "_data/output.csv"

    cleaned_data = fix_date(input_file)

    with open(output_file, 'w', newline='', encoding='utf-8') as csv_output:
        writer = csv.writer(csv_output)
        print("Output Count= ", len(cleaned_data))
        writer.writerows(cleaned_data)