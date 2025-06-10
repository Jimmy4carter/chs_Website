import json
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from hostel.forms import StudentEthosRecordForm
from accounts.models import CustomUser, FeedBackStaff, NotificationStaff, SessionYearModel, SiteControls, Staff, Students, Subjects
from hostel.models import Allocations, Hostel, Logbook, Rooms, StudentEthosRecords
from datetime import datetime
from django.db import transaction


# Create your views here.
@login_required
def hostel_home(request):
    # Retrieve data for cards
    male_hostel = Hostel.objects.filter(Sex='Male').first()
    female_hostel = Hostel.objects.filter(Sex='Female').first()

    # Retrieve data for accordion sections
    rooms_data = Rooms.objects.all()
    # Order reports_data based on the parsed rdate
    reports_data = Logbook.objects.all()
    reports_data = sorted(reports_data, key=lambda x: datetime.strptime(x.rdate, '%Y-%m-%d'))

    context = {
        'male_hostel': male_hostel,
        'female_hostel': female_hostel,
        'rooms_data': rooms_data,
        'reports_data': reports_data,
    }

    return render(request, 'hostel_home.html', context)

@login_required
def hostel_profile(request):
    if request.method!="POST":
        user=CustomUser.objects.get(id=request.user.id)
        tutor=Staff.objects.get(admin=user)
        return render(request,"hostel_profile.html",{"tutor":tutor})

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
                return HttpResponseRedirect(reverse("hostel_profile"))

        except:
            messages.error(request,"Failed To Update")
            return HttpResponseRedirect(reverse("hostel_profile"))
@login_required
def hostels_manage(request):
    if request.method!="POST":
        hostels=Hostel.objects.all()
        return render(request,"hostels_template.html",{"hostels":hostels})
    else:
        type = request.POST.get('cate')
        ids = request.POST.get('ID')
        name = request.POST.get("name")
        capacity = request.POST.get("capacity")
        rooms = request.POST.get("rooms")
        p1 = request.POST.get("p1")
        p2 = request.POST.get("p2")
        prefect = request.POST.get("prefect")

        try:
            check_exist=Hostel.objects.filter(id=ids)
            hp1=CustomUser.objects.get(username=p1)
            hpre=CustomUser.objects.get(username=prefect)
            hp=Students.objects.get(admin=hpre)
            if check_exist:
                check_exist=Hostel.objects.get(id=ids)
                check_exist.sex=type
                check_exist.name=name
                check_exist.capacity=capacity
                check_exist.room_count=rooms
                check_exist.hparent1=hp1
                check_exist.hparent2=p2
                check_exist.hprefect=hp
                check_exist.save()
                messages.success(request,"Hostel Details Successfully Updated")
                return HttpResponseRedirect(reverse("hostels_manage"))
            else:
                Hostel.objects.create(name=name,room_count=rooms,Sex=type,capacity=capacity,hparent1=hp1,hparent2=p2,hprefect=hp)            
                messages.success(request,"Hostel Successfully Added")
                return HttpResponseRedirect(reverse("hostels_manage"))
        except:
            messages.error(request,"Failed To Update/Add Hostel")
            return HttpResponseRedirect(reverse("hostels_manage"))
@login_required
def rooms_manage(request):
    if request.method!="POST":
        hostels=Hostel.objects.all()
        rooms=Rooms.objects.all()
        students = Students.objects.filter(class_id__in=[4, 5, 6])
        return render(request,"rooms.html",{"rooms":rooms,"hostels":hostels,"students":students})
    else:
        hostel = int(request.POST.get('hostel'))
        roomid = request.POST.get("roomid")
        roomname = request.POST.get("name")
        roomcap = request.POST.get("capacity")
        roomhead = request.POST.get("roomhead")

        try:
            check_exist = Rooms.objects.filter(id=roomid)
            if check_exist:
                check_exist = Rooms.objects.get(id=roomid)
                check_exist.name=roomname
                check_exist.capacity=roomcap
                check_exist.hostels=Hostel.objects.get(id=hostel)
                headid=CustomUser.objects.get(username=roomhead)
                check_exist.roomhead=Students.objects.get(admin=headid)
                check_exist.save()
                messages.success(request,"Room Details Successfully Updated")
                return HttpResponseRedirect(reverse("rooms_manage"))
            else:
                hostel=Hostel.objects.get(id=hostel)
                headid=CustomUser.objects.get(username=roomhead)
                rhead=Students.objects.get(admin=headid)
                Rooms.objects.create(name=roomname,roomhead=rhead,hostels=hostel,capacity=roomcap)
                messages.success(request,"Room Successfully Added")
                return HttpResponseRedirect(reverse("rooms_manage"))


        except:
            messages.error(request,"Failed To Update/Add Room")
            return HttpResponseRedirect(reverse("rooms_manage"))

@login_required          
def delete_room(request,item_id):
    try:
        dels=Rooms.objects.get(id=item_id)
        dels.delete()
        
        messages.info(request,"Entry Deleted Successfully, Check List Below TO Confirm")
        return HttpResponseRedirect(reverse("rooms_manage"))
    except:
        messages.error(request,"Failed To Delete Entry, Please Check and Try Again")
        return HttpResponseRedirect(reverse("rooms_manage"))
