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
    return 1.0  # normal

def enhanced_risk_score(input_cost, predicted_yield, credit_score, financial_history):
    """
    Combine loan-to-revenue ratio with external credit data.
    """
    ratio_risk = calculate_risk(input_cost, predicted_yield)
    
    # Adjust risk based on credit score (higher score = lower risk)
    if credit_score is not None and credit_score > 50:
        credit_risk = "Low"
    elif credit_score and credit_score > 30:
        credit_risk = "Medium"
    else:
        credit_risk = "High"
    
    # Combine both risks (simplified example)
    if ratio_risk == "Low" and credit_risk == "Low":
        return "Low"
    elif ratio_risk == "High" or credit_risk == "High":
        return "High"
    return "Medium"