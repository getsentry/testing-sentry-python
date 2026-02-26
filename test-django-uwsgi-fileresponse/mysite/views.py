from django.http import FileResponse, HttpResponse
import os

def get_image(request):
    image_path = os.path.join(os.path.dirname(__file__), 'sample_image.png')
    return FileResponse(open(image_path, 'rb'), content_type='image/png')
