from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Crop, FarmInput, LoanRequest
from .serializers import RegisterSerializer
from .services import (
    calculate_yield, calculate_risk, loan_decision,
    calculate_profit, get_weather_factor, enhanced_risk_score
)
from .interswitch_services import (
    get_customer_demographics, get_financial_history,
    get_financial_habits, get_credit_score,
    get_loan_offers, accept_loan_offer, verify_bank_account, update_loan_status
)

# ---------- Authentication ----------
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------- Crops ----------
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

# ---------- Simulation (without Interswitch) ----------
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

# ---------- Loan Request (with Interswitch integration) ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_loan(request):
    crop_id = request.data.get("crop_id")
    farm_size = request.data.get("farm_size")
    input_cost = request.data.get("input_cost")
    season_duration = request.data.get("season_duration", 12)
    weather = request.data.get("weather", "normal")
    # Optionally, farmer can provide phone/BVN for credit score
    msisdn = request.data.get("msisdn")  # for credit score

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

    # Basic yield and risk
    weather_factor = get_weather_factor(weather)
    predicted_yield = calculate_yield(farm_size, crop.average_yield_per_hectare, weather_factor)
    profit = calculate_profit(predicted_yield, crop.market_price_per_ton, input_cost)

    # Get credit score if msisdn provided
    credit_score = None
    if msisdn:
        try:
            credit_data = get_credit_score(msisdn)
            if credit_data.get('creditScores') and len(credit_data['creditScores']) > 0:
                credit_score = int(credit_data['creditScores'][0]['score'])
        except Exception as e:
            # Log error but continue – use fallback
            pass

    # Enhanced risk using credit score if available
    risk = enhanced_risk_score(input_cost, predicted_yield, credit_score)
    decision = loan_decision(risk)

    # Save farm input and loan request
    FarmInput.objects.create(
        farmer=request.user,
        crop=crop,
        farm_size=farm_size,
        input_cost=input_cost,
        season_duration=season_duration
    )
    loan = LoanRequest.objects.create(
        farmer=request.user,
        amount_requested=input_cost,
        status=decision,
        risk_level=risk
    )

    # If loan is approved, we could call Interswitch to actually disburse funds
    # For now just store it.

    return Response({
        "message": "Loan request saved",
        "predicted_yield": round(predicted_yield, 2),
        "risk": risk,
        "loan_decision": decision,
        "profit": round(profit, 2),
        "credit_score": credit_score  # optional
    }, status=status.HTTP_201_CREATED)

# ---------- Interswitch Data Endpoints ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_customer(request):
    id_type = request.data.get('identificationType')
    id_number = request.data.get('identificationNumber')
    if not id_type or not id_number:
        return Response({'error': 'identificationType and identificationNumber required'}, status=400)
    try:
        result = get_customer_demographics(id_type, id_number)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def credit_score(request):
    msisdn = request.query_params.get('msisdn')
    if not msisdn:
        return Response({'error': 'msisdn required'}, status=400)
    try:
        result = get_credit_score(msisdn)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def financial_history(request):
    id_number = request.data.get('identificationNumber')
    start = request.data.get('startYearMonth')
    end = request.data.get('endYearMonth')
    if not all([id_number, start, end]):
        return Response({'error': 'identificationNumber, startYearMonth, endYearMonth required'}, status=400)
    try:
        result = get_financial_history(id_number, start, end)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def financial_habits(request):
    id_number = request.data.get('identificationNumber')
    year_month = request.data.get('yearMonth')
    if not id_number or not year_month:
        return Response({'error': 'identificationNumber and yearMonth required'}, status=400)
    try:
        result = get_financial_habits(id_number, year_month)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# ---------- Interswitch Lending Endpoints ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_offers(request):
    customer_id = request.data.get('customerId')
    if not customer_id:
        return Response({'error': 'customerId required'}, status=400)
    try:
        result = get_loan_offers(customer_id)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_loan(request):
    required = ['customerId', 'offerId', 'destinationAccountNumber', 'destinationBankCode', 'loanReferenceId']
    data = {k: request.data.get(k) for k in required}
    if not all(data.values()):
        return Response({'error': f'Missing fields: {required}'}, status=400)
    try:
        result = accept_loan_offer(**data)
        # Optionally store interswitch_loan_id in LoanRequest
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_account(request):
    bank_code = request.query_params.get('bank_code')
    account_number = request.query_params.get('account_number')
    if not bank_code or not account_number:
        return Response({'error': 'bank_code and account_number required'}, status=400)
    try:
        result = verify_bank_account(bank_code, account_number)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_loan_status(request):
    loan_id = request.data.get('loanId')
    status_val = request.data.get('status')
    if not loan_id or not status_val:
        return Response({'error': 'loanId and status required'}, status=400)
    try:
        result = update_loan_status(loan_id, status_val)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)