from transformers import BertModel, BertTokenizer
import torch
from torch import nn

RANDOM_SEED = 42
torch.manual_seed(RANDOM_SEED)

class_names = ['negative', 'neutral', 'positive']
PRE_TRAINED_MODEL_NAME = 'bert-base-cased'
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

class SentimentClassifier(nn.Module):
    def __init__(self, n_classes):
        super(SentimentClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
        self.drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        output = self.bert(
        input_ids=input_ids,
        attention_mask=attention_mask
        )
        pooled_output = output[1]
        output = self.drop(pooled_output)
        return self.out(output)

model = SentimentClassifier(len(class_names))

model.load_state_dict(
    torch.load("basic_app/bert_sentiment_analysis.pt", map_location=torch.device('cpu')),
    strict=False
)


def predict_sentiment(sample_texts):
    sentiment = []
    for sample_text in sample_texts:
        encoded_review = tokenizer.encode_plus(
            sample_text,
            max_length=512,
            add_special_tokens=True,
            return_token_type_ids=False,
            padding='max_length',     # <--- Updated here
            truncation=True,           # <--- Added this
            return_attention_mask=True,
            return_tensors='pt',
        )

        input_ids = encoded_review['input_ids']
        attention_mask = encoded_review['attention_mask']

        output = model(input_ids, attention_mask)
        _, prediction = torch.max(output, dim=1)

        sentiment.append(class_names[prediction])

    return sentiment
