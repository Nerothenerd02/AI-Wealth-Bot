from transformers import BertModel, BertTokenizer
import torch
from torch import nn

class_names = ['negative', 'neutral', 'positive']
PRE_TRAINED_MODEL_NAME = 'bert-base-cased'

# Load tokenizer
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

# Define the model
class SentimentClassifier(nn.Module):
    def __init__(self, n_classes):
        super(SentimentClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
        self.drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = output[1]
        output = self.drop(pooled_output)
        return self.out(output)
