import datetime
import re

def validate_rental_data(data):
    required_fields = ["rental_id", "car_model", "car_brand", "car_year", 
                      "rental_price", "rental_duration", "additional_info"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"
    
    if not isinstance(data["rental_id"], str):
        return False, "rental_id must be a string"
    if not isinstance(data["car_model"], str):
        return False, "car_model must be a string"
    if not isinstance(data["car_brand"], str):
        return False, "car_brand must be a string"
    if not isinstance(data["car_year"], int) or data["car_year"] < 1900 or data["car_year"] > datetime.datetime.now().year:
        return False, "car_year must be a valid year"
    if not isinstance(data["rental_price"], (int, float)) or data["rental_price"] <= 0:
        return False, "rental_price must be a positive number"
    if not isinstance(data["rental_duration"], int) or data["rental_duration"] <= 0:
        return False, "rental_duration must be a positive integer"
    if not isinstance(data["additional_info"], str):
        return False, "additional_info must be a string"
    
    return True, ""


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    # Минимум 8 символов
    # Хотя бы одна цифра
    # Хотя бы одна заглавная буква
    # Хотя бы одна строчная буква
    if len(password) < 8:
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    return True