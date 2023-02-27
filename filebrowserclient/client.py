from requests import Session, Response, HTTPError, get

from filebrowserclient.errors import Forbidden, NotFound, AuthenticationError
from filebrowserclient.models import User, Share, CreateShare, Resources
from filebrowserclient.utils.token import Token
from filebrowserclient.utils.typing import response_model, response_list_model


class FileBrowserClient(Session):
    def __init__(self, base_url: str, token=None):
        super().__init__()
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self._token = None
        self.base_url = base_url
        self.token = token

    def check_token(self):
        if self._token and self._token.expired:
            self.token = self.renew_token()

    @property
    def token(self):
        if self._token:
            return self._token.raw

    @token.setter
    def token(self, val):
        if val:
            self._token = Token(val)
        else:
            self._token = None

    def request(self, method, url, headers=None, **kwargs) -> Response:
        self.check_token()
        headers = headers or {}
        return super().request(method, self.base_url + url, headers={**headers, "x-auth": self.token}, **kwargs)

    def with_auth(self, username, password, recaptcha=""):
        try:
            return self.__class__(
                base_url=self.base_url,
                token=self.get_token(username, password, recaptcha)
            )
        except Forbidden as e:
            raise AuthenticationError from e

    def check_response(self, resp):
        try:
            resp.raise_for_status()
        except HTTPError as e:
            if resp.status_code == 403:
                raise Forbidden from e
            if resp.status_code == 404:
                raise NotFound from e
            raise

    def get_json_response(self, resp):
        self.check_response(resp)
        return resp.json()

    def get_text_response(self, resp):
        self.check_response(resp)
        return resp.text

    def get_token(self, username, password, recaptcha=""):
        return self.get_text_response(
            self.post(
                "api/login",
                json=dict(
                    username=username,
                    password=password,
                    recaptcha=recaptcha
                )
            )
        )

    def renew_token(self):
        return self.get_text_response(self.post("api/renew"))

    def get_usage(self, path=""):
        return self.get_json_response(self.get("api/usage/" + path))

    def get_resources(self, path=""):
        return self.get_json_response(self.get("api/resources/" + path))

    def get_download_link(self, path="", algo=None):
        return f"{self.base_url}api/raw/{path}?auth={self.token}&algo=" + (algo or "")

    def download(self, path="", algo=None):
        with get(self.get_download_link(path, algo), stream=True) as s:
            return s.iter_content(1024)

    @response_list_model(User)
    def list_users(self):
        return self.get_json_response(self.get("api/users"))

    @response_model(User)
    def get_user(self, user_id):
        return self.get_json_response(self.get("api/users/" + str(user_id)))

    @response_list_model(Share)
    def list_path_shares(self, path):
        return self.get_json_response(self.get("api/share" + path))

    @response_list_model(Share)
    def list_all_shares(self):
        return self.get_json_response(self.get("api/shares"))

    @response_model(Share)
    def create_share(self, path, expires, unit, password=""):
        return self.get_json_response(
            self.post(
                "api/share" + path,
                json=CreateShare(
                    expires=expires,
                    unit=unit,
                    password=password
                ).dict(),
                params=dict(
                    expires=expires,
                    unit=unit
                )
            )
        )

    def delete_share(self, _hash):
        self.check_response(self.delete("api/share/" + _hash))

    @response_model(Resources)
    def list_resources(self, path="/"):
        return self.get_json_response(self.get("api/resources" + path))

    def create_resource(self, path, data, content_type, override=False):
        self.check_response(
            self.post(
                "api/resources" + path,
                data=data,
                headers={"Content-Type": content_type},
                params=dict(override=override)
            )
        )

    def delete_resource(self, path):
        self.check_response(self.delete("api/resources" + path))

    def update_resource(self, path, data, content_type):
        self.check_response(self.put("api/resources" + path, data=data, headers={"Content-Type": content_type}))
