from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse


class LoginCheckMiddleware(MiddlewareMixin):
    
    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename=view_func.__module__
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "accounts.AdminViews":
                    pass
                elif modulename == "accounts.views" or "accounts.PublicViews" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("admin_home"))

            elif user.user_type == "2":
                if modulename == "accounts.TurtorViews":
                    pass
                elif modulename == "accounts.views" or "accounts.PublicViews" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("tutors_home"))

            elif user.user_type == "3":
                if modulename == "accounts.StudentViews" :
                    pass
                elif modulename == "accounts.views" or modulename == "django.views.static" or modulename == "publicsite.PublicViews" or modulename == "paystackpayments.views" or modulename == "onlinecbt.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("students_home"))
            elif user.user_type == "4":
                if modulename == "accounts.PrincipalViews" :
                    pass
                elif modulename == "accounts.views" or modulename == "django.views.static" or modulename == "publicsite.PublicViews":
                    pass
                else:
                    return HttpResponseRedirect(reverse("principal_home"))

            elif user.user_type == "5":
                if modulename == "accounts.AdminsecViews" :
                    pass
                elif modulename == "accounts.views" or modulename == "django.views.static" or modulename == "publicsite.PublicViews":
                    pass
                else:
                    return HttpResponseRedirect(reverse("adminsec_home"))
                    
            elif user.user_type == "7":
                if modulename == "hostel.HostelViews" :
                    pass
                elif modulename == "accounts.views" or modulename == "django.views.static" or modulename == "publicsite.PublicViews":
                    pass
                else:
                    return HttpResponseRedirect
                    
            elif user.user_type == "8":
                if modulename == "accounts.TuckshopViews" :
                    pass
                elif modulename == "accounts.views" or modulename == "django.views.static" or modulename == "publicsite.PublicViews":
                    pass
                else:
                    return HttpResponseRedirect(reverse("tuckshop_home"))

            elif user.user_type == "7":
                if modulename == "hostel.HostelViews" :
                    pass
                elif modulename == "accounts.views" or modulename == "django.views.static" or modulename == "publicsite.PublicViews":
                    pass
                else:
                    return HttpResponseRedirect(reverse("hostel_home"))

        else:
            if request.path == reverse("login") or request.path == reverse("doLogin") or "publicsite.PublicViews" or modulename == "django.contrib.auth.views" or modulename == "paystackpayments.views":
                pass
            else:
                return HttpResponseRedirect(reverse("login"))



