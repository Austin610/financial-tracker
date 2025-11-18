#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Tracker Module
A console-based application for tracking personal finances
"""

import json
import os
import datetime
from typing import List, Dict, Optional, Tuple


class FinancialTracker:
    """
    A class to track personal finances including budget and expenses.
    """
    
    def __init__(self, data_file: str = "financial_data.json"):
        """
        Initialize FinancialTracker with data file path.
        """
        self.data_file = data_file
        self.data = {"budget": 0.0, "expenses": []}
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load financial data from JSON file.
        """
        try:
            if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    loaded_data = json.load(file)
                    self.data = loaded_data
        except (json.JSONDecodeError, IOError):
            # If file is empty or corrupted, start with fresh data
            self.data = {"budget": 0.0, "expenses": []}
    
    def _save_data(self) -> None:
        """
        Save financial data to JSON file.
        """
        with open(self.data_file, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)
    
    def set_budget(self, budget: float) -> bool:
        """
        Set the user's budget.
        """
        try:
            budget_float = float(budget)
            if budget_float < 0:
                raise ValueError("Budget cannot be negative")
            
            self.data["budget"] = budget_float
            self._save_data()
            return True
        except (ValueError, TypeError):
            raise ValueError("Invalid budget value")
    
    def add_expense(self, amount: float, category: str, date: Optional[str] = None) -> bool:
        """
        Add a new expense record.
        """
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Amount must be positive")
            
            if not category or not category.strip():
                raise ValueError("Category cannot be empty")
            
            if date is None:
                expense_date = datetime.date.today().isoformat()
            else:
                # Validate date format
                datetime.datetime.strptime(date, '%Y-%m-%d')
                expense_date = date
            
            expense = {
                "amount": amount_float,
                "category": category.strip(),
                "date": expense_date
            }
            
            self.data["expenses"].append(expense)
            self._save_data()
            return True
        except ValueError:
            raise ValueError("Invalid expense data")
    
    def get_total_spent(self) -> float:
        """
        Calculate total amount spent across all expenses.
        """
        return sum(expense["amount"] for expense in self.data["expenses"])
    
    def get_category_stats(self) -> Dict[str, float]:
        """
        Get spending statistics by category.
        """
        categories = {}
        for expense in self.data["expenses"]:
            category = expense["category"]
            categories[category] = categories.get(category, 0) + expense["amount"]
        return categories
    
    def get_period_stats(self, start_date: str, end_date: str) -> Dict[str, float]:
        """
        Get spending statistics for a specific period.
        """
        try:
            # Validate dates
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")
            
            period_expenses = [
                expense for expense in self.data["expenses"]
                if start_date <= expense["date"] <= end_date
            ]
            
            total_period = sum(expense["amount"] for expense in period_expenses)
            
            return {
                "total_spent": total_period,
                "expense_count": len(period_expenses)
            }
        except ValueError:
            raise ValueError("Invalid date format")
    
    def get_financial_summary(self) -> Dict[str, float]:
        """
        Get complete financial summary.
        """
        total_spent = self.get_total_spent()
        remaining = self.data["budget"] - total_spent
        
        return {
            "budget": self.data["budget"],
            "total_spent": total_spent,
            "remaining": remaining
        }


def validate_amount(amount_str: str) -> Tuple[bool, float]:
    """
    Validate and convert amount string to float.
    """
    try:
        amount = float(amount_str)
        return (True, amount) if amount >= 0 else (False, 0)
    except ValueError:
        return (False, 0)


def validate_date(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD).
    """
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def main():
    """Main application function."""
    print("=== Financial Tracker ===")
    
    data_file = input("Enter data file path (press Enter for default): ").strip()
    if not data_file:
        data_file = "financial_data.json"
    
    tracker = FinancialTracker(data_file)
    print(f"Data will be stored in: {os.path.abspath(data_file)}")
    
    while True:
        print("\n=== Main Menu ===")
        print("1. Set Budget")
        print("2. Add Expense")
        print("3. View Statistics")
        print("4. Exit")
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            amount_str = input("Enter your budget: ").strip()
            is_valid, amount = validate_amount(amount_str)
            if is_valid:
                tracker.set_budget(amount)
                print(f"Budget set to: {amount}")
            else:
                print("Invalid amount! Please enter a positive number.")
        
        elif choice == "2":
            amount_str = input("Enter amount spent: ").strip()
            is_valid, amount = validate_amount(amount_str)
            if not is_valid or amount <= 0:
                print("Invalid amount! Please enter a positive number.")
                continue
            
            category = input("Enter category: ").strip()
            if not category:
                print("Category cannot be empty!")
                continue
            
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date:
                date = None
            elif not validate_date(date):
                print("Invalid date format! Using today's date.")
                date = None
            
            tracker.add_expense(amount, category, date)
            print("Expense added successfully!")
        
        elif choice == "3":
            show_statistics(tracker)
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice! Please try again.")


def show_statistics(tracker: FinancialTracker):
    """Display financial statistics."""
    summary = tracker.get_financial_summary()
    categories = tracker.get_category_stats()
    
    print("\n=== Financial Summary ===")
    print(f"Budget: {summary['budget']}")
    print(f"Total Spent: {summary['total_spent']}")
    print(f"Remaining: {summary['remaining']}")
    
    print("\n=== Spending by Category ===")
    if categories:
        for category, amount in categories.items():
            print(f"{category}: {amount}")
    else:
        print("No expenses recorded.")
    
    print("\n=== Period Statistics ===")
    start_date = input("Enter start date (YYYY-MM-DD) or press Enter to skip: ").strip()
    if start_date:
        if validate_date(start_date):
            end_date = input("Enter end date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not end_date:
                end_date = datetime.date.today().isoformat()
            
            if validate_date(end_date):
                try:
                    period_stats = tracker.get_period_stats(start_date, end_date)
                    print(f"\nFrom {start_date} to {end_date}:")
                    print(f"Total spent: {period_stats['total_spent']}")
                    print(f"Number of expenses: {period_stats['expense_count']}")
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Invalid end date format!")
        else:
            print("Invalid start date format!")


if __name__ == "__main__":
    main()