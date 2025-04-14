from sentiment_classifier import SentimentClassifier, tokenizer, class_names
import torch
from datetime import datetime
from scraper_sources import get_all_headlines
import csv
import json
import os

# Load model
model = SentimentClassifier(len(class_names))
model.load_state_dict(
    torch.load("bert_sentiment_analysis.pt", map_location=torch.device('cpu')),
    strict=False
)
model.eval()

def predict_sentiment(text):
    encoded = tokenizer.encode_plus(
        text,
        max_length=128,
        add_special_tokens=True,
        return_token_type_ids=False,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    input_ids = encoded['input_ids']
    attention_mask = encoded['attention_mask']

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        confidence, prediction = torch.max(probs, dim=1)

    label = class_names[prediction]
    return label, float(confidence)

def sentiment_to_score(label, confidence):
    return {
        "negative": -1 * confidence,
        "neutral": 0,
        "positive": +1 * confidence
    }[label]

def analyze_batch(headlines):
    results = []
    total_score = 0

    for headline in headlines:
        sentiment, confidence = predict_sentiment(headline)
        score = sentiment_to_score(sentiment, confidence)
        total_score += score

        results.append({
            "datetime": datetime.now().isoformat(),
            "headline": headline,
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "score": round(score, 3)
        })

    avg_score = round(total_score / len(results), 3) if results else 0
    return results, avg_score

def classify_market(avg_score):
    if avg_score >= 0.5:
        return "Bullish"
    elif avg_score <= -0.5:
        return "Bearish"
    else:
        return "Neutral"

def save_as_csv(results, filename="sentiment_log.csv"):
    fieldnames = results[0].keys()
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

def save_as_json(results, filename="sentiment_log.json"):
    with open(filename, mode='a', encoding='utf-8') as file:
        for item in results:
            file.write(json.dumps(item) + "\n")


if __name__ == "__main__":
    headlines = get_all_headlines()
    results, avg_score = analyze_batch(headlines)
    market_class = classify_market(avg_score)

    for item in results:
        print(item)

    print(f"\n📊 Average Sentiment Score: {avg_score}")
    print(f"🧠 Market Sentiment Classification: {market_class}")

    #Save the files
    save_as_csv(results)
    save_as_json(results)
