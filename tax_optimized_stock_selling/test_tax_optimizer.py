import unittest
import datetime
import os
from tax_optimized_stock_selling import StockLot, TaxOptimizer, load_stock_lots_from_csv

class TestTaxOptimizer(unittest.TestCase):
    def setUp(self):
        # Create sample stock lots for testing
        self.today = datetime.date.today()
        one_year_ago = self.today - datetime.timedelta(days=366)
        six_months_ago = self.today - datetime.timedelta(days=180)
        
        # Sample lots with varying characteristics
        self.lots = [
            # Long-term losses
            StockLot(index=0, quantity=10, symbol="TEST", date_acquired=one_year_ago, cost_basis_per_share=150.0),
            
            # Short-term losses
            StockLot(index=1, quantity=15, symbol="TEST", date_acquired=six_months_ago, cost_basis_per_share=130.0),
            
            # Long-term gains
            StockLot(index=2, quantity=20, symbol="TEST", date_acquired=one_year_ago, cost_basis_per_share=80.0),
            
            # Short-term gains
            StockLot(index=3, quantity=25, symbol="TEST", date_acquired=six_months_ago, cost_basis_per_share=90.0),
        ]
        
        # Current price for TEST stock
        self.current_prices = {"TEST": 100.0}
        
        # Tax rates
        self.tax_rates = {"short_term": 0.35, "long_term": 0.15}
        
        # Create optimizer
        self.optimizer = TaxOptimizer(self.lots, self.current_prices, self.tax_rates)
    
    def test_is_long_term(self):
        """Test long-term vs short-term determination"""
        self.assertTrue(self.lots[0].is_long_term())
        self.assertFalse(self.lots[1].is_long_term())
        self.assertTrue(self.lots[2].is_long_term())
        self.assertFalse(self.lots[3].is_long_term())
    
    def test_unrealized_gain_loss(self):
        """Test unrealized gain/loss calculations"""
        # Lot 0: Long-term loss
        self.assertEqual(self.lots[0].unrealized_gain_loss_per_share(100.0), -50.0)
        self.assertEqual(self.lots[0].total_unrealized_gain_loss(100.0), -500.0)
        
        # Lot 2: Long-term gain
        self.assertEqual(self.lots[2].unrealized_gain_loss_per_share(100.0), 20.0)
        self.assertEqual(self.lots[2].total_unrealized_gain_loss(100.0), 400.0)
    
    def test_calculate_tax(self):
        """Test tax calculation"""
        # Long-term loss (negative tax = tax benefit)
        self.assertAlmostEqual(self.optimizer.calculate_tax(self.lots[0], 10.0), -75.0)  # -500 * 0.15
        
        # Short-term loss (negative tax = tax benefit)
        self.assertAlmostEqual(self.optimizer.calculate_tax(self.lots[1], 15.0), -157.5)  # -450 * 0.35
        
        # Long-term gain (positive tax)
        self.assertAlmostEqual(self.optimizer.calculate_tax(self.lots[2], 20.0), 60.0)  # 400 * 0.15
        
        # Short-term gain (positive tax)
        self.assertAlmostEqual(self.optimizer.calculate_tax(self.lots[3], 25.0), 87.5)  # 250 * 0.35
    
    def test_optimize_sales_prioritizes_losses(self):
        """Test that the optimizer prioritizes tax-loss harvesting"""
        # Request an amount that requires selling from multiple lots
        # 10 shares from lot 0 ($1000) + at least some from lot 1
        optimal_sales = self.optimizer.optimize_sales(1500.0)
        
        # Should prioritize losses first (lots 0 and 1)
        lot_indices = [idx for idx, _ in optimal_sales]
        self.assertIn(0, lot_indices)  # Long-term loss
        self.assertIn(1, lot_indices)  # Short-term loss
    
    def test_optimize_sales_prefers_long_term_gains(self):
        """Test that the optimizer prefers long-term gains over short-term gains"""
        # Create an optimizer with only gain lots
        gain_lots = [self.lots[2], self.lots[3]]  # Long-term gain and short-term gain
        gain_optimizer = TaxOptimizer(gain_lots, self.current_prices, self.tax_rates)
        
        # Request an amount that requires selling some but not all available shares
        optimal_sales = gain_optimizer.optimize_sales(1500.0)
        
        # First lot should be the long-term gain (index 2)
        self.assertEqual(optimal_sales[0][0], 2)
    
    def test_exact_target_amount(self):
        """Test that the optimizer can hit the exact target amount when possible"""
        # $100 per share × 10 shares = $1000 exactly
        optimal_sales = self.optimizer.optimize_sales(1000.0)
        
        # Calculate actual proceeds
        total_proceeds = sum(
            self.optimizer.calculate_proceeds(
                next(lot for lot in self.lots if lot.index == lot_idx), 
                shares
            )
            for lot_idx, shares in optimal_sales
        )
        
        # Should be very close to the target amount
        self.assertAlmostEqual(total_proceeds, 1000.0, places=2)
    
    def test_partial_lot_sales(self):
        """Test that the optimizer can sell partial lots"""
        # Request an amount that will require selling part of a lot
        optimal_sales = self.optimizer.optimize_sales(250.0)
        
        # Check if any of the lots are sold partially
        any_partial = False
        for lot_idx, shares in optimal_sales:
            lot = next(lot for lot in self.lots if lot.index == lot_idx)
            if shares < lot.quantity:
                any_partial = True
                break
        
        self.assertTrue(any_partial, "Should sell partial lots when needed")
    
    def test_cannot_exceed_portfolio_value(self):
        """Test that the optimizer cannot sell more than the portfolio value"""
        # Total portfolio value is 7000 (10+15+20+25 shares at $100)
        optimal_sales = self.optimizer.optimize_sales(10000.0)
        
        # Calculate total shares sold
        total_shares_sold = sum(shares for _, shares in optimal_sales)
        
        # Should not exceed total shares available
        total_shares_available = sum(lot.quantity for lot in self.lots)
        self.assertLessEqual(total_shares_sold, total_shares_available)


