from .models import Category

def categoryprocessor(request):
    categories = Category.objects.all()
    return {'categories': categories}
    