"""Shared pytest fixtures for the Swiggy analytics project."""

from __future__ import annotations

import pandas as pd


def make_orders_df() -> pd.DataFrame:
    """Small deterministic order dataset that exercises analytics edge cases."""
    return pd.DataFrame(
        [
            {
                "State": "Karnataka",
                "City": "Bengaluru",
                "Location": "Indiranagar",
                "Order Date": "2025-01-05",
                "Restaurant Name": "Alpha",
                "Category": "Biryani",
                "Dish Name": "Veg Biryani",
                "Price (INR)": 150,
                "Rating": 4.5,
                "Rating Count": 20,
            },
            {
                "State": "Karnataka",
                "City": "Bengaluru",
                "Location": "Indiranagar",
                "Order Date": "2025-01-20",
                "Restaurant Name": "Alpha",
                "Category": "Biryani",
                "Dish Name": "Chicken Biryani",
                "Price (INR)": 350,
                "Rating": 4.2,
                "Rating Count": 15,
            },
            {
                "State": "Maharashtra",
                "City": "Mumbai",
                "Location": "Bandra",
                "Order Date": "2025-02-10",
                "Restaurant Name": "Beta",
                "Category": "Pizza",
                "Dish Name": "Paneer Pizza",
                "Price (INR)": 550,
                "Rating": 4.7,
                "Rating Count": 30,
            },
            {
                "State": "Maharashtra",
                "City": "Mumbai",
                "Location": "Bandra",
                "Order Date": "2025-02-18",
                "Restaurant Name": "Gamma",
                "Category": "Curry",
                "Dish Name": "Egg Curry",
                "Price (INR)": 220,
                "Rating": 4.0,
                "Rating Count": 10,
            },
            {
                "State": "Delhi",
                "City": "New Delhi",
                "Location": "Connaught Place",
                "Order Date": "2025-03-01",
                "Restaurant Name": "Alpha",
                "Category": "Dessert",
                "Dish Name": "Eggless Cake",
                "Price (INR)": 900,
                "Rating": 4.8,
                "Rating Count": 25,
            },
            {
                "State": "Delhi",
                "City": "New Delhi",
                "Location": "Connaught Place",
                "Order Date": "2025-03-12",
                "Restaurant Name": "Gamma",
                "Category": "Meals",
                "Dish Name": "Non-Veg Meal Combo",
                "Price (INR)": 1200,
                "Rating": 3.9,
                "Rating Count": 8,
            },
        ]
    )
