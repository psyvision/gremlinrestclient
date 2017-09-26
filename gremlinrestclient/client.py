import collections
import json

import requests

from gremlinrestclient.exceptions import RequestError, GremlinServerError


__all__ = ("GremlinRestClient", "Response")

Response = collections.namedtuple(
    "Response",
    ["status_code", "data", "message", "metadata"])


class GremlinRestClient(object):

    HEADERS = {'content-type': 'application/json'}

    def __init__(self, url="http://localhost:8182", ssl_verify=None):
        self._url = url
        self._ssl_verify = ssl_verify

    def execute(self, gremlin, bindings=None, lang="gremlin-groovy", query_timeout=None):
        """
        Send a script to the Gremlin Server

        :param str gremlin: The script to send.
        :param dict bindings: Bindings for the Gremlin Script.
        :param str lang: Gremlin language variant.

        :returns: :py:class:`Response<gremlinrestclient.client.Response>`
        """
        if bindings is None:
            bindings = {}
        payload = {
            "gremlin": gremlin,
            "bindings": bindings,
            "language": lang
        }
        resp = self._post(self._url, json.dumps(payload), query_timeout, self._ssl_verify)
        resp = resp.json()
        resp = Response(resp["status"]["code"],
                        resp["result"]["data"],
                        resp["status"]["message"],
                        resp["result"]["meta"])
        return resp

    def _post(self, url, data, post_timeout=None, ssl_verify=None):
        resp = requests.post(url, data=data, headers=self.HEADERS, timeout=post_timeout, verify=ssl_verify)
        status_code = resp.status_code
        if status_code != 200:
            if status_code == 403:
                raise RuntimeError(
                    "403 Forbidden: Server must be configured for REST")
            msg = resp.json()["message"]
            if resp.status_code < 500:
                raise RequestError(resp.status_code, msg)
            else:
                raise GremlinServerError(resp.status_code, msg)
        return resp
