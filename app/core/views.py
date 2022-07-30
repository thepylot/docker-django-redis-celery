from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from.models import Prediction
from datetime import datetime, timedelta



current_date=datetime.today().strftime('%Y-%m-%d')
start_date=((datetime.today()-timedelta(3))).strftime('%Y-%m-%d')
end_date=((datetime.today()+ timedelta(3))).strftime('%Y-%m-%d')

def IndexView(request):
    top_predictions = Prediction.objects.filter(home_win__gte=60,date__gte=current_date,date__lte=end_date)|Prediction.objects.filter(away_win__gte=60,date__gte=current_date,date__lte=end_date)

    context ={
        'top_predictions':top_predictions,
        
    }
   
    return render(request,'index.html',context)

def PredictView(request,pk):
     league = Prediction.objects.filter(league=pk).filter(date__gte=current_date,date__lte=end_date)
     
     context ={
        'league':league,
        }
  
     return render(request,'predict.html',context)