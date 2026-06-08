import os
import joblib
import traceback  # تم استدعاؤها لطباعة الخطأ بدقة
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from . import models
from . import serializers

# 1. جلب مسار المجلد الحالي وتحديد اسم ملف الموديل
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'property_model.pkl')

load_error_message = None
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✅ تم تحميل موديل الذكاء الاصطناعي بنجاح!")
    else:
        load_error_message = f"ملف الموديل غير موجود في مجلد ml_models"
        print("⚠️ " + load_error_message)
except Exception as e:
    model = None
    load_error_message = f"فشل تحميل الموديل بسبب: {str(e)}"
    print("\n❌ === تقرير الخطأ الفعلي من داخل الموديل ===")
    traceback.print_exc()  # سيطبع الخطأ الحقيقي كاملاً هنا
    print("===========================================\n")

# قواميس التشفير النصي
LOCATION_MAP = {'akrama': 0, 'al-nuzha': 1, 'muhajreen': 2}
CONDITION_MAP = {'delux': 0, 'normal': 1, 'super-delux': 2}
ORIENTATION_MAP = {
    'east': 0, 'east-west': 1, 'north': 2, 'north-east': 3, 'north-west': 4,
    'south': 5, 'south-east': 6, 'south-north': 7, 'south-west': 8, 'west': 9
}
FURNISHED_MAP = {'furnished': 0, 'unfurnished': 1}
SERVICES_MAP = {
    'bus_station': 0, 'hospital': 1, 'main_street': 2, 'school': 3, 'shopping_center': 4
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def User_History(request):
    user = request.user
    return Response(serializers.HistorySerializer(models.History.objects.filter(user_id=user.id), many=True).data)

@swagger_auto_schema(
    method='post',
    request_body=serializers.HistorySerializer,
    responses={200: "price: integer"}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Get_Price(request):
    data = request.data.copy()
    data["user"] = request.user.id
    
    if model is None:
        return Response({
            "error": "لم يتم تحميل موديل الذكاء الاصطناعي بنجاح في السيرفر.",
            "details": load_error_message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    val = serializers.HistorySerializer(data=data)
    if val.is_valid():
        validated_data = val.validated_data
        
        loc_raw = validated_data.get('Location')
        cond_raw = validated_data.get('Condition')
        orient_raw = validated_data.get('Orientation')
        furn_raw = validated_data.get('Furnished')
        services_raw = validated_data.get('Services', [])
        
        loc_encoded = LOCATION_MAP.get(loc_raw, 0)
        cond_encoded = CONDITION_MAP.get(cond_raw, 1)
        orient_encoded = ORIENTATION_MAP.get(orient_raw, 0)
        furn_encoded = FURNISHED_MAP.get(furn_raw, 1)
        
        service_single = services_raw[0] if isinstance(services_raw, list) and len(services_raw) > 0 else 'main_street'
        service_encoded = SERVICES_MAP.get(service_single, 2)

        try:
            features = [[
                loc_encoded,
                validated_data.get('Area_m2'),
                validated_data.get('Age_Years'),
                validated_data.get('Rooms'),
                validated_data.get('Floor'),
                cond_encoded,
                orient_encoded,
                validated_data.get('Building_Floor'),
                validated_data.get('Bathrooms'),
                furn_encoded,
                service_encoded
            ]]
            
            prediction = model.predict(features)[0]
            calculated_price = int(prediction)
            
            val.save(user=request.user, price=calculated_price) 
            return Response({"price": calculated_price}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": f"فشل الموديل في حساب السعر المتوقع: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # ... الكود الحالي
    
    # 💡 أضيفي هذا السطر السحري هنا لقراءة الأخطاء في الترمينال فوراً
    print("❌ أخطاء السيريالايزر هي:", val.errors) 
    
    return Response(val.errors, status=status.HTTP_400_BAD_REQUEST)
    