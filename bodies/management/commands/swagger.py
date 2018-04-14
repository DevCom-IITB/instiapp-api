import json
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from rest_framework_swagger.views import get_swagger_view
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas

@api_view()
@renderer_classes([OpenAPIRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='InstiApp API')
    return response.Response(generator.get_schema(request=request))

class Command(BaseCommand):
    help = 'Generates JSON Swagger specification'

    def handle(self, *args, **options):
        """Generate swagger schema."""

        request = HttpRequest()
        request.method = 'GET'
        request.META['SERVER_NAME'] = 'localhost'
        request.META['SERVER_PORT'] = '80'
        request.path = '/docs/?format=openapi'

        returned = schema_view(request).render()
        output = json.dumps(json.loads(returned.content), indent=2)

        with open("docs/swagger.json", "w") as file:
            file.write(output)

        self.stdout.write(self.style.SUCCESS('Swagger generated'))