class TestWithRealData(unittest.TestCase):
    """Tests using the real AMZN sample data"""
    
    def setUp(self):
        self.csv_file = os.path.join(os.path.dirname(__file__), "amzn_20250407.csv")
        self.stock_lots = load_stock_lots_from_csv(self.csv_file)
        
        # Fixed price for AMZN for consistent testing
        self.current_prices = {"AMZN": 175.50}
        
        # Tax rates
        self.tax_rates = {"short_term": 0.35, "long_term": 0.15}
        
        # Create optimizer
        self.optimizer = TaxOptimizer(self.stock_lots, self.current_prices, self.tax_rates)
    
    def test_csv_loading(self):
        """Test that CSV data is loaded correctly"""
        self.assertTrue(len(self.stock_lots) > 0, "Should load stock lots from CSV")
        self.assertEqual(self.stock_lots[0].symbol, "AMZN", "Symbol should be loaded correctly")
    
    def test_optimize_with_real_data(self):
        """Test optimization with real data"""
        # Request to sell $10,000 worth of stock
        optimal_sales = self.optimizer.optimize_sales(10000.0)
        
        # Should return a non-empty list of sales
        self.assertTrue(len(optimal_sales) > 0, "Should find optimal sales")
        
        # Calculate total proceeds and tax
        total_proceeds = 0
        total_tax = 0
        
        for lot_idx, shares in optimal_sales:
            lot = next(l for l in self.stock_lots if l.index == lot_idx)
            proceeds = self.optimizer.calculate_proceeds(lot, shares)
            tax = self.optimizer.calculate_tax(lot, shares)
            
            total_proceeds += proceeds
            total_tax += tax
        
        # Should prioritize tax efficiency (losses first, then long-term gains)
        self.assertLessEqual(total_tax, 0.20 * total_proceeds, 
                            "Tax should be less than 20% of proceeds with efficient sales")
        
        # Log the results for inspection
        print(f"\nOptimal sales for ${10000:.2f} target:")
        print(f"Total Proceeds: ${total_proceeds:.2f}")
        print(f"Total Tax: ${total_tax:.2f}")
        print(f"Net Proceeds: ${total_proceeds - total_tax:.2f}")
        
        # List the specific lots sold
        print("\nLots sold:")
        for lot_idx, shares in optimal_sales:
            lot = next(l for l in self.stock_lots if l.index == lot_idx)
            proceeds = self.optimizer.calculate_proceeds(lot, shares)
            tax = self.optimizer.calculate_tax(lot, shares)
            gain_loss = lot.unrealized_gain_loss_per_share(self.current_prices["AMZN"]) * shares
            
            print(f"Lot {lot_idx}: {shares:.2f} shares, Proceeds: ${proceeds:.2f}, "
                 f"Tax: ${tax:.2f}, Gain/Loss: ${gain_loss:.2f}, "
                 f"Term: {'Long-term' if lot.is_long_term() else 'Short-term'}")


# Run the tests if this file is executed directly
if __name__ == "__main__":
    unittest.main()