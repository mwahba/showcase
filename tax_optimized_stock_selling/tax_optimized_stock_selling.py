import csv
import datetime
import yfinance as yf
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import os

@dataclass
class StockLot:
    index: int
    quantity: float
    symbol: str
    date_acquired: datetime.date
    cost_basis_per_share: float
    
    def is_long_term(self) -> bool:
        """Returns True if this lot qualifies for long-term capital gains treatment"""
        holding_period = datetime.date.today() - self.date_acquired
        return holding_period.days >= 365
    
    def unrealized_gain_loss_per_share(self, current_price: float) -> float:
        """Calculate unrealized gain/loss per share"""
        return current_price - self.cost_basis_per_share
    
    def total_unrealized_gain_loss(self, current_price: float) -> float:
        """Calculate total unrealized gain/loss for the lot"""
        return self.quantity * self.unrealized_gain_loss_per_share(current_price)
    
    def __str__(self) -> str:
        return f"Lot {self.index}: {self.quantity} shares of {self.symbol}, acquired {self.date_acquired}, cost basis ${self.cost_basis_per_share:.2f}"


class TaxOptimizer:
    def __init__(self, stock_lots: List[StockLot], current_prices: Dict[str, float], 
                 tax_rates: Dict[str, float]):
        self.stock_lots = stock_lots
        self.current_prices = current_prices
        self.tax_rates = tax_rates  # Example: {"short_term": 0.35, "long_term": 0.15}
    
    def calculate_tax(self, lot: StockLot, shares_to_sell: float) -> float:
        """
        Calculate tax liability for selling given shares from a lot.
        
        For gains: returns positive tax value
        For losses: returns negative tax value (tax benefit)
        """
        if shares_to_sell <= 0:
            return 0.0
        
        current_price = self.current_prices.get(lot.symbol, 0)
        gain_loss_per_share = lot.unrealized_gain_loss_per_share(current_price)
        total_gain_loss = shares_to_sell * gain_loss_per_share
        
        # Determine tax rate based on holding period
        tax_rate = self.tax_rates["long_term"] if lot.is_long_term() else self.tax_rates["short_term"]
        
        # Return the tax amount (positive for gains, negative for losses)
        return total_gain_loss * tax_rate
    
    def calculate_proceeds(self, lot: StockLot, shares_to_sell: float) -> float:
        """Calculate proceeds from selling shares"""
        if shares_to_sell <= 0:
            return 0.0
        
        current_price = self.current_prices.get(lot.symbol, 0)
        return shares_to_sell * current_price
    
    def calculate_tax_efficiency_score(self, lot: StockLot) -> Optional[float]:
        """
        Calculate the tax efficiency score for a lot based on how close to zero
        the resulting tax would be.
        
        Returns None if the lot has no valid price or quantity.
        """
        current_price = self.current_prices.get(lot.symbol, 0)
        if current_price <= 0 or lot.quantity <= 0:
            return None
        
        gain_loss_per_share = lot.unrealized_gain_loss_per_share(current_price)
        is_long_term = lot.is_long_term()
        
        # Tax rate based on holding period
        tax_rate = self.tax_rates["long_term"] if is_long_term else self.tax_rates["short_term"]
        
        # Calculate absolute tax per dollar of proceeds (closer to zero is better)
        if current_price > 0:
            tax_per_dollar = abs((gain_loss_per_share * tax_rate) / current_price)
        else:
            return float('inf')  # Not tax efficient if we can't sell it
        
        return tax_per_dollar
        
    def optimize_for_zero_tax(self, target_amount: float) -> List[Tuple[int, float, float, float]]:
        """
        Find the optimal combination of lots to sell to reach the target amount
        while getting a tax amount as close to zero as possible.
        
        Returns a list of tuples: (lot_index, shares_to_sell, proceeds, tax)
        """
        # Filter valid lots and calculate tax efficiency (how close to zero tax)
        valid_lots = []
        for lot in self.stock_lots:
            current_price = self.current_prices.get(lot.symbol, 0)
            if current_price <= 0 or lot.quantity <= 0:
                continue
                
            # Calculate hypothetical tax per share
            gain_loss_per_share = lot.unrealized_gain_loss_per_share(current_price)
            is_long_term = lot.is_long_term()
            tax_rate = self.tax_rates["long_term"] if is_long_term else self.tax_rates["short_term"]
            tax_per_share = gain_loss_per_share * tax_rate
            
            # Add to our collection of valid lots
            valid_lots.append((lot, tax_per_share))
        
        # If no valid lots, return empty result
        if not valid_lots:
            return []
            
        # Separate into gain lots (positive tax) and loss lots (negative tax)
        gain_lots = [(lot, tax) for lot, tax in valid_lots if tax > 0]
        loss_lots = [(lot, tax) for lot, tax in valid_lots if tax < 0]
        
        # Sort gain lots by lowest tax first
        gain_lots.sort(key=lambda x: x[1])
        
        # Sort loss lots by smallest absolute tax first (closer to zero)
        loss_lots.sort(key=lambda x: abs(x[1]))
        
        # Try different combinations to find the one with tax closest to zero
        best_solution = None
        best_tax_distance_from_zero = float('inf')
        
        # Try different mixes of gain and loss lots
        for gain_percentage in range(0, 101, 5):  # Try 0%, 5%, 10%, ..., 100% from gain lots
            loss_percentage = 100 - gain_percentage
            
            # Calculate how much to raise from each category
            gain_target = target_amount * (gain_percentage / 100)
            loss_target = target_amount * (loss_percentage / 100)
            
            # Create a solution with this mix
            solution = []
            total_proceeds = 0
            total_tax = 0
            
            # First sell from gain lots up to gain_target
            remaining_gain_target = gain_target
            for lot, tax_per_share in gain_lots:
                if remaining_gain_target <= 0:
                    break
                    
                current_price = self.current_prices.get(lot.symbol, 0)
                
                # Calculate how many shares to sell from this lot
                shares_needed = remaining_gain_target / current_price
                shares_to_sell = min(lot.quantity, shares_needed)
                
                if shares_to_sell > 0:
                    proceeds = self.calculate_proceeds(lot, shares_to_sell)
                    tax = self.calculate_tax(lot, shares_to_sell)
                    
                    solution.append((lot.index, shares_to_sell, proceeds, tax))
                    total_proceeds += proceeds
                    total_tax += tax
                    remaining_gain_target -= proceeds
            
            # Then sell from loss lots up to loss_target
            remaining_loss_target = loss_target
            for lot, tax_per_share in loss_lots:
                if remaining_loss_target <= 0:
                    break
                    
                current_price = self.current_prices.get(lot.symbol, 0)
                
                # Calculate how many shares to sell from this lot
                shares_needed = remaining_loss_target / current_price
                shares_to_sell = min(lot.quantity, shares_needed)
                
                if shares_to_sell > 0:
                    proceeds = self.calculate_proceeds(lot, shares_to_sell)
                    tax = self.calculate_tax(lot, shares_to_sell)
                    
                    solution.append((lot.index, shares_to_sell, proceeds, tax))
                    total_proceeds += proceeds
                    total_tax += tax
                    remaining_loss_target -= proceeds
            
            # Check if this solution gets close enough to the target amount
            if total_proceeds >= target_amount * 0.98:  # Allow 2% tolerance
                # Check if this solution has tax closer to zero
                tax_distance_from_zero = abs(total_tax)
                
                if tax_distance_from_zero < best_tax_distance_from_zero:
                    best_tax_distance_from_zero = tax_distance_from_zero
                    best_solution = solution
        
        # If no solution found, try normal tax-loss harvesting
        if best_solution is None:
            # Fall back to maximizing tax loss harvesting
            return self.maximize_tax_loss_harvesting(target_amount)
        
        return best_solution
        
    def fine_tune_for_zero_tax(self, initial_solution: List[Tuple[int, float, float, float]], 
                               target_amount: float) -> List[Tuple[int, float, float, float]]:
        """
        Fine-tune a solution to get the tax amount as close to zero as possible
        by adjusting the share quantities.
        
        Returns a refined list of tuples: (lot_index, shares_to_sell, proceeds, tax)
        """
        if not initial_solution:
            return []
            
        # Extract the initial solution details
        solution = initial_solution.copy()
        
        # Calculate current total
        total_proceeds = sum(proceeds for _, _, proceeds, _ in solution)
        total_tax = sum(tax for _, _, _, tax in solution)
        
        # If the tax is already very close to zero, we're done
        if abs(total_tax) < 1.0:  # $1 tolerance
            return solution
            
        # Try to adjust the solution to get closer to zero tax
        if total_tax > 0:
            # We need to increase shares from loss lots or decrease from gain lots
            loss_lots = [(i, lot_idx, shares, proceeds, tax) 
                      for i, (lot_idx, shares, proceeds, tax) in enumerate(solution) 
                      if tax < 0]
            
            gain_lots = [(i, lot_idx, shares, proceeds, tax) 
                       for i, (lot_idx, shares, proceeds, tax) in enumerate(solution) 
                       if tax > 0]
            
            # If we have loss lots, try to increase them
            if loss_lots:
                # Sort loss lots by most negative tax per share (highest tax benefit)
                loss_lots.sort(key=lambda x: x[4]/x[3] if x[3] > 0 else 0)
                
                for i, lot_idx, shares, proceeds, tax in loss_lots:
                    # Get the actual lot
                    lot = next(l for l in self.stock_lots if l.index == lot_idx)
                    remaining_shares = lot.quantity - shares
                    
                    if remaining_shares > 0:
                        # Calculate how many more shares we need to sell to offset the positive tax
                        current_price = self.current_prices.get(lot.symbol, 0)
                        tax_per_share = tax / shares  # Current tax per share for this lot
                        
                        additional_shares_needed = min(
                            remaining_shares,
                            total_tax / abs(tax_per_share) * (shares / proceeds if proceeds > 0 else 1)
                        )
                        
                        if additional_shares_needed > 0:
                            # Update this lot in the solution
                            new_shares = shares + additional_shares_needed
                            new_proceeds = self.calculate_proceeds(lot, new_shares)
                            new_tax = self.calculate_tax(lot, new_shares)
                            
                            solution[i] = (lot_idx, new_shares, new_proceeds, new_tax)
                            
                            # Recalculate total
                            total_proceeds = sum(proceeds for _, _, proceeds, _ in solution)
                            total_tax = sum(tax for _, _, _, tax in solution)
                            
                            if abs(total_tax) < 1.0 or total_proceeds > target_amount * 1.05:
                                break
            
            # If tax is still positive and we have gain lots, try to decrease them
            if total_tax > 1.0 and gain_lots:
                # Sort gain lots by highest tax per share first
                gain_lots.sort(key=lambda x: x[4]/x[3] if x[3] > 0 else float('inf'), reverse=True)
                
                for i, lot_idx, shares, proceeds, tax in gain_lots:
                    if shares <= 0.1:  # Skip if already very small
                        continue
                        
                    # Calculate how many shares to remove to decrease tax
                    shares_to_remove = min(
                        shares * 0.5,  # Don't remove more than half
                        total_tax / (tax / shares) if tax > 0 else 0
                    )
                    
                    if shares_to_remove > 0:
                        # Get the actual lot
                        lot = next(l for l in self.stock_lots if l.index == lot_idx)
                        
                        # Update this lot in the solution
                        new_shares = shares - shares_to_remove
                        if new_shares < 0.1:  # Avoid tiny shares
                            new_shares = 0
                            
                        if new_shares > 0:
                            new_proceeds = self.calculate_proceeds(lot, new_shares)
                            new_tax = self.calculate_tax(lot, new_shares)
                            solution[i] = (lot_idx, new_shares, new_proceeds, new_tax)
                        else:
                            # Remove this lot from the solution
                            solution[i] = (lot_idx, 0, 0, 0)
                        
                        # Recalculate total
                        total_proceeds = sum(proceeds for _, _, proceeds, _ in solution)
                        total_tax = sum(tax for _, _, _, tax in solution)
                        
                        if abs(total_tax) < 1.0 or total_proceeds < target_amount * 0.95:
                            break
                            
        elif total_tax < 0:
            # We need to increase shares from gain lots or decrease from loss lots
            gain_lots = [(i, lot_idx, shares, proceeds, tax) 
                       for i, (lot_idx, shares, proceeds, tax) in enumerate(solution) 
                       if tax > 0]
            
            loss_lots = [(i, lot_idx, shares, proceeds, tax) 
                      for i, (lot_idx, shares, proceeds, tax) in enumerate(solution) 
                      if tax < 0]
            
            # If we have gain lots, try to increase them
            if gain_lots:
                # Sort gain lots by lowest tax per share first
                gain_lots.sort(key=lambda x: x[4]/x[3] if x[3] > 0 else float('inf'))
                
                for i, lot_idx, shares, proceeds, tax in gain_lots:
                    # Get the actual lot
                    lot = next(l for l in self.stock_lots if l.index == lot_idx)
                    remaining_shares = lot.quantity - shares
                    
                    if remaining_shares > 0:
                        # Calculate how many more shares we need to sell to offset the negative tax
                        current_price = self.current_prices.get(lot.symbol, 0)
                        tax_per_share = tax / shares if shares > 0 else 0  # Current tax per share
                        
                        additional_shares_needed = min(
                            remaining_shares,
                            abs(total_tax) / tax_per_share * (shares / proceeds if proceeds > 0 else 1) if tax_per_share > 0 else 0
                        )
                        
                        if additional_shares_needed > 0:
                            # Update this lot in the solution
                            new_shares = shares + additional_shares_needed
                            new_proceeds = self.calculate_proceeds(lot, new_shares)
                            new_tax = self.calculate_tax(lot, new_shares)
                            
                            solution[i] = (lot_idx, new_shares, new_proceeds, new_tax)
                            
                            # Recalculate total
                            total_proceeds = sum(proceeds for _, _, proceeds, _ in solution)
                            total_tax = sum(tax for _, _, _, tax in solution)
                            
                            if abs(total_tax) < 1.0 or total_proceeds > target_amount * 1.05:
                                break
            
            # If tax is still negative and we have loss lots, try to decrease them
            if total_tax < -1.0 and loss_lots:
                # Sort loss lots by highest absolute tax per share first
                loss_lots.sort(key=lambda x: abs(x[4]/x[3]) if x[3] > 0 else 0, reverse=True)
                
                for i, lot_idx, shares, proceeds, tax in loss_lots:
                    if shares <= 0.1:  # Skip if already very small
                        continue
                        
                    # Calculate how many shares to remove to decrease negative tax
                    shares_to_remove = min(
                        shares * 0.5,  # Don't remove more than half
                        abs(total_tax) / abs(tax / shares) if tax < 0 else 0
                    )
                    
                    if shares_to_remove > 0:
                        # Get the actual lot
                        lot = next(l for l in self.stock_lots if l.index == lot_idx)
                        
                        # Update this lot in the solution
                        new_shares = shares - shares_to_remove
                        if new_shares < 0.1:  # Avoid tiny shares
                            new_shares = 0
                            
                        if new_shares > 0:
                            new_proceeds = self.calculate_proceeds(lot, new_shares)
                            new_tax = self.calculate_tax(lot, new_shares)
                            solution[i] = (lot_idx, new_shares, new_proceeds, new_tax)
                        else:
                            # Remove this lot from the solution
                            solution[i] = (lot_idx, 0, 0, 0)
                        
                        # Recalculate total
                        total_proceeds = sum(proceeds for _, _, proceeds, _ in solution)
                        total_tax = sum(tax for _, _, _, tax in solution)
                        
                        if abs(total_tax) < 1.0 or total_proceeds < target_amount * 0.95:
                            break
        
        # Remove any zero-share entries and ensure we meet the target amount
        solution = [(idx, shares, proceeds, tax) for idx, shares, proceeds, tax in solution if shares > 0]
        
        # Check if we've met the target amount
        total_proceeds = sum(proceeds for _, _, proceeds, _ in solution)
        
        if total_proceeds < target_amount * 0.98:
            # We need to add more shares to reach the target
            # Find unused lots or lots with remaining shares
            used_lot_indices = {idx for idx, _, _, _ in solution}
            
            # First try to use remaining shares from lots already in the solution
            for lot in self.stock_lots:
                if lot.index in used_lot_indices:
                    # Get current shares sold for this lot
                    current_shares = next(shares for idx, shares, _, _ in solution if idx == lot.index)
                    remaining_shares = lot.quantity - current_shares
                    
                    if remaining_shares > 0:
                        current_price = self.current_prices.get(lot.symbol, 0)
                        if current_price <= 0:
                            continue
                            
                        # Calculate how many more shares we need
                        additional_proceeds_needed = target_amount - total_proceeds
                        additional_shares = min(remaining_shares, additional_proceeds_needed / current_price)
                        
                        if additional_shares > 0:
                            # Find this lot in our solution
                            for i, (idx, shares, proceeds, tax) in enumerate(solution):
                                if idx == lot.index:
                                    # Update this lot
                                    new_shares = shares + additional_shares
                                    new_proceeds = self.calculate_proceeds(lot, new_shares)
                                    new_tax = self.calculate_tax(lot, new_shares)
                                    
                                    solution[i] = (idx, new_shares, new_proceeds, new_tax)
                                    
                                    # Update total
                                    total_proceeds += (new_proceeds - proceeds)
                                    
                                    if total_proceeds >= target_amount * 0.98:
                                        break
            
            # If we still need more, add unused lots
            if total_proceeds < target_amount * 0.98:
                unused_lots = [lot for lot in self.stock_lots if lot.index not in used_lot_indices]
                
                # Prioritize lots that will keep tax close to zero
                # Calculate current total tax
                total_tax = sum(tax for _, _, _, tax in solution)
                
                if total_tax >= 0:
                    # Prefer loss lots
                    unused_lots.sort(key=lambda lot: self.calculate_tax_efficiency_score(lot) or float('inf'))
                else:
                    # Prefer gain lots
                    unused_lots.sort(key=lambda lot: (
                        abs(self.calculate_tax_efficiency_score(lot) or float('inf'))
                        if self.calculate_tax(lot, 1) > 0 
                        else float('inf')
                    ))
                
                for lot in unused_lots:
                    current_price = self.current_prices.get(lot.symbol, 0)
                    if current_price <= 0 or lot.quantity <= 0:
                        continue
                        
                    # Calculate how many shares we need
                    additional_proceeds_needed = target_amount - total_proceeds
                    shares_to_sell = min(lot.quantity, additional_proceeds_needed / current_price)
                    
                    if shares_to_sell > 0:
                        proceeds = self.calculate_proceeds(lot, shares_to_sell)
                        tax = self.calculate_tax(lot, shares_to_sell)
                        
                        solution.append((lot.index, shares_to_sell, proceeds, tax))
                        total_proceeds += proceeds
                        
                        if total_proceeds >= target_amount * 0.98:
                            break
        
        return solution
    
    def find_minimum_tax_sales(self, target_amount: float) -> List[Tuple[int, float]]:
        """
        Find the combination of lots that minimizes total tax while reaching the target amount.
        
        Returns a list of tuples: (lot_index, shares_to_sell)
        """
        # First try to get a solution with tax close to zero
        initial_solution = self.optimize_for_zero_tax(target_amount)
        
        if not initial_solution:
            return []
            
        # Fine-tune the solution to get even closer to zero tax
        refined_solution = self.fine_tune_for_zero_tax(initial_solution, target_amount)
        
        # Convert to the expected return format
        return [(idx, shares) for idx, shares, _, _ in refined_solution]
    
    def optimize_sales(self, target_amount: float) -> List[Tuple[int, float]]:
        """
        Find the optimal combination of lots to sell to reach the target amount
        while minimizing taxes.
        
        Returns a list of tuples: (lot_index, shares_to_sell)
        """
        return self.find_minimum_tax_sales(target_amount)


