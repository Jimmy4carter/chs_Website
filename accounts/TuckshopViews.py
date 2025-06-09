from datetime import datetime
import json
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyexpat.errors import messages
from django.contrib import messages
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views import View
from .forms import AddQuantityForm, AddQuantityFormSet, DamageReportForm, DateForm, ItemForm, StockOperationForm
from django.forms import formset_factory

from accounts.models import Classes, CustomUser, DamageReport, FeedBackStaff, Item, SessionYearModel, Staff, Stock, StockLog, Students



def tuckshop_home(request):
    get_students = Students.objects.all()
    all_students = get_students.count()
    active_student = get_students.filter(class_id__in=(1,2,3,4,5,6)).count()
    all_staff = Staff.objects.all().count()

    return render(request,"tuckshop_template/tuckshop_home.html", {"all_students":all_students,"active_student":active_student,"all_staff":all_staff})

def tuckshop_staff(request):
    staff=Staff.objects.all()
    return render(request,"tuckshop_template/tuckshop_staff.html",{"staff":staff})

def tuckshop_students(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"adminsec_template/adminsec_students.html",{"sessions":sessions,"classes":classes})

@csrf_exempt
def tuckshop_get_students(request):
    session_id=request.POST.get("session_id")
    class_ids=request.POST.get("classid")
    all_stud=class_ids+session_id
    if all_stud=='00':
        students=Students.objects.all()
    elif  session_id=='0':
        the_class=Classes.objects.get(id=class_ids)
        students=Students.objects.filter(class_id=the_class)
    elif class_ids=='0':   
        the_session=SessionYearModel.objects.get(id=session_id)
        students=Students.objects.filter(session_year_id=the_session)
    else:
        students=Students.objects.filter(class_id=class_ids,session_year_id=session_id)

    if students!=None:
        list_data=[]
        for student in students:
            data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"gender":student.gender,"profile_pic":str(student.profile_pic),"parent_phone":student.parent_phone,"parent_email":student.parent_email,"parent_name":student.parent_name}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    else:
        messages.Error(request,"No Records Found")


def tuckshop_profile(request):
    
    if request.method!="POST":
        user=CustomUser.objects.get(id=request.user.id)
        tutor=Staff.objects.get(admin=user)
        return render(request,"tuckshop_template/tuckshop_profile.html", {"user":user,"tutor":tutor})
    else:
        address=request.POST.get("address")
        password=request.POST.get("password")

        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            if password!=None and password!="":
                customuser.set_password(password)
                customuser.save()
                staff=Staff.objects.get(admin=customuser.id)
                staff.address=address
                staff.save()
                messages.success(request,"Profile Successfully Updated")
                return HttpResponseRedirect(reverse("login"))
            else:
                staff=Staff.objects.get(admin=customuser.id)
                staff.address=address
                staff.save()
                messages.success(request,"Profile Successfully Updated")
                return HttpResponseRedirect(reverse("tuckshop_profile"))

        except:
            messages.error(request,"Failed To Update")
            return HttpResponseRedirect(reverse("staff_profile"))
def tuckshop_feedback(request):
    staff_id=Staff.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaff.objects.filter(staff_id=staff_id)
    return render(request,"tuckshop_template/tuckshop_feedback_template.html",{"feedback_data":feedback_data})

