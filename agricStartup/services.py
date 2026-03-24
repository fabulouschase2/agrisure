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