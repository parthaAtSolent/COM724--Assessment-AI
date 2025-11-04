from datetime import date

# Configuration constants
START_DATE = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Model parameters
LSTM_SEQUENCE_LENGTH = 60
RF_LOOKBACK_PERIOD = 60
TRAIN_TEST_SPLIT = 0.8

# Random Forest parameters
RF_PARAMS = {
    'n_estimators': 100,
    'random_state': 42,
    'max_depth': 10,
    'min_samples_split': 5,
    'n_jobs': -1
}

# LSTM parameters
LSTM_PARAMS = {
    'epochs': 50,
    'batch_size': 32,
    'verbose': 0
}