def parse_date(date_str: str) -> datetime.date:
    """Parse date from string, handling various formats"""
    try:
        for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d-%b-%Y', '%d-%b-%y'):
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        # If none of the formats work, try a fallback
        return datetime.datetime.strptime(date_str, '%m/%d/%y').date()
    except ValueError:
        # Return a default date if parsing fails
        print(f"Warning: Could not parse date '{date_str}', using today's date")
        return datetime.date.today()


def clean_numeric(value_str: str) -> float:
    """Clean a numeric string, handling currency symbols and commas"""
    if not value_str or value_str.strip() == '':
        return 0.0
    
    # Remove currency symbols, commas, and other non-numeric characters except dots
    clean_str = ''.join(c for c in value_str if c.isdigit() or c == '.' or c == '-')
    
    try:
        return float(clean_str)
    except ValueError:
        print(f"Warning: Could not parse number '{value_str}', using 0")
        return 0.0


def load_stock_lots_from_csv(filename: str) -> List[StockLot]:
    """Load stock lots from a CSV file"""
    lots = []
    
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for i, row in enumerate(reader):
                try:
                    # Extract and clean data from CSV
                    symbol = row.get('Symbol', '')
                    quantity = clean_numeric(row.get('Quantity', '0'))
                    date_acquired = parse_date(row.get('Date Acquired', ''))
                    cost_basis = clean_numeric(row.get('Cost Basis/Share', '0'))
                    
                    # Skip empty rows or rows without key fields
                    if not symbol or quantity <= 0 or cost_basis <= 0:
                        continue
                    
                    lot = StockLot(
                        index=i,
                        quantity=quantity,
                        symbol=symbol,
                        date_acquired=date_acquired,
                        cost_basis_per_share=cost_basis
                    )
                    lots.append(lot)
                except Exception as e:
                    print(f"Error processing row {i}: {e}")
                    print(f"Row data: {row}")
            
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
    
    return lots


