from js9 import j

from functools import wraps
from asyncio import get_event_loop
from sanic.response import text, json

from jose import jwt, exceptions

oauth2_server_pub_key = """"""

token_prefix = 'Bearer '

class oauth2_itsyouonline:
    def __init__(self, scopes=None, audience= None):

        self.described_by = "headers"
        self.field = "Authorization"

        self.allowed_scopes = scopes
        if audience is None:
            self.audience = ''
        else:
            self.audience = ",".join(audience)
        self.cfg = j.core.config.get('ays') or {}

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            self.check_token(args[1])

            return f(*args, **kwargs)

        return decorated_function

    async def check_token(self, request):
        if not self.cfg.get('production', False):
            return 200, ''
        # check provided token
        authorization = request.cookies.get(
        'jwt',
        request.headers.get(
            'Authorization',
            None
        ))

        if authorization is None:
            j.atyourservice.server.logger.error('No JWT token')
            return 401, 'No JWT token'

        msg = ""
        ss = authorization.split(' ', 1)
        if len(ss) != 2:
            msg = "Unauthorized"
        else:
            type, token = ss[0], ss[1]
            if type.lower() == 'bearer':
                try:
                    headers = jwt.get_unverified_header(token)
                    if 'oauth' not in self.cfg:
                        raise j.exceptions.Input('No ays oauth information in JumpScale config')
                    payload = jwt.decode(
                        token,
                        self.cfg['oauth'].get('jwt_key'),
                        algorithms=[headers['alg']],
                        audience=self.cfg['oauth']['organization'],
                        issuer='itsyouonline')
                    # case JWT is for an organization
                    if 'globalid' in payload and payload['globalid'] == self.cfg['oauth'].get('organization'):
                        return 200, ''

                    # case JWT is for a user
                    if 'scope' in payload and 'user:memberof:%s' % self.cfg[
                            'oauth'].get('organization') in payload['scope']:
                        return 200, ''
                        
                    # in case jwt created from organization
                    if 'azp' in payload and payload['azp'] == self.cfg['oauth'].get('organization'):
                        return 200, ''

                    msg = 'Unauthorized'
                except exceptions.ExpiredSignatureError as e:
                    msg = 'Your JWT has expired'

                except exceptions.JOSEError as e:
                    msg = 'JWT Error: %s' % str(e)

                except Exception as e:
                    msg = 'Unexpected error : %s' % str(e)

            else:
                msg = 'Your JWT is invalid'

        j.atyourservice.server.logger.error(msg)
        return 401, msg
