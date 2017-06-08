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

def hostToSURT(host, reverse_ipaddr=True):
    if not reverse_ipaddr and _RE_IP_ADDRESS.match(host):
        return host

    parts = host.split(b'.')
    parts.reverse()
    return b','.join(parts)

class SURT(object):
    def __init__(self, with_scheme=False, trailing_comma=False, reverse_ipaddr=True, **options):
        """Traditional SURT Format.
        """
        self.with_scheme = with_scheme
        self.trailing_comma = trailing_comma
        if reverse_ipaddr:
            self.host_to_surt = hostToSURT
        else:
            self.host_to_surt = partial(hostToSURT, reverse_ipaddr=False)

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
            e(self.host_to_surt(hurl.host))
            if hurl.port != hurl.DEFAULT_PORT:
                e(b':')
                e(format(hurl.port).encode('ascii'))
            if self.trailing_comma:
                e(b',')
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

class URL(object):
    def __init__(self, **options):
        """URL format - identical to :meth:`~surt.handyurl.geturl_bytes`
        """
        pass
    def format(self, hurl):
        return hurl.geturl_bytes()
