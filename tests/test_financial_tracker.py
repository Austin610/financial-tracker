import unittest
import os
import tempfile
import sys
sys.path.append('src')
from financial_tracker import FinancialTracker, validate_amount, validate_date


class TestFinancialTracker(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.tracker = FinancialTracker(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialize_with_empty_file(self):
        """Test initialization with empty file."""
        # Write empty content to file
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write('')
        
        # Should initialize without error
        tracker = FinancialTracker(self.temp_file.name)
        self.assertEqual(tracker.data["budget"], 0.0)
        self.assertEqual(len(tracker.data["expenses"]), 0)
    
    def test_set_budget_positive(self):
        """Test setting a positive budget."""
        result = self.tracker.set_budget(1000.0)
        self.assertTrue(result)
        self.assertEqual(self.tracker.data["budget"], 1000.0)
    
    def test_set_budget_negative(self):
        """Test setting a negative budget should raise ValueError."""
        with self.assertRaises(ValueError):
            self.tracker.set_budget(-100.0)
    
    def test_set_budget_invalid_type(self):
        """Test setting budget with invalid type."""
        with self.assertRaises(ValueError):
            self.tracker.set_budget("invalid")
    
    def test_add_expense_valid(self):
        """Test adding a valid expense."""
        result = self.tracker.add_expense(50.0, "Food", "2024-01-15")
        self.assertTrue(result)
        self.assertEqual(len(self.tracker.data["expenses"]), 1)
        self.assertEqual(self.tracker.data["expenses"][0]["amount"], 50.0)
        self.assertEqual(self.tracker.data["expenses"][0]["category"], "Food")
    
    def test_add_expense_negative_amount(self):
        """Test adding expense with negative amount."""
        with self.assertRaises(ValueError):
            self.tracker.add_expense(-50.0, "Food")
    
    def test_add_expense_empty_category(self):
        """Test adding expense with empty category."""
        with self.assertRaises(ValueError):
            self.tracker.add_expense(50.0, "")
    
    def test_get_total_spent(self):
        """Test calculating total spent."""
        self.tracker.add_expense(50.0, "Food")
        self.tracker.add_expense(30.0, "Transport")
        total = self.tracker.get_total_spent()
        self.assertEqual(total, 80.0)
    
    def test_get_category_stats(self):
        """Test getting category statistics."""
        self.tracker.add_expense(50.0, "Food")
        self.tracker.add_expense(30.0, "Food")
        self.tracker.add_expense(20.0, "Transport")
        
        stats = self.tracker.get_category_stats()
        self.assertEqual(stats["Food"], 80.0)
        self.assertEqual(stats["Transport"], 20.0)
    
    def test_get_period_stats_valid(self):
        """Test getting period statistics with valid dates."""
        self.tracker.add_expense(50.0, "Food", "2024-01-15")
        self.tracker.add_expense(30.0, "Transport", "2024-01-16")
        
        stats = self.tracker.get_period_stats("2024-01-15", "2024-01-16")
        self.assertEqual(stats["total_spent"], 80.0)
        self.assertEqual(stats["expense_count"], 2)
    
    def test_get_period_stats_invalid_dates(self):
        """Test getting period statistics with invalid dates."""
        with self.assertRaises(ValueError):
            self.tracker.get_period_stats("invalid-date", "2024-01-16")
    
    def test_get_financial_summary(self):
        """Test getting complete financial summary."""
        self.tracker.set_budget(1000.0)
        self.tracker.add_expense(50.0, "Food")
        self.tracker.add_expense(30.0, "Transport")
        
        summary = self.tracker.get_financial_summary()
        self.assertEqual(summary["budget"], 1000.0)
        self.assertEqual(summary["total_spent"], 80.0)
        self.assertEqual(summary["remaining"], 920.0)


class TestHelperFunctions(unittest.TestCase):
    
    def test_validate_amount_positive(self):
        """Test validating positive amounts."""
        is_valid, amount = validate_amount("50.5")
        self.assertTrue(is_valid)
        self.assertEqual(amount, 50.5)
    
    def test_validate_amount_negative(self):
        """Test validating negative amounts."""
        is_valid, amount = validate_amount("-50.5")
        self.assertFalse(is_valid)
    
    def test_validate_amount_invalid(self):
        """Test validating invalid amount strings."""
        is_valid, amount = validate_amount("invalid")
        self.assertFalse(is_valid)
    
    def test_validate_date_valid(self):
        """Test validating valid dates."""
        self.assertTrue(validate_date("2024-01-15"))
    
    def test_validate_date_invalid(self):
        """Test validating invalid dates."""
        self.assertFalse(validate_date("2024-01-32"))
        self.assertFalse(validate_date("invalid-date"))


if __name__ == "__main__":
    unittest.main()