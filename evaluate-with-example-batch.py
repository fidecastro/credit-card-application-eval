import os
import shutil
import subprocess

# Replace this with the number of iterations you want to run
num_iterations = 10

for i in range(num_iterations):
    print(f"Running iteration {i + 1}...")

    # Call evaluate-with-example.py
    subprocess.run(["python3", "evaluate-with-example.py"])

    # Rename AER_credit_card_data_processed.csv to <iteration_number>.csv
    input_file = "AER_credit_card_data_processed.csv"
    output_file = f"LLMoutput-example-{i + 1}-AER_credit_card_data_processed.csv"

    if os.path.exists(input_file):
        shutil.move(input_file, output_file)
        print(f"Saved iteration {i + 1} results as {output_file}")
    else:
        print(f"Error: {input_file} not found. Skipping iteration {i + 1}.")

print("Finished running all iterations.")
