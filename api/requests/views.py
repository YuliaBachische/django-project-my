from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, "requests/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:

    return render(request,"requests/user-bio-form.html")


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST" and request.FILES.get("myfile"):
        myfile = request.FILES["myfile"]
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        file_size = fs.size(filename)

        if file_size > 1048576:
            fs.delete(filename)
            print("File deleted", filename)
            return render(request, "requests/file-too-big-error.html")
        else:
            print('saved file', filename)

    return render(request, "requests/file-upload.html")
