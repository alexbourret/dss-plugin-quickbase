import requests
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='quickbase plugin %(levelname)s - %(message)s')


class QuickBaseAuth(requests.auth.AuthBase):
    def __init__(self, config):
        self.auth_type = config.get("auth_type", "tokens")
        self.token_type = None
        self.token = None
        self.realm_hostname = None
        if self.auth_type == "tokens":
            token = config.get("token", {})
            self.token_type = token.get("token_type", "user")
            self.token = token.get("token")
            self.realm_hostname = token.get("realm_hostname")
            if not self.token:
                raise Exception("The token is empty")
        if not self.realm_hostname:
            raise Exception("The real hostname is empty")

    def __call__(self, request):
        if self.token_type == "user":
            request.headers["Authorization"] = "QB-USER-TOKEN {}".format(self.token)
        request.headers["QB-Realm-Hostname"] = self.realm_hostname
        return request


class QuickBaseSession():
    def __init__(self, config):
        self.session = requests.Session()
        self.session.auth = QuickBaseAuth(config)
        self.last_number_of_rows_retrieved = -1

    def get(self, url, params=None):
        headers = {
            "Content-Type": "application/json"
        }
        response = self.session.get(url, params=params, headers=headers)
        return response

    def post(self, url, params=None, json=None):
        headers = {
            "Content-Type": "application/json"
        }
        response = self.request("POST", url, params=params, headers=headers, json=json)
        json_response = response.json()
        rows = json_response.get("data", [])
        self.last_number_of_rows_retrieved = len(rows)
        fields = json_response.get("fields", [])
        metadata = json_response.get("metadata", {})
        return rows, fields, metadata

    def request(self, method, url, params=None, headers=None, json=None):
        response = self.session.request(method, url, params=params, headers=headers, json=json)
        assert_response_ok(response)
        return response

    def has_more_data(self):
        if self.last_number_of_rows_retrieved == 0:
            return False
        return True


def assert_response_ok(response):
    if type(response) != requests.models.Response:
        raise Exception("requests response not correct")
    status_code = response.status_code
    if status_code < 400:
        return
    logger.error("Error {} while trying {} on {}".format(status_code, response.request.method, response.url))
    logger.error("Dumping content={}".format(response.content))
    raise Exception("Error {}".format(status_code))
