import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
import os
from datetime import datetime as dt, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.model_helper import save_model

class StockPricePredictor:
    def __init__(self, ticker = 'AAPL', model_dir='../model-outputs/3-stock-price-predictor', look_back=60, future_days=30):
        """
        Initialize Stock Price Predictor

        Parameters:
            ticker (str, optional): Stock ticker symbol. Defaults to 'AAPL'.
            model_dir (str, optional): Directory to save model outputs. Defaults to '../model-outputs'.
            look_back (int, optional): Number of previous days to use for prediction. Defaults to 60.
            future_days (int, optional): Number of days to predict into the future. Defaults to 30.
        """
        self.ticker = ticker
        self.model_dir = model_dir
        self.look_back = look_back
        self.future_days = future_days
        self.scaler = MinMaxScaler(feature_range=(0, 1))

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok = True)
        os.makedirs(f'{model_dir}/figures', exist_ok = True)
        os.makedirs(f'{model_dir}/figures/{ticker}', exist_ok = True)

    def fetch_data(self, years=5) -> pd.DataFrame:
        """Fetch historical stock data from Yahoo Finance"""
        end_date = dt.now()
        start_date = end_date - timedelta(days=years*365)

        print(f'Fetching {years} years of {self.ticker} data...')
        self.data = yf.download(self.ticker, start = start_date, end = end_date)

        # Keep only the 'Close' price
        self.df = self.data[['Close']].copy()
        self.df.rename(columns={'Close': 'price'}, inplace = True)

        print(f'Data fetched: {len(self.df)} trading days')
        return self.df
    
    def prepare_data(self, train_size = 0.8):
        """Prepare and transform data for LSTM (Long Short-Term Memory) model"""
        # LSTM models are a type of recurrent neural networks (RNN), designed to
        # handle sequential data by learning long-term dependencies, overcoming the
        # vanishing gradient problem common in standard RNNs. It is used in tasks
        # like language modeling, time series analysis, and speech recognition.

        # Normalize data
        self.scaled_data = self.scaler.fit_transform(self.df)

        # Create the training and test sets
        train_size = int(len(self.scaled_data) * train_size)
        self.train_data = self.scaled_data[:train_size]
        self.test_data = self.scaled_data[train_size - self.look_back:]

        # Create sequences
        self.x_train, self.y_train = self._create_sequences(self.train_data)
        self.x_test, self.y_test = self._create_sequences(self.test_data)

        # Reshapre for LSTM: [samples, time steps, features]
        self.x_train = self.x_train.reshape(self.x_train.shape[0], self.x_train.shape[1], 1)
        self.x_test = self.x_test.reshape(self.x_test.shape[0], self.x_test.shape[1], 1)

        print(f'Training data shape: {self.x_train.shape}')
        print(f'Testing data shape: {self.x_test.shape}')

        return self.x_train, self.y_train, self.x_test, self.y_test
    
    def _create_sequences(self, data) -> tuple[np.ndarray, np.ndarray]:
        x, y = [], []

        for i in range(len(data) - self.look_back):
            x.append(data[i:i + self.look_back, 0])
            y.append(data[i + self.look_back, 0])
        
        return np.array(x), np.array(y)
    
    def build_model(self):
        """Build LSTM model architecture"""
        self.model = Sequential([
            # First LSTM layer with return sequences for stacking
            LSTM(units = 50, return_sequences = True, input_shape = (self.look_back, 1)),
            Dropout(0.2),

            # Second LSTM layer
            LSTM(units = 50, return_sequences = True),
            Dropout(0.2),

            # Third LSTM layer
            LSTM(units = 50),
            Dropout(0.2),

            # Output layer
            Dense(units = 1)
        ])

        # Compile model
        self.model.compile(optimizer = 'adam', loss = 'mean_squared_error')

        print('Model built:')
        self.model.summary()

        return self.model
    
    def train_model(self, epochs = 50, batch_size = 32):
        """Train the LSTM model"""

        # Create callbacks
        callbacks = [
            EarlyStopping(monitor = 'val_loss', patience = 10, restore_best_weights = True),
            ModelCheckpoint(
                filepath=os.path.join(self.model_dir, f'{self.ticker}_model_checkpoint.keras'),
                save_best_only = True,
                monitor = 'val_loss'
            )
        ]

        # Train model
        history = self.model.fit(
            self.x_train, self.y_train,
            epochs = epochs,
            batch_size = batch_size,
            validation_split = 0.2,
            callbacks = callbacks,
            verbose = 1
        )

        # Plot training history
        plt.figure(figsize=(12, 6))
        plt.plot(history.history['loss'], label = 'Training Loss')
        plt.plot(history.history['val_loss'], label = 'Validation Loss')
        plt.title(f'{self.ticker} Stock Price Prediction - Training History')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{self.model_dir}/figures/{self.ticker}/training-history-{self.ticker}.png')

        return history
    
    def evaluate_model(self) -> tuple[float, float]:
        """Evaluate model on test data"""

        # Make predictions
        predictions = self.model.predict(self.x_test)

        # Inverse trasnform predictions and actual values
        prediction_copies = np.repeat(predictions, self.df.shape[1], axis = -1)
        predictions = self.scaler.inverse_transform(prediction_copies)[:, 0]

        y_test_copies = np.repeat(self.y_test.reshape(-1, 1), self.df.shape[1], axis = -1)
        actual = self.scaler.inverse_transform(y_test_copies)[:,0]

        # Calculate error metrics
        rmse = np.sqrt(np.mean(np.square(predictions - actual)))
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100

        print(f'Root mean square error: ${rmse:.2f}')
        print(f'Mean absolute percentage error: {mape:.2f}%')

        # Plot predictions vs actual
        train_size = int(len(self.scaled_data) * 0.8)
        train_dates = self.df.index[:train_size]
        test_dates = self.df.index[train_size:train_size + len(predictions)]

        plt.figure(figsize = (16, 8))
        plt.plot(self.df.index, self.df['price'], label = 'Historical Prices', alpha = 0.7)
        plt.plot(test_dates, predictions, label = 'Predicted Prices', color = 'red')
        plt.title(f'{self.ticker} Stock Price Prediction', fontsize = 16)
        plt.xlabel('Date', fontsize = 14)
        plt.ylabel('Stock Price ($)', fontsize = 14)
        plt.legend(fontsize = 12)
        plt.grid(True, alpha = 0.3)
        plt.savefig(f'{self.model_dir}/figures/{self.ticker}/historical-vs-predicted-{self.ticker}.png')

        return rmse, mape
    
    def predict_future(self) -> pd.DataFrame:
        """Predict future stock prices"""
        # Get the last sequence from the data
        last_sequence = self.scaled_data[-self.look_back:].reshape(1, self.look_back, 1)

        # Generate predictions for future days
        future_predictions = []
        current_sequence = last_sequence

        for _ in range(self.future_days):
            # Get prediction for the next day
            next_pred = self.model.predict(current_sequence)[0]

            # Append to predictions
            future_predictions.append(next_pred)

            # Update sequence for next prediction
            current_sequence = np.append(current_sequence[:,1:,:], [[next_pred]], axis = 1)

        # Inverse transform predictions
        future_pred_copies = np.repeat(np.array(future_predictions).reshape(-1, 1), self.df.shape[1], axis = -1)
        future_predictions = self.scaler.inverse_transform(future_pred_copies)[:,0]

        # Generate future dates
        last_date = self.df.index[-1]
        future_dates = pd.date_range(start = last_date + timedelta(days = 1), periods = self.future_days, freq = 'B')

        # Plot future predictions
        plt.figure(figsize = (16, 8))
        plt.plot(self.df.index[-100:], self.df['price'].iloc[-100:], label = 'Historical Prices', alpha = 0.7)
        plt.plot(future_dates, future_predictions, label = 'Future Predictions', color = 'red', linestyle = '--')
        plt.axvline(x = last_date, color = 'green', linestyle = '-', alpha = 0.7, label = 'Prediction Start')
        plt.title(f'{self.ticker} Stock Price - Future {self.future_days} Trading Days Prediction', fontsize = 16)
        plt.xlabel('Date', fontsize = 14)
        plt.ylabel('Stock Price ($)', fontsize = 14)
        plt.legend(fontsize = 12)
        plt.grid(True, alpha = 0.3)
        plt.savefig(f'{self.model_dir}/figures/{self.ticker}/prediction-{self.ticker}-{self.future_days}-days.png')

        # Create a DataFrame with predictions
        future_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Price': future_predictions
        }).set_index('Date')

        print('\nFuture Price Predictions:')
        print(future_df)

        return future_df
    
def main():
    # Initialize stock predictor for Apple
    predictor = StockPricePredictor(ticker = 'AAPL', look_back = 60, future_days = 30)

    # Fetch and prepare data
    predictor.fetch_data(years = 5)
    predictor.prepare_data()

    # Build and train the model
    predictor.build_model()
    predictor.train_model(epochs = 50)

    # Evaluate the model
    predictor.evaluate_model()
    
    # Predict future prices
    predictor.predict_future()

    # Save model
    additional_metadata = {
        'ticker': predictor.ticker,
        'look_back': predictor.look_back,
        'data_range': f'{predictor.df.index[0].strftime('%Y-%m-%d')} to {predictor.df.index[-1].strftime('%Y-%m-%d')}'
    }
    save_model(predictor.model, f'stock_predictor_{predictor.ticker}', additional_metadata = additional_metadata)

if __name__ == '__main__':
    main()