def tuckshop_feedback_save(request):

    if request.method!="POST":
        return HttpResponseRedirect(reverse("tuckshop_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaff(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
             
            messages.success(request,"Feedback Successfully Sent")
            return HttpResponseRedirect(reverse("tuckshop_feedback"))
        except:
            messages.error(request,"Failed To Send Feedback")
            return HttpResponseRedirect(reverse("tuckshop_feedback"))

def tuckshop_students(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"tuckshop_template/tuckshop_students.html",{"sessions":sessions,"classes":classes})

def m_analysis(request):
    return render(request,"tuckshop_template/monthly_analysis.html")

def a_analysis(request):
    return render(request,"tuckshop_template/annual_analysis.html")

def t_requisition(request):
    return render(request,"tuckshop_template/requisition.html")

class AddItemView(View):
    template_name = 'tuckshop_template/items.html'  # Replace with your template name

    def get(self, request):
        form = ItemForm()
        items = Item.objects.all()
        return render(request, self.template_name, {'form': form, 'items': items})

    def post(self, request):
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            data = {
                'success': True,
                'message': 'Item added successfully!',
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'brand': item.brand,
                    'package_type': item.get_package_type_display(),
                    'description': item.description,
                    'note': item.note,
                    'expected_marketprice': item.expected_marketprice,
                }
            }
        else:
            data = {
                'success': False,
                'message': 'Error adding item.',
                'errors': form.errors
            }

        return JsonResponse(data)






StockFormSet = formset_factory(StockOperationForm, extra=1)

def StockOperationView(request):
    date_form = DateForm()
    stock_logs = StockLog.objects.filter(stock_type='incoming').values('general_date').distinct().order_by('-general_date')
    formset = AddQuantityFormSet(prefix='quantity')
    if request.method == 'POST':
        stock_formset = StockFormSet(request.POST, prefix='stock')
        date_form = DateForm(request.POST, prefix='date')
        print(stock_formset)

        if stock_formset.is_valid() and date_form.is_valid():
            stock_date = date_form.cleaned_data['date']
            general_note = date_form.cleaned_data['general_note']
            stock_type = "incoming"

            for form in stock_formset:
                if form.cleaned_data.get('item') and form.cleaned_data.get('quantity'):
                    stock_instance = form.save(commit=False)
                    stock_instance.date = stock_date
                    stock_instance.save()

                    stock_log = StockLog.objects.create(
                        stock=stock_instance,
                        general_note=general_note,
                        stock_type=stock_type,
                        general_date=stock_date,
                        quantity_at_entry=stock_instance.quantity,
                        unit_price_at_entry=stock_instance.price,
                        quantity_after_entry =stock_instance.quantity,
                        unit_price_after_entry =stock_instance.price
                    )

            # Redirect to the same view to allow adding more entries
            messages.success(request,"Successfully")
            return redirect('add_stock')
    else:
        stock_formset = StockFormSet(prefix='stock')
        date_form = DateForm(prefix='date')
        

    return render(request, 'tuckshop_template/incoming_stock.html', {'date_form': date_form, 'formset': formset, 'stock_formset': stock_formset, 'date_form': date_form, 'stock_logs': stock_logs})




def add_quantity(request):
    stock_logs = StockLog.objects.filter(stock_type='incoming').values('general_date').distinct().order_by('-general_date')
    if request.method == 'POST':
        date_form = DateForm(request.POST, prefix='date')
        formset = AddQuantityFormSet(request.POST, prefix='quantity')

        if formset.is_valid():
            general_note = request.POST['date-general_note']
            date = request.POST.get('date-date')
            
            for form in formset:
                if form.cleaned_data:
                    item_id = form.cleaned_data['item'].id
                    quantity_to_add = form.cleaned_data['quantity']
                    price = form.cleaned_data['price']
                    
                    # Get the existing stock item
                    stock = Stock.objects.get(item__id=item_id)

                    old_price = stock.price
                    old_quantity = stock.quantity

                    # Update stock quantity and price directly
                    stock.quantity += quantity_to_add
                    stock.price = price

                    # Save the updated stock
                    stock.save()

                    # Create log entry for the updated stock instance
                    StockLog.objects.create(
                        stock=stock,
                        general_note=general_note,
                        stock_type='incoming',
                        general_date=date,
                        quantity_at_entry=old_quantity,
                        quantity_after_entry=stock.quantity,
                        unit_price_at_entry=old_price,
                        unit_price_after_entry=stock.price
                    )

            messages.success(request, 'Stock quantity added successfully.')
            return redirect('add_stock')
        else:
           # Capture the error messages
            formset_errors = formset.errors
            date_form_errors = date_form.errors
            
            # Add the error messages to the messages framework
            messages.error(request, f"Error adding stock quantity. Formset errors: {formset_errors}. Date form errors: {date_form_errors}")

    else:
        date_form = DateForm(prefix='date')
        formset = AddQuantityFormSet(prefix='quantity')
        stock_formset = StockFormSet(prefix='stock')

        return render(request, 'tuckshop_template/incoming_stock.html',  {'date_form': date_form, 'formset': formset, 'stock_formset': stock_formset, 'date_form': date_form, 'stock_logs': stock_logs})


def update_stock(request):
    stocks = Stock.objects.all()

    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date', '')
        
        if not selected_date_str:
            return HttpResponse("Error: Selected date not provided")

        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        
        selected_stocks = request.POST.getlist('selected_stocks')
        general_note = request.POST.get('general_note', '')
        
        # Update stocks and create log entries
        for stock_id in selected_stocks:
            stock = Stock.objects.get(id=stock_id)
            quantity_to_update = int(request.POST.get(f'quantity_{stock_id}', 0))
            
            if quantity_to_update > 0 and quantity_to_update <= stock.quantity:
                # Update stock quantity and create log entry
                stock.quantity -= quantity_to_update
                stock.save()
                
                StockLog.objects.create(
                    stock=stock,
                    general_note=general_note,
                    stock_type='outgoing',
                    general_date=selected_date,
                    quantity_at_entry=quantity_to_update,
                    quantity_after_entry=stock.quantity,
                    unit_price_at_entry=stock.price,
                    unit_price_after_entry=stock.price  # Assuming unit price remains the same
                )

        # Redirect to the same view to refresh the page
        return redirect('update_stock')

    # Fetch only distinct dates with outgoing stock_type
    stock_logs = StockLog.objects.filter(stock_type='outgoing').values('general_date').distinct().order_by('-general_date')

    return render(request, 'tuckshop_template/outgoing_stock.html', {'stocks': stocks,'stock_logs': stock_logs})





def view_report(request):
    selected_date = request.POST.get('selected_date')
    selected_type = request.POST.get('selected_type')
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Query to get all stock logs for the specified date and type
    stock_logs = StockLog.objects.filter(general_date=selected_date, stock_type=selected_type)

    # Calculate total quantity, total price, and average unit price
    total_quantity = stock_logs.aggregate(total_quantity=Sum('quantity_after_entry'))['total_quantity']
    total_price = stock_logs.aggregate(total_price=Coalesce(Sum(ExpressionWrapper(F('quantity_after_entry') * F('unit_price_after_entry'), output_field=fields.DecimalField())), 0, output_field=fields.DecimalField()))['total_price']
    average_unit_price = stock_logs.aggregate(average_unit_price=Coalesce(Sum(F('unit_price_after_entry') / total_quantity, output_field=fields.DecimalField()), 0, output_field=fields.DecimalField()))['average_unit_price']
    
    
    for log in stock_logs:
        # Calculate the difference between unit_price_after_entry and unit_price_at_entry
        log.price_difference = log.unit_price_after_entry - log.unit_price_at_entry
        
    # Render the report template with additional context
    return render(request, 'tuckshop_template/report_incoming.html', {
        'selected_date': selected_date,
        'selected_type': selected_type,
        'stock_logs': stock_logs,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'average_unit_price': average_unit_price,
    })



def damage_report(request):
    damage_reports = DamageReport.objects.all().order_by('-date')
    if request.method == 'POST':
        form = DamageReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('damage_report')  # Redirect to the list of damage reports
    else:
        form = DamageReportForm()

    return render(request, 'tuckshop_template/damage_report.html', {'form': form, 'damage_reports':damage_reports})
