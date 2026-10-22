from unittest.mock import patch

from django.test import SimpleTestCase, override_settings


class _UpstreamResponse:
    status = 200
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=60",
    }

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return b'{"ok":true}'


class MapsProxyTests(SimpleTestCase):
    @override_settings(MAPS_SERVICE_URL="http://maps.local:8002")
    @patch("backend.maps_proxy.urlopen", return_value=_UpstreamResponse())
    def test_places_request_is_forwarded_to_maps_service(self, urlopen):
        response = self.client.get("/api/places/?search=cafe")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://maps.local:8002/api/places/?search=cafe",
        )

    @override_settings(MAPS_SERVICE_URL="http://maps.local:8002")
    @patch("backend.maps_proxy.urlopen", return_value=_UpstreamResponse())
    def test_route_post_preserves_json_body_and_path(self, urlopen):
        payload = b'{"source":{"lat":19.1,"lng":72.9},"stops":[]}'
        response = self.client.post(
            "/api/route/", data=payload, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://maps.local:8002/api/route/")
        self.assertEqual(request.data, payload)
        self.assertEqual(request.get_method(), "POST")

    @override_settings(MAPS_SERVICE_URL="http://maps.local:8002")
    @patch("backend.maps_proxy.urlopen", return_value=_UpstreamResponse())
    def test_live_route_request_is_forwarded(self, urlopen):
        response = self.client.post(
            "/api/route/live/", data=b"{}", content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url, "http://maps.local:8002/api/route/live/"
        )

    @override_settings(MAPS_SERVICE_URL="http://maps.local:8002")
    @patch("backend.maps_proxy.urlopen", return_value=_UpstreamResponse())
    def test_tile_request_is_forwarded_to_map_service(self, urlopen):
        response = self.client.get("/map/1/0/0.pbf")

        self.assertEqual(response.status_code, 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://maps.local:8002/map/1/0/0.pbf")

    @override_settings(MAPS_SERVICE_URL="http://maps.local:8002")
    @patch("backend.maps_proxy.urlopen", return_value=_UpstreamResponse())
    def test_glyph_request_is_forwarded_to_map_service(self, urlopen):
        response = self.client.get("/map/fonts/Open%20Sans%20Regular/0-255.pbf")

        self.assertEqual(response.status_code, 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://maps.local:8002/map/fonts/Open%20Sans%20Regular/0-255.pbf",
        )

    @override_settings(MAPS_SERVICE_URL="http://maps.local:8002")
    @patch("backend.maps_proxy.urlopen", side_effect=OSError("connection refused"))
    def test_unavailable_maps_service_returns_gateway_error(self, _urlopen):
        response = self.client.get("/api/places/")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": "Maps service is unavailable."})
