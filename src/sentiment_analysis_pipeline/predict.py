from sentiment_classifier import SentimentClassifier, tokenizer, class_names
import torch

# Load the model
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

    sentiment = class_names[prediction]
    return sentiment, float(confidence)

# Example test
if __name__ == "__main__":
    test_text = "The market is crashing faster than expected."
    sentiment, confidence = predict_sentiment(test_text)
    print(f"Sentiment: {sentiment} (confidence: {round(confidence, 3)})")
