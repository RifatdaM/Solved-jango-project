from django.shortcuts import render

def home(request):
    context = {
    }
    return render(request, 'home/home.html', context)

def about_us(request):
    context = {
    }
    return render(request, 'home/about_us.html', context)

def downloads(request):
    context = {
    }
    return render(request, 'home/downloads.html', context)

def contact_us(request):
    context = {
    }
    return render(request, 'home/contact_us.html', context)

def services(request):
    context = {
    }
    return render(request, 'home/3d_printer_ui.html', context)
