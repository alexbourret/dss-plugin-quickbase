import requests


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
        response = self.session.post(url, params=params, headers=headers, json=json)
        json_response = response.json()
        rows = json_response.get("data", [])
        self.last_number_of_rows_retrieved = len(rows)
        fields = json_response.get("fields", [])
        metadata = json_response.get("metadata", {})
        return rows, fields, metadata

    def has_more_data(self):
        if self.last_number_of_rows_retrieved == 0:
            return False
        return True
