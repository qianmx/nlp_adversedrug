# nlp_adversedrug
Adverse Drug Reaction Extraction from Drug Labels

## Summary of this repository
1. Extract texts (and word labels if applicable) from the XML datasets
2. Pre-process texts with common NLP methods
3. Word embedding
4. Train LSTM networks together with word embedding
5. Tune parameters by validation outputs
6. Predict the holdout validation dataset
7. Calculate F1 score

### Updated next steps:
1. Make the first submission
2. Add ngram to the model (i.e. we should also predict phrases as names)
3. Make a submission of predictions on the test set
