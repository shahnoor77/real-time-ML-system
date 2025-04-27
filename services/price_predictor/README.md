steps:
1 - Fetch ohlc_data from FeatureStore.
2 - Split the data into Train and Test data.
3 - Preprocess data 
    Add missing rows, replace NaN values, etc.
4 - Create a Target metric 
5 - Train the Model
 Next step:
 --push the model to model registry using COMET-ML