from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serializers
import joblib
import os

# 1. جلب مسار المجلد الحالي للتطبيق بشكل صحيح باستخدام __file__
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# تحديد المسار المتوقع للموديل بدقة
MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'property_model.pkl')

# محاولة تحميل الموديل بذكاء دون التسبب في انهيار السيرفر
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✅ تم تحميل موديل الذكاء الاصطناعي بنجاح!")
    else:
        # محاولة أخرى في حال كان المجلد بالمفرد ml_model
        ALT_PATH = os.path.join(BASE_DIR, 'ml_model', 'property_model.pkl')
        if os.path.exists(ALT_PATH):
            model = joblib.load(ALT_PATH)
            print("✅ تم تحميل موديل الذكاء الاصطناعي من المسار البديل!")
        else:
            model = None
            print("⚠️ تحذير: ملف الموديل property_model.pkl غير موجود في المجلدات المحددة.")
except Exception as e:
    model = None
    print(f"تحذير: حدث خطأ أثناء تحميل ملف الموديل: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def User_History(request):
    user = request.user
    return Response(serializers.HistorySerializer(models.History.objects.filter(user_id=user.id), many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Get_Price(request):
    data = request.data.copy()
    data["user"] = request.user.id
    
    # 1. تجهيز البيانات وتوقع السعر عبر موديل الذكاء الاصطناعي
    if model is not None:
        try:
            # قم بترتيب الخصائص (Features) هنا تماماً بالشكل والترتيب الرقمي الذي تدرب عليه الموديل الخاص بك
            features = [[
                data.get('Area_m2'), 
                data.get('Rooms'), 
                data.get('Bathrooms'),
                data.get('Floor'),
                data.get('Building_Floor'),
                data.get('Age_Years')
            ]]
            
            calculated_price = model.predict(features)[0]
            data['price'] = int(calculated_price)
        except Exception as e:
            return Response({"error": f"فشل الموديل في حساب السعر المتوقع: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # قيمة افتراضية في حال عدم وجود الملف أونلاين لكي لا يتوقف السيرفر عن العمل ويفتح السويدجر
        data['price'] = 150000 

    # 2. التحقق من صحة البيانات وحفظ العملية في جدول الـ History
    val = serializers.HistorySerializer(data=data)
    if val.is_valid():
        val.save(user=request.user, price=data['price']) 
        return Response({"price": data['price']}, status=status.HTTP_200_OK)
            
    return Response(val.errors, status=status.HTTP_400_BAD_REQUEST)