def extract_current_price_from_csv(filename: str, symbol: str) -> Optional[float]:
    """
    Attempt to extract current price from CSV by analyzing unrealized G/L data.
    This is a fallback if yfinance prices aren't available.
    """
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                row_symbol = row.get('Symbol', '')
                
                if row_symbol != symbol:
                    continue
                
                quantity = clean_numeric(row.get('Quantity', '0'))
                cost_basis = clean_numeric(row.get('Cost Basis/Share', '0'))
                unrealized_gl = clean_numeric(row.get('Unrealized G/L', '0'))
                
                if quantity > 0 and cost_basis > 0:
                    # Calculate implied current price from unrealized G/L
                    current_price = cost_basis + (unrealized_gl / quantity)
                    if current_price > 0:
                        return current_price
        
        return None
    except Exception as e:
        print(f"Error extracting current price from CSV: {e}")
        return None


def get_current_prices(symbols: List[str]) -> Dict[str, float]:
    """Get current stock prices using yfinance"""
    prices = {}
    
    for symbol in set(symbols):  # Use set to eliminate duplicates
        if not symbol:  # Skip empty symbols
            continue
            
        try:
            ticker = yf.Ticker(symbol)
            # Get the latest closing price
            hist = ticker.history(period="1d")
            if not hist.empty:
                prices[symbol] = hist['Close'].iloc[-1]
            else:
                print(f"Warning: Could not get current price for {symbol}")
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
    
    return prices


def main():
    """Main function to run the tax optimizer"""
    print("Tax-Optimized Stock Selling Program")
    print("===================================")
    
    # Get CSV file input with default to the sample file
    csv_file = input("Enter the path to your stock lots CSV file (press Enter for default 'amzn_20250407.csv'): ")
    if not csv_file:
        csv_file = "amzn_20250407.csv"
    
    # Load stock lots from CSV
    stock_lots = load_stock_lots_from_csv(csv_file)
    if not stock_lots:
        print("No valid stock lots found. Exiting.")
        return
    
    print(f"Loaded {len(stock_lots)} stock lots.")
    
    # Get unique symbols
    symbols = list(set([lot.symbol for lot in stock_lots if lot.symbol]))
    if not symbols:
        print("No stock symbols found in the data. Exiting.")
        return
    
    print(f"Fetching current prices for {len(symbols)} symbols...")
    
    # Try to get prices from yfinance
    current_prices = get_current_prices(symbols)
    
    # If any symbols are missing prices, try to extract them from the CSV
    for symbol in symbols:
        if symbol not in current_prices or current_prices[symbol] <= 0:
            print(f"Attempting to extract price for {symbol} from CSV data...")
            csv_price = extract_current_price_from_csv(csv_file, symbol)
            if csv_price:
                current_prices[symbol] = csv_price
                print(f"Using calculated price for {symbol}: ${csv_price:.2f}")
    
    # Verify we have prices for all symbols
    missing_prices = [s for s in symbols if s not in current_prices or current_prices[s] <= 0]
    if missing_prices:
        print(f"Warning: Missing prices for symbols: {', '.join(missing_prices)}")
        decision = input("Continue anyway? (y/n): ")
        if decision.lower() != 'y':
            return
    
    # Summarize lot data
    print("\nSummary of Stock Lots:")
    print(f"{'Index':<6} {'Symbol':<8} {'Quantity':<10} {'Cost Basis':<12} {'Current':<10} {'Gain/Loss':<12} {'Term':<10}")
    print("-" * 80)
    
    for lot in stock_lots:
        current_price = current_prices.get(lot.symbol, 0)
        gain_loss = lot.unrealized_gain_loss_per_share(current_price) * lot.quantity
        term = "Long-term" if lot.is_long_term() else "Short-term"
        
        print(f"{lot.index:<6} {lot.symbol:<8} {lot.quantity:<10.2f} "
              f"${lot.cost_basis_per_share:<11.2f} ${current_price:<9.2f} "
              f"${gain_loss:<11.2f} {term:<10}")
    
    print("-" * 80)
    
    # Get tax rates
    print("\nEnter your capital gains tax rates:")
    short_term_rate_str = input("Short-term capital gains tax rate (e.g., 0.35 for 35%) [default: 0.35]: ")
    long_term_rate_str = input("Long-term capital gains tax rate (e.g., 0.15 for 15%) [default: 0.15]: ")
    
    short_term_rate = 0.35 if not short_term_rate_str else float(short_term_rate_str)
    long_term_rate = 0.15 if not long_term_rate_str else float(long_term_rate_str)
    
    tax_rates = {
        "short_term": short_term_rate,
        "long_term": long_term_rate
    }
    
    # Get target amount
    target_amount_str = input("\nEnter the target amount you need to raise ($): ")
    target_amount = float(target_amount_str)
    
    if target_amount <= 0:
        print("Target amount must be greater than zero. Exiting.")
        return
    
    # Create optimizer and calculate optimal sales
    optimizer = TaxOptimizer(stock_lots, current_prices, tax_rates)
    optimal_sales = optimizer.optimize_sales(target_amount)
    
    if not optimal_sales:
        print("\nCould not find a solution to reach the target amount.")
        return
    
    # Calculate and display results
    total_proceeds = 0
    total_tax = 0
    
    print("\nOptimal Sales Plan:")
    print("===================")
    print(f"{'Index':<6} {'Symbol':<8} {'Quantity':<10} {'Cost Basis':<12} {'Current':<10} {'Proceeds':<12} {'Tax':<12} {'Term':<10}")
    print(f"{'':<6} {'':<8} {'to Sell':<10} {'per Share':<12} {'Price':<10} {'':<12} {'':<12} {'':<10}")
    print("-" * 80)
    
    results = []
    
    for lot_index, shares_to_sell in optimal_sales:
        lot = next((l for l in stock_lots if l.index == lot_index), None)
        if lot and shares_to_sell > 0:
            current_price = current_prices.get(lot.symbol, 0)
            proceeds = optimizer.calculate_proceeds(lot, shares_to_sell)
            tax = optimizer.calculate_tax(lot, shares_to_sell)
            term = "Long-term" if lot.is_long_term() else "Short-term"
            
            total_proceeds += proceeds
            total_tax += tax
            
            tax_display = f"${tax:.2f}" if tax >= 0 else f"-${abs(tax):.2f}"
            
            print(f"{lot.index:<6} {lot.symbol:<8} {shares_to_sell:<10.2f} "
                  f"${lot.cost_basis_per_share:<11.2f} ${current_price:<9.2f} "
                  f"${proceeds:<11.2f} {tax_display:<11} {term:<10}")
                  
            results.append({
                "index": lot.index,
                "symbol": lot.symbol,
                "shares_to_sell": shares_to_sell,
                "cost_basis": lot.cost_basis_per_share,
                "current_price": current_price,
                "proceeds": proceeds,
                "tax": tax,
                "term": term
            })
    
    print("-" * 80)
    print(f"Total Proceeds: ${total_proceeds:.2f}")
    print(f"Total Tax: ${total_tax:.2f}")
    print(f"Net Proceeds: ${total_proceeds - total_tax:.2f}")
    
    # Calculate how close we got to the target
    percent_achieved = (total_proceeds / target_amount) * 100
    print(f"Target achievement: {percent_achieved:.1f}% (${target_amount:.2f} requested)")
    
    if abs(total_proceeds - target_amount) > 0.01 * target_amount:
        print(f"\nNote: Could only achieve ${total_proceeds:.2f} of the ${target_amount:.2f} target amount.")
        if total_proceeds < target_amount:
            total_possible = sum(lot.quantity * current_prices.get(lot.symbol, 0) for lot in stock_lots)
            print(f"Total portfolio value is ${total_possible:.2f}, which is less than the requested amount.")
    
    # Write results to file
    output_file = "tax_optimized_sales.txt"
    with open(output_file, "w") as f:
        f.write("Tax-Optimized Stock Sales\n")
        f.write("========================\n\n")
        f.write(f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n")
        f.write(f"Target Amount: ${target_amount:.2f}\n")
        f.write(f"Total Proceeds: ${total_proceeds:.2f}\n")
        f.write(f"Total Tax: ${total_tax:.2f}\n")
        f.write(f"Net Proceeds: ${total_proceeds - total_tax:.2f}\n\n")
        
        f.write(f"{'Index':<6} {'Symbol':<8} {'Quantity':<10} {'Cost Basis':<12} {'Current':<10} {'Proceeds':<12} {'Tax':<12} {'Term':<10}\n")
        f.write(f"{'':<6} {'':<8} {'to Sell':<10} {'per Share':<12} {'Price':<10} {'':<12} {'':<12} {'':<10}\n")
        f.write("-" * 80 + "\n")
        
        for r in results:
            tax_display = f"${r['tax']:.2f}" if r['tax'] >= 0 else f"-${abs(r['tax']):.2f}"
            f.write(f"{r['index']:<6} {r['symbol']:<8} {r['shares_to_sell']:<10.2f} "
                   f"${r['cost_basis']:<11.2f} ${r['current_price']:<9.2f} "
                   f"${r['proceeds']:<11.2f} {tax_display:<11} {r['term']:<10}\n")
                   
        f.write("-" * 80 + "\n")
        f.write("\nTax Optimization Strategy:\n")
        f.write("1. First, harvest tax losses (sell lots with unrealized losses)\n")
        f.write("2. Then, sell long-term gain lots (lower tax rate)\n")
        f.write("3. Finally, if needed, sell short-term gain lots (higher tax rate)\n")
    
    print(f"\nResults saved to {os.path.abspath(output_file)}")
    
    # Ask if user wants to save lots that weren't sold
    save_unsold = input("\nDo you want to save information about unsold lots? (y/n): ")
    if save_unsold.lower() == 'y':
        unsold_file = "remaining_lots.txt"
        with open(unsold_file, "w") as f:
            f.write("Remaining Stock Lots After Sales\n")
            f.write("===============================\n\n")
            f.write(f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n")
            
            sold_lot_indices = {lot_idx for lot_idx, _ in optimal_sales}
            unsold_lots = [lot for lot in stock_lots if lot.index not in sold_lot_indices]
            
            if not unsold_lots:
                f.write("All lots were sold.\n")
            else:
                f.write(f"{'Index':<6} {'Symbol':<8} {'Quantity':<10} {'Cost Basis':<12} {'Current':<10} {'Value':<12} {'Gain/Loss':<12} {'Term':<10}\n")
                f.write("-" * 90 + "\n")
                
                for lot in unsold_lots:
                    current_price = current_prices.get(lot.symbol, 0)
                    value = lot.quantity * current_price
                    gain_loss = lot.total_unrealized_gain_loss(current_price)
                    term = "Long-term" if lot.is_long_term() else "Short-term"
                    
                    f.write(f"{lot.index:<6} {lot.symbol:<8} {lot.quantity:<10.2f} "
                           f"${lot.cost_basis_per_share:<11.2f} ${current_price:<9.2f} "
                           f"${value:<11.2f} ${gain_loss:<11.2f} {term:<10}\n")
                           
                f.write("-" * 90 + "\n")
            
        print(f"Unsold lots saved to {os.path.abspath(unsold_file)}")


if __name__ == "__main__":
    main()