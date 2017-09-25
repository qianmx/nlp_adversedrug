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
8. Make the first submission by combining two neighboring two words if applicable

### Updated next steps:
1. Add ngram to the model (i.e. we should also predict phrases as names)
2. Make a submission of predictions on the test set