@login_required
def hostel_all_notification(request):
    staff=Staff.objects.get(admin=request.user.id)
    notification=NotificationStaff.objects.filter(staff_id=staff.id)
    return render(request,"all_notifcation.html",{"notifications":notification})

@login_required
def hostel_feedback(request):
    if request.method!="POST":
        staff_id=Staff.objects.get(admin=request.user.id)
        feedback_data=FeedBackStaff.objects.filter(staff_id=staff_id)
        return render(request,"staff_feedback_template.html",{"feedback_data":feedback_data})
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaff(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
             
            messages.success(request,"Feedback Successfully Sent")
            return HttpResponseRedirect(reverse("hostel_feedback"))
        except:
            messages.error(request,"Failed To Send Feedback")
            return HttpResponseRedirect(reverse("hostel_feedback"))
@login_required   
def allocate_room(request):
    if request.method!="POST":
        hostels = Hostel.objects.all()
        ses=SessionYearModel.objects.get(status=1)
        rooms=Rooms.objects.all()
        students = Students.objects.filter(class_id__in=[1, 2, 3, 4, 5, 6]).order_by('class_id')
        allo=Allocations.objects.filter(sessionid=ses)
        return render(request, "allocateroom_template.html",{"rooms":rooms,"hostels":hostels,"ses":ses,"allo":allo,"students":students})
    else:
        hostel=int(request.POST.get('hostel'))
        room=int(request.POST.get('room'))
        student=request.POST.get('studentid')
        rooms=Rooms.objects.get(id=room)
        ses=SessionYearModel.objects.get(status=1)
        student=CustomUser.objects.get(username=student)
        student=Students.objects.get(admin=student)
        allocator=Staff.objects.get(admin=request.user.id)
        checks=Allocations.objects.filter(sessionid=ses,student=student)
        if checks:
            allo=Allocations.objects.get(sessionid=ses,student=student)
            allo.room=rooms
            allo.allocator=allocator
            allo.save()
            messages.success(request,"Allocation Successfully Updated")
            return HttpResponseRedirect(reverse("allocate_room"))
        else:
            Allocations.objects.create(sessionid=ses,student=student,room=rooms,allocator=allocator)
            messages.success(request,"Allocation Successful")
            return HttpResponseRedirect(reverse("allocate_room"))

@login_required
@csrf_exempt
def get_rooms(request):
    hostel=int(request.POST.get('hostel'))
    rooms=Rooms.objects.filter(hostels=hostel)

    if rooms!=None:
        list_data=[]
        for rooms in rooms:
            data_small={"id":rooms.id,"name":rooms.name,}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    else:
        messages.Error(request,"No ROOMs for selected HOSTEL")

        
@login_required
def view_logs(request):
    reports=Logbook.objects.all()
    return render(request,"viewlogs.html",{"reports":reports})
@login_required
def report_preview(request, report_id):
    reports=Logbook.objects.get(id=report_id)
    return render(request,"report_preview.html",{"reports":reports})
@login_required
def hostel_student(request):
    ses=SessionYearModel.objects.get(status=1)
    get_students = Students.objects.all()
    active_student = get_students.filter(class_id__in=(1,2,3,4,5,6)).order_by('class_id')
    return render(request,"students_template.html",{"active_student":active_student,"ses":ses})

@login_required
@csrf_exempt
def create_log(request):
    if request.method != "POST":
        return render(request, "createlog_template.html")
    else:
        try:
            date = request.POST.get("dateof")
            report = request.POST.get("cod")
            ses = SessionYearModel.objects.get(status=1)
            reporter = Staff.objects.get(admin=request.user.id)

            Logbook.objects.create(rdate=date, reporter=reporter, report=report, sessionid=ses)
            return JsonResponse({'success': True})
        except SessionYearModel.DoesNotExist:
            return JsonResponse({'error': 'Session year does not exist'}, status=400)
        except Staff.DoesNotExist:
            return JsonResponse({'error': 'Reporter does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
            

def hostel_grading(request):
    if request.method == 'POST':
        form = StudentEthosRecordForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request,"Ethos Successfully Added, you can check to view")
            except Exception as e:
                return HttpResponse(f"Error occurred while saving the form data: {str(e)}")
            return HttpResponseRedirect(reverse("hostel_grading"))
        else:
            print(form.errors) 
    else:
        form = StudentEthosRecordForm()
    res_type = SiteControls.objects.get(c_code='RT')
    if res_type.status == 0:
        result_type = "First Half"
    else:
        result_type = "End of Term"
    ethos_records = StudentEthosRecords.objects.filter(term__status=1, session_year__status=1, result_type=res_type.status)
     # Calculate sum of positive and negative ethos for each record
    for record in ethos_records:
        positive_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness'))])
        negative_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal'))])
        record.total_positive_ethos = positive_ethos_sum
        record.total_negative_ethos = negative_ethos_sum
        record.total_ethos = positive_ethos_sum - negative_ethos_sum
    return render(request, 'hostel_grade.html', {'form': form, 'ethos_records': ethos_records, 'result_type':result_type})

