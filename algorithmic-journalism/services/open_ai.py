from openai import OpenAI
import os
from datasets import load_dataset
import evaluate
import pandas as pd
import json
import time
from rouge_score import rouge_scorer, scoring

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "replace-with-your-own-token"))
DEFAULT_SYSTEM_PROMPT = 'You are a teaching assistant for Machine Learning. You should help the user to answer his question.'

def fine_tune_gpt_model():
    training_file_id = client.files.create(
        file=open(r"C:\Users\alara\OneDrive\Desktop\extra_train.jsonl", "rb"), purpose="fine-tune")

    validation_file_id = client.files.create(
        file=open(r"C:\Users\alara\OneDrive\Desktop\extra_validation.jsonl", "rb"), purpose="fine-tune")

    print(f"Training File ID: {training_file_id}")
    print(f"Validation File ID: {validation_file_id}")

    response = client.fine_tuning.jobs.create(
        training_file=training_file_id.id, 
        validation_file=validation_file_id.id,
        model="replace-with-intended-model")

    job_id = response.id
    status = response.status

    print(f'Fine-tunning model with jobID: {job_id}.')
    print(f"Training Response: {response}")
    print(f"Training Status: {status}")

    status = client.fine_tuning.jobs.retrieve(job_id).status
    if status not in ["succeeded", "failed"]:
        print(f"Job not in terminal status: {status}. Waiting.")
        while status not in ["succeeded", "failed"]:
            time.sleep(2)
            status = client.fine_tuning.jobs.retrieve(job_id).status
            print(f"Status: {status}")
    else:
        print(f"Finetune job {job_id} finished with status: {status}")
    print("Checking other finetune jobs in the subscription.")
    result = client.fine_tuning.jobs.list()
    print(f"Found {len(result.data)} finetune jobs.")

    # Retrieve the finetuned model
    fine_tuned_model = result.data[0].fine_tuned_model
    print(fine_tuned_model)

def get_summary_from_model(news_article):
    answer = client.chat.completions.create(
        model="replace-with-fine-tuned-model",  
        messages=[
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": news_article} 
          ]
    )

    return answer.choices[0].message.content

def create_dataset(question, answer):
    return {
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }

def create_gpt_finetune_datasets():
    xsum_dataset = load_dataset("EdinburghNLP/xsum")
    cnn_daily_dataset = load_dataset("cnn_dailymail", '3.0.0')
    df_xsum = xsum_dataset['train'].to_pandas()
    df_cnn = cnn_daily_dataset['train'].to_pandas()

    df_xsum.rename(columns={'document': 'Question', 'summary': 'Answer'}, inplace=True)
    df_cnn.rename(columns={'article': 'Question', 'highlights': 'Answer'}, inplace=True)
    df_train = df_xsum.loc[:50]
    df_train = pd.concat( [df_train, df_cnn.loc[:50]], ignore_index=True)

    df_validation = df_xsum.loc[50:62]
    df_validation = pd.concat([df_validation, df_cnn.loc[50:63]], ignore_index=True)

    with open(r"C:\Users\alara\OneDrive\Desktop\train.jsonl", "w") as f:
        for _, row in df_train.iterrows():
            example_str = json.dumps(create_dataset(row["Question"], row["Answer"]))
            f.write(example_str + "\n")

    with open(r"C:\Users\alara\OneDrive\Desktop\validation.jsonl", "w") as f:
        for _, row in df_validation.iterrows():
            example_str = json.dumps(create_dataset(row["Question"], row["Answer"]))
            f.write(example_str + "\n")



def retrain_gpt():
    cnn_daily_dataset = load_dataset("cnn_dailymail", '3.0.0')
    df_cnn = cnn_daily_dataset['train'].to_pandas()
    df_cnn.rename(columns={'article': 'Question', 'highlights': 'Answer'}, inplace=True)
    df_train = df_cnn.loc[200:300]
    df_validation = df_cnn.loc[300:350]

    with open(r"C:\Users\alara\OneDrive\Desktop\extra_train.jsonl", "w") as f:
        for _, row in df_train.iterrows():
            example_str = json.dumps(create_dataset(row["Question"], row["Answer"]))
            f.write(example_str + "\n")

    with open(r"C:\Users\alara\OneDrive\Desktop\extra_validation.jsonl", "w") as f:
        for _, row in df_validation.iterrows():
            example_str = json.dumps(create_dataset(row["Question"], row["Answer"]))
            f.write(example_str + "\n")


def calculate_bleu_score(predictions, references):
    bleu = evaluate.load('bleu')
    bleu_score = bleu.compute(predictions=predictions, references=references)
    print("BLEU score:", bleu_score)

def calculate_rouge_score(predictions, references):
    rouge = evaluate.load("rouge")
    rouge_score = rouge.compute(predictions=predictions, references=references)
    print("ROUGE score:", rouge_score)

""" if __name__ == "__main__":
    news_articles = []

    news_articles.extend(fetch_service.fetch_cnbc_data())
    news_articles.extend(fetch_service.fetch_guardian_data())
    # news_articles.extend(fetch_service.fetch_time_news())

    references = []
    predictions = []

    for article in news_articles:
        summary = get_summary_from_model((article["content"]))
        references.append([article["content"]])
        predictions.append(summary)
    
    calculate_bleu_score(predictions, references)
    calculate_rouge_score(predictions, references) """