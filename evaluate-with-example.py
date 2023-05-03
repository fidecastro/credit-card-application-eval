import pandas as pd
import asyncio
import json
import sys
import csv
import time
import re

try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.") 

HOST = 'localhost:5005'
URI = f'ws://{HOST}/api/v1/stream'

prompt_preamble = "Credit card application decision\n"
prompt_end = "\nI will decide based on the facts above whether the applicant is either ""HIGH RISK"" or ""LOW RISK"". I won't write MEDIUM RISK. I deem the applicant to be: "

async def run(context): #context is the prompt; the other parameters can be freely changed
    request = {
        'prompt': context,
        'max_new_tokens': 10,
        'do_sample': True,
        'temperature': 1.99,
        'top_p': 0.18,
        'typical_p': 1,
        'repetition_penalty': 1.15,
        'top_k': 30,
        'min_length': 5,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 510,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    async with websockets.connect(URI) as websocket:
        await websocket.send(json.dumps(request))

        yield context

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['text']
                case 'stream_end':
                    return

async def print_response_stream(prompt):
    result = ''
    buffer = "\n\n\n\n\n\n\n\n\n\n" #adding tokens to create a buffer for streaming processing
    prompt_with_buffer= buffer + prompt
    prompt_length = len(prompt_with_buffer)
    async for response in run(prompt_with_buffer):
        result += response
        print(response, end='')
        sys.stdout.flush()
    return result[prompt_length:].strip()


import random

def create_evaluation_text(text, input_file):
    df = pd.read_csv(input_file)
    
    # 1. Randomly draw a 'yes' example
    example_yes = df[df['card'] == 'yes'].sample(1).iloc[0]['text']
    # 2. Randomly draw a 'no' example
    example_no = df[df['card'] == 'no'].sample(1).iloc[0]['text']

    # 3. Add the preamble and prompt_end to the examples
    example_prompt_yes = prompt_preamble + example_yes + prompt_end + " LOW RISK"
    example_prompt_no = prompt_preamble + example_no + prompt_end + " HIGH RISK"

    # 4. Randomly assign example_prompt_one and example_prompt_two
    if random.random() < 0.5:
        example_prompt_one = example_prompt_yes
        example_prompt_two = example_prompt_no
    else:
        example_prompt_one = example_prompt_no
        example_prompt_two = example_prompt_yes

    # 5. Create the final evaluation_text
    evaluation_text = f"1. {example_prompt_one}\n\n2. {example_prompt_two}\n\n3. {prompt_preamble}{text}{prompt_end}"
    
    return evaluation_text


async def main():
    input_file = "AER_credit_card_data_preprocessed.csv"
    output_file = "AER_credit_card_data_processed.csv"

    df = pd.read_csv(input_file)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(df.columns.tolist() + ['FullReply', 'evaluation'])

        for i, (_, row) in enumerate(df.iterrows()):
            valid_evaluation = False
            while not valid_evaluation:
                try:
                    print(f"\nCurrent row: {i+1}")
                    text = row['text']
                    evaluation_text = create_evaluation_text(text, input_file)
                    evaluation = await print_response_stream(evaluation_text)
                    evaluation_lower = evaluation.lower()

                    list_markers = ["1\\. ", r"\(a\)", r"\(A\)", "1\\) ", "a\\. ", "A\\. "]
                    contains_list_marker = any(re.search(marker, evaluation) for marker in list_markers)
                    contains_both_high_and_low = "high" in evaluation_lower and "low" in evaluation_lower

                    if not (contains_list_marker or contains_both_high_and_low):
                        if "high" in evaluation_lower:
                            valid_evaluation = True
                            evaluation_decision = "no"
                        elif "low" in evaluation_lower:
                            valid_evaluation = True
                            evaluation_decision = "yes"

                    else:
                        print("\nInvalid evaluation, retrying...\n\n")

                    if valid_evaluation:
                                csv_writer.writerow(row.tolist() + [evaluation, evaluation_decision])
                    
                except asyncio.TimeoutError:
                    print("Processing timed out.\n")
                    break

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()

    elapsed_time = (end_time - start_time)/60
    print(f"Elapsed time: {elapsed_time:.2f} minutes")