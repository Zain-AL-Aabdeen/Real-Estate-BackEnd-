from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serializers
import joblib
import os

# تحميل موديل الذكاء الاصطناعي تلقائياً عند تشغيل السيرفر
# تأكد من وضع ملف الموديل الخاص بك باسم 'property_model.pkl' داخل مجلد باسم 'ml_models' في تطبيق prediction_app
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models/property_model.pkl')

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"تحذير: لم يتم العثور على ملف الموديل في المسار المذكور أو حدث خطأ أثناء تحميله: {e}")

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
            # مثال افتراضي بناءً على البيانات القادمة من الـ الفرونت:
            features = [[
                data.get('Area_m2'), 
                data.get('Rooms'), 
                data.get('Bathrooms'),
                data.get('Floor'),
                data.get('Building_Floor'),
                data.get('Age_Years')
                # أضف هنا باقي الحقول بعد تحويلها لأرقام إذا كان الموديل يتطلب ذلك
            ]]
            
            calculated_price = model.predict(features)[0]
            data['price'] = int(calculated_price)
        except Exception as e:
            return Response({"error": f"فشل الموديل في حساب السعر المتوقع: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # قيمة افتراضية في حال عدم شحن الموديل بعد للتجربة النظيفة
        data['price'] = 150000 

    # 2. التحقق من صحة البيانات وحفظ العملية في جدول الـ History
    val = serializers.HistorySerializer(data=data)
    if val.is_valid():
        val.save(user=request.user, price=data['price']) # تمرير القيم المحمية تلقائياً
        return Response({"price": data['price']}, status=status.HTTP_200_OK)
            
    return Response(val.errors, status=status.HTTP_400_BAD_REQUEST)