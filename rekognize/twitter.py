import requests


API_VERSION = '1'
BASE_API_URL = 'https://%s.rekognize.io/twitter/'


class TwitterClientError(Exception):
    def __init__(self, msg, resource_url=None, request_method=None, status_code=None, error_code=None, headers=None):
        self._msg = msg
        self.request_method = request_method
        self.resource_url = resource_url
        self.status_code = status_code
        self.error_code = error_code
        self.headers = headers

    def __str__(self):
        if self.request_method and self.resource_url:
            return '%s (%s %s)' % (self._msg, self.request_method, self.resource_url)
        return self._msg


class TwitterApiError(TwitterClientError):
    def __init__(self, msg, response=None, request_method=None, error_code=None):
        kwargs = {
            'request_method': request_method,
            'error_code': error_code,
        }
        if response is not None:
            kwargs.update(
                {
                    'status_code': response.status_code,
                    'resource_url': response.url,
                    'headers': response.headers,
                }
            )

        super(TwitterApiError, self).__init__(
            msg,
            **kwargs
        )


class TwitterRateLimitError(TwitterApiError):
    pass


class TwitterAuthError(TwitterApiError):
    pass


class ApiComponent(object):
    def __init__(self, client, path=None):
        self._client = client
        self._path = path

    def __repr__(self):
        return '<ApiComponent: %s>' % self._path

    def __getitem__(self, path):
        if not self._path is None:
            path = '%s/%s' % (self._path, path)
        return ApiComponent(self._client, path)

    def __getattr__(self, path):
        return self[path]

    def get(self, **params):
        if self._path is None:
            raise TypeError('Calling get() on an empty API path is not supported.')
        return self._client.request('GET', self._path, **params)

    def post(self, **params):
        if self._path is None:
            raise TypeError('Calling post() on an empty API path is not supported.')
        return self._client.request('POST', self._path, **params)

    def get_path(self):
        return self._path


class BaseResponse(object):
    def __repr__(self):
        return '<%s: %s %s>' % (self.__class__.__name__, self.request_method, self.resource_url)


class ApiResponse(BaseResponse):
    def __init__(self, response, request_method, json_data, remaining=None):
        self.resource_url = response.url
        self.headers = response.headers
        self.request_method = request_method
        self.data = json_data
        self.remaining = remaining


class JSONObject(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError('%s has no property named %s.' % (self.__class__.__name__, name))

    def __setattr__(self, *args):
        raise AttributeError('%s instances are read-only.' % self.__class__.__name__)
    __delattr__ = __setitem__ = __delitem__ = __setattr__

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, dict.__repr__(self))


class BaseTwitterClient(object):
    api_version = API_VERSION
    base_api_url = BASE_API_URL
    user_agent_string = 'Rekognize Twitter Client'

    def __getattr__(self, path):
        return ApiComponent(self, path)

    def configure_oauth_session(self, session):
        session.headers = {'User-Agent': self.get_user_agent_string()}
        return session

    def get_user_agent_string(self):
        return self.user_agent_string

    def request(self, method, path, **params):
        method = method.upper()
        url = self.construct_resource_url(path)
        request_kwargs = {}
        params, files = self.sanitize_params(params)

        if method == 'GET':
            request_kwargs['params'] = params
        elif method == 'POST':
            request_kwargs['json'] = params

        try:
            response = self.make_api_call(method, url, **request_kwargs)
        except requests.RequestException as e:
            raise TwitterClientError(
                str(e),
                resource_url=url,
                request_method=method
            )

        return self.handle_response(method, response)

    def construct_resource_url(self, path):
        paths = path.split('/')
        return '%s%s' % (self.base_api_url % paths[0], '/'.join(paths[1:]))

    def make_api_call(self, method, url, **request_kwargs):
        req = getattr(self.session, method.lower())
        return req(url, **request_kwargs)

    def handle_response(self, method, response):
        try:
            data = response.json(object_hook=self.get_json_object_hook)
        except ValueError:
            data = None

        if response.status_code == 200:
            return ApiResponse(response, method, data['data'], remaining=data['remaining'])

        if data is None:
            raise TwitterApiError(
                'Unable to decode JSON response.',
                response=response,
                request_method=method,
            )

        error_code, error_msg = self.get_twitter_error_details(data)
        kwargs = {
            'response': response,
            'request_method': method,
            'error_code': error_code,
        }

        if response.status_code == 401 or 'Bad Authentication data' in error_msg:
            raise TwitterAuthError(error_msg, **kwargs)

        if response.status_code == 404:
            raise TwitterApiError('Invalid API resource.', **kwargs)

        if response.status_code == 429:
            raise TwitterRateLimitError(error_msg, **kwargs)

        raise TwitterApiError(error_msg, **kwargs)

    @staticmethod
    def sanitize_params(input_params):
        params, files = ({}, {})

        for k, v in input_params.items():
            if hasattr(v, 'read') and callable(v.read):
                files[k] = v
            elif isinstance(v, bool):
                if v:
                    params[k] = 'true'
                else:
                    params[k] = 'false'
            elif isinstance(v, list):
                params[k] = ','.join(v)
            else:
                params[k] = v
        return params, files

    @staticmethod
    def get_json_object_hook(data):
        return JSONObject(data)

    @staticmethod
    def get_twitter_error_details(data):
        code, msg = (None, 'An unknown error has occured processing your request.')
        errors = data.get('errors') if data else None

        if errors and isinstance(errors, list):
            code = errors[0]['code']
            msg = errors[0]['message']
        elif errors:
            code = errors['code']
            msg = errors['message']

        return (code, msg)


class UserClient(BaseTwitterClient):
    def __init__(self, access_token, access_token_secret):
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.session = requests.Session()
        self.session.headers.update({
            'X-Access-Token': self.access_token,
            'X-Access-Token-Secret': self.access_token_secret,
        })

    def get_signin_token(self, callback_url=None, auto_set_token=True, **kwargs):
        return self.get_request_token(self.base_signin_url, callback_url, auto_set_token, **kwargs)

    def get_authorize_token(self, callback_url=None, auto_set_token=True, **kwargs):
        return self.get_request_token(self.base_authorize_url, callback_url, auto_set_token, **kwargs)

    def auto_set_token(self, token):
        self.access_token = token['oauth_token']
        self.access_token_secret = token['oauth_token_secret']
        self.session = self.get_oauth_session()
