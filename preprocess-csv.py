import pandas as pd
import csv
import time

def process_row(row):
    result = []

    result.append(f"The applicant is {round(row['age'])} years old,")
    result.append(f"has {row['reports']} major derogatory reports,")
    result.append(f"earns an annual income of ${row['income'] * 10000:.0f},")
    result.append(f"has a share ratio of {row['share'] * 100:.0f}% of credit card expenditure to yearly income,")
    result.append(f"spends an average of ${round(row['expenditure'])} per month on their credit card,")
    result.append(f"{'owns' if row['owner'] == 1 else 'does not own'} their home,")
    result.append(f"{'is' if row['selfemp'] == 1 else 'is not'} self-employed,")
    result.append(f"has {row['dependents']} dependents,")
    result.append(f"has lived at their current address for {row['months']} months,")
    result.append(f"holds {row['majorcards']} major credit cards,")
    result.append(f"and has {row['active']} active credit accounts.")

    return ' '.join(result)

def main():
    input_file = "AER_credit_card_data.csv"
    output_file = "AER_credit_card_data_preprocessed.csv"

    df = pd.read_csv(input_file)

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(df.columns.tolist() + ['text'])

        for i, (_, row) in enumerate(df.iterrows()):
            print(f"Current row: {i+1}")
            text = process_row(row)
            csv_writer.writerow(row.tolist() + [text])

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()

    elapsed_time = (end_time - start_time)/60
    print(f"Elapsed time: {elapsed_time:.2f} minutes")
