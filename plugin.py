###
# Copyright (c) 2009, Benjamin Rubin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import re
import steam


class Steamy(callbacks.Plugin):
    """Add the help for "@plugin help Steamy" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Steamy, self)
        self.__parent.__init__(irc)
        self.api = None
        self.group = None

    def update(self, apikey):
        self.api = steam.Service(apikey)
        self.group = steam.Group(self.api, self.registryValue('group'))
        self.group._update()

    def np(self, irc, msg, args):
        """Return a list of a people currently in-game on Steam
        """
        key = self.registryValue('apikey')
        if not key:
            irc.replyError('plugins.steamy.apikey has not been set')
            return

        self.update(key)
        ingame = filter(lambda player: player.isInGame(), self.group.members)
        playerCount = len(ingame)
        playerlist = map(lambda x:
            '{0}: {1}'.format(x.steamID.encode('utf8'), x.gameextrainfo.encode('utf8')), ingame)

        self.log.info(str(playerlist))

        if len(playerlist) != 0:
            reply = 'Now Playing: %s' % (', '.join(playerlist))
        else:
            reply = 'Now Playing: nobody :('

        if ircutils.isChannel(msg.args[0]):
            irc.queueMsg(ircmsgs.privmsg(msg.args[0], reply))
        else:
            irc.queueMsg(ircmsgs.privmsg(msg.nick, reply))
    np = wrap(np)


Class = Steamy


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
