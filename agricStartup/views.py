from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Crop, FarmInput, LoanRequest
from .serializers import RegisterSerializer
from .services import (
    calculate_yield, calculate_risk, loan_decision,
    calculate_profit, get_weather_factor
)

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def crop_list(request):
    crops = Crop.objects.all()
    data = [{
        "id": c.id,
        "name": c.name,
        "yield_per_hectare": c.average_yield_per_hectare,
        "market_price": c.market_price_per_ton
    } for c in crops]
    return Response(data)

@api_view(['POST'])
def simulate(request):
    crop_id = request.data.get("crop_id")
    farm_size = request.data.get("farm_size")
    input_cost = request.data.get("input_cost")
    weather = request.data.get("weather", "normal")

    if not all([crop_id, farm_size, input_cost]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        crop = Crop.objects.get(id=crop_id)
    except Crop.DoesNotExist:
        return Response({"error": "Invalid crop_id"}, status=status.HTTP_404_NOT_FOUND)

    try:
        farm_size = float(farm_size)
        input_cost = float(input_cost)
    except (TypeError, ValueError):
        return Response({"error": "Invalid numeric values"}, status=status.HTTP_400_BAD_REQUEST)

    weather_factor = get_weather_factor(weather)
    predicted_yield = calculate_yield(farm_size, crop.average_yield_per_hectare, weather_factor)
    risk = calculate_risk(input_cost, predicted_yield)
    decision = loan_decision(risk)
    profit = calculate_profit(predicted_yield, crop.market_price_per_ton, input_cost)

    return Response({
        "predicted_yield": round(predicted_yield, 2),
        "risk": risk,
        "loan_decision": decision,
        "profit": round(profit, 2),
        "market_price": crop.market_price_per_ton
    })

@api_view(['POST'])
def request_loan(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    crop_id = request.data.get("crop_id")
    farm_size = request.data.get("farm_size")
    input_cost = request.data.get("input_cost")
    season_duration = request.data.get("season_duration", 12)
    weather = request.data.get("weather", "normal")

    if not all([crop_id, farm_size, input_cost]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        crop = Crop.objects.get(id=crop_id)
    except Crop.DoesNotExist:
        return Response({"error": "Invalid crop_id"}, status=status.HTTP_404_NOT_FOUND)

    try:
        farm_size = float(farm_size)
        input_cost = float(input_cost)
        season_duration = int(season_duration)
    except (TypeError, ValueError):
        return Response({"error": "Invalid numeric values"}, status=status.HTTP_400_BAD_REQUEST)

    weather_factor = get_weather_factor(weather)
    predicted_yield = calculate_yield(farm_size, crop.average_yield_per_hectare, weather_factor)
    risk = calculate_risk(input_cost, predicted_yield)
    decision = loan_decision(risk)
    profit = calculate_profit(predicted_yield, crop.market_price_per_ton, input_cost)

    FarmInput.objects.create(
        farmer=request.user,
        crop=crop,
        farm_size=farm_size,
        input_cost=input_cost,
        season_duration=season_duration
    )

    LoanRequest.objects.create(
        farmer=request.user,
        amount_requested=input_cost,
        status=decision,
        risk_level=risk
    )

    return Response({
        "message": "Loan request saved",
        "predicted_yield": round(predicted_yield, 2),
        "risk": risk,
        "loan_decision": decision,
        "profit": round(profit, 2)
    }, status=status.HTTP_201_CREATED)