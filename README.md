# nlp_adversedrug
Adverse Drug Reaction Extraction from Drug Labels

## Summary of this repository
1. Extract texts (and word labels if applicable) from the XML datasets
2. Pre-process texts with common NLP methods
3. Word embedding
4. Train LSTM networks together with word embedding
5. Tune parameters by validation outputs
6. Predict the holdout validation dataset

### Updated next steps:
1. Calculate F1 score
2. Fine-tune the model
3. Add ngram to the model (i.e. we should also predict phrases as names)
4. Make a submission of predictions on the test set
