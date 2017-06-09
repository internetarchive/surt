# Copyright(c)2012-2013 Internet Archive. Software license AGPL version 3.
#
# This file is part of the `surt` python package.
#
#     surt is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     surt is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with surt.  If not, see <http://www.gnu.org/licenses/>.
#
#     The surt source is hosted at https://github.com/internetarchive/surt
import re
from functools import partial

# hostToSURT
#_______________________________________________________________________________
_RE_IP_ADDRESS = re.compile(br"(?:(?:\d{1,3}\.){3}\d{1,3})$")

# unused - kept for backward compatibility just in case someone's using this.
def hostToSURT(host, reverse_ipaddr=True):
    return _host_to_surt(host, reverse_ipaddr=reverse_ipaddr)[0]

def _host_to_surt(host, trailing_comma=False, reverse_ipaddr=True):
    """Return SURT-fied host and trailing character to be appended to
    the authority part.
    """
    if _RE_IP_ADDRESS.match(host):
        if not reverse_ipaddr:
            return host, b''
        trailer = b''
    else:
        trailer = b',' if trailing_comma else b''
    parts = host.split(b'.')
    parts.reverse()
    return b','.join(parts), trailer

class SURT(object):
    def __init__(self, with_scheme=False, trailing_comma=False, reverse_ipaddr=True, **options):
        """Traditional SURT Format.
        """
        self.with_scheme = with_scheme
        self.host_to_surt = partial(_host_to_surt, trailing_comma=trailing_comma, reverse_ipaddr=reverse_ipaddr)

    def format(self, hurl):
        """Generate SURT from `hurl`.
        Note: no longer implements ``public_suffix`` option. Must be done in canonicalization phase.

        :param hurl: parsed and canonicalized URL.
        :type hurl: :class:`handyurl`
        """
        surt = bytearray()
        e = surt.extend

        if self.with_scheme:
            e(hurl.scheme)
            e(b':')
            if hurl.host:
                if hurl.scheme != b'dns':
                    e(b'//')
                e(b'(')
        elif not hurl.host:
            e(hurl.scheme)
            e(b':')
        if hurl.host:
            if hurl.authUser:
                e(hurl.authUser)
                if hurl.authPass:
                    e(hurl.authPass)
                e(b'@')
            shost, trailer = self.host_to_surt(hurl.host)
            e(shost)
            if hurl.port != hurl.DEFAULT_PORT:
                e(b':')
                e(format(hurl.port).encode('ascii'))
            if trailer:
                e(trailer)
            e(b')')
        # TODO: path should be normalized
        if hurl.path:
            e(hurl.path)
        elif hurl.query is not None or hurl.hash is not None:
            # must have '/' with query or hash
            e(b'/')
        if hurl.query is not None:
            e(b'?')
            e(hurl.query)
        if hurl.hash is not None:
            e(b'#')
            e(hurl.hash)
        if hurl.last_delimiter is not None:
            e(hurl.last_delimiter)

        return bytes(surt)

class URI(object):
    def __init__(self, **options):
        """Plain URI format - identical to :meth:`~surt.handyurl.geturl_bytes`
        """
        pass
    def format(self, hurl):
        return hurl.geturl_bytes()
