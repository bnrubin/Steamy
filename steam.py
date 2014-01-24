#!/usr/bin/env python
import sys
import urllib2
#import pprint
from lxml import etree


def getValue(tree, tag):
    """Return tag text or None"""
    try:
        return tree.find(tag).text
    except AttributeError:
        return None


def convertNameToID(steamID):
    """Convert a player name (steamID) to its 64bit representation"""
    url = 'http://steamcommunity.com/id/%s/?xml=1' % steamID
    tree = etree.parse(urllib2.urlopen(url))
    return tree.find('steamID64').text


class Service:
    def __init__(self, apikey):
        self.apikey = apikey


class Group:
    def __init__(self, service, id=None, id64=None):
        self.id = id
        self.id64 = id
        self.members = []
        self.api = service
        self._update()

    def _update(self):
        url = 'http://steamcommunity.com/groups/%s/memberslistxml/?xml=1' % self.id
        memberList = []
        for event, member in list(etree.iterparse(urllib2.urlopen(url), tag='steamID64')):
            memberList.append(member.text)

        self.bulkPlayerUpdate(memberList)

    def bulkPlayerUpdate(self, idList):
        url = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0001/?key=%s&steamids=%s&format=xml' % (self.api.apikey, ','.join(idList)))
        tree = etree.parse(url)
        self.members = []
        for playerTree in tree.find('players').findall('player'):
            self.members.append(Player(self.api, tree=playerTree))


class Player:
    PERSONA_STATES = {'0': 'Offline', '1': 'Online', '2': 'Busy', '3': 'Away', '4': 'Snooze'}
    VISIBILITY_STATES = {'1': 'Private', '2': 'Friends Only', '3': 'Public'}

    def __init__(self, service, steamID=None, steamID64=None, tree=None):
        self.api = service
        self.steamID = steamID
        self.steamID64 = steamID64
        self.communityvisibilitystate = None
        self.lastlogoff = None
        self.profileurl = None
        self.avatar = None
        self.personastate = None
        self.primaryclanid = None
        self.timecreated = None
        self.gameextrainfo = None
        self.gameid = None
        if tree is not None:
            self._update(tree)
        else:
            if steamID64 is None:
                self.steamID64 = convertNameToID(self.steamID)
            url = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0001/?key=%s&steamids=%s&format=xml' % (self.api.apikey, self.steamID64))
            self._update(etree.parse(url).find('players').find('player'))

    def _update(self, tree):
        self.steamID64 = getValue(tree, 'steamid')
        self.steamID = getValue(tree, 'personaname')
        self.communityvisibilitystate = getValue(tree, 'communityvisibilitystate')
        self.lastlogoff = getValue(tree, 'lastlogoff')
        self.profileurl = getValue(tree, 'profileurl')
        self.avatar = getValue(tree, 'avatar')
        self.personastate = getValue(tree, 'personastate')
        self.primaryclanid = getValue(tree, 'primaryclanid')
        self.timecreated = getValue(tree, 'timecreated')
        self.gameextrainfo = getValue(tree, 'gameextrainfo')
        self.gameid = getValue(tree, 'gameid')

    def dump(self):
        print 'steamID64: %s' % self.steamID64
        print 'steamID: %s' % self.steamID
        print 'communityvisibilitystate: %s (%s)' % (self.VISIBILITY_STATES[self.communityvisibilitystate], self.communityvisibilitystate)
        print 'lastlogoff: %s' % self.lastlogoff
        print 'profileurl: %s' % self.profileurl
        print 'avatar: %s' % self.avatar
        print 'personastate: %s (%s)' % (self.PERSONA_STATES[self.personastate], self.personastate)
        print 'primaryclanid: %s' % self.primaryclanid
        print 'timecreated: %s' % self.timecreated
        print 'gameextrainfo: %s' % self.gameextrainfo
        print 'gameid: %s' % self.gameid

    def isOnline(self):
        return self.personastate != '0'

    def isInGame(self):
        return self.gameextrainfo is not None


def main(argv=None):
    pass

if __name__ == '__main__':
    sys.exit(main())
