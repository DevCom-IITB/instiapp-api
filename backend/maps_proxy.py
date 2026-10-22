"""Narrow HTTP gateway to the standalone InstiMaps service."""

from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST", "OPTIONS"])
def maps_proxy(request, maps_path):
    """Forward the public Maps contract while keeping the services decoupled."""
    if maps_path.startswith("places") or maps_path.startswith("route"):
        upstream_path = f"api/{maps_path}"
    else:
        upstream_path = f"map/{maps_path}"

    # Django gives us the decoded path. Re-encode it before making the
    # upstream request so font stacks such as "Open Sans Regular" remain
    # valid URL path segments.
    encoded_path = quote(upstream_path, safe="/:@!$&'()*+,;=-._~")
    url = f"{settings.MAPS_SERVICE_URL}/{encoded_path}"
    if request.META.get("QUERY_STRING"):
        url = f"{url}?{request.META['QUERY_STRING']}"

    headers = {}
    for name in ("HTTP_ACCEPT", "CONTENT_TYPE"):
        value = request.META.get(name)
        if value:
            headers["Accept" if name == "HTTP_ACCEPT" else "Content-Type"] = value

    body = request.body if request.method == "POST" else None
    upstream_request = Request(url, data=body, headers=headers, method=request.method)

    try:
        with urlopen(upstream_request, timeout=15) as upstream:
            response = HttpResponse(
                upstream.read(),
                status=upstream.status,
                content_type=upstream.headers.get("Content-Type"),
            )
            for name in ("Cache-Control", "ETag", "Last-Modified", "Allow"):
                value = upstream.headers.get(name)
                if value:
                    response[name] = value
            return response
    except HTTPError as upstream:
        content_type = upstream.headers.get("Content-Type", "application/json")
        return HttpResponse(
            upstream.read(), status=upstream.code, content_type=content_type
        )
    except (TimeoutError, URLError, OSError):
        return JsonResponse(
            {"detail": "Maps service is unavailable."}, status=502
        )
