def calculate_yield(farm_size, yield_per_hectare, weather_factor=1.0):
    return farm_size * yield_per_hectare * weather_factor

def calculate_risk(input_cost, predicted_yield):
    if predicted_yield <= 0:
        return "High"
    ratio = input_cost / predicted_yield
    if ratio < 20000:
        return "Low"
    elif ratio < 50000:
        return "Medium"
    return "High"

def loan_decision(risk):
    if risk == "Low":
        return "approved"
    elif risk == "Medium":
        return "conditional"
    return "rejected"

def calculate_profit(predicted_yield, market_price, input_cost):
    return (predicted_yield * market_price) - input_cost

def get_weather_factor(weather):
    weather = weather.lower()
    if weather == "good":
        return 1.2
    elif weather == "bad":
        return 0.7
    return 1.0

def enhanced_risk_score(input_cost, predicted_yield, credit_score):
    """
    Combine your ratio risk with Interswitch credit score.
    credit_score: integer (e.g., 0-100) or None if unavailable.
    """
    ratio_risk = calculate_risk(input_cost, predicted_yield)

    # Map credit score to risk level
    if credit_score is not None and credit_score > 50:
        credit_risk = "Low"
    elif credit_score is not None and credit_score > 30:
        credit_risk = "Medium"
    else:
        credit_risk = "High"   # missing or low score

    # Combine (priority: if either is High -> High, if both Low -> Low, else Medium)
    if ratio_risk == "High" or credit_risk == "High":
        return "High"
    elif ratio_risk == "Low" and credit_risk == "Low":
        return "Low"
    else:
        return "Medium"