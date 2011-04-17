'''
    Subsonic XBMC Plugin
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from resources.lib.Subsonic import Addon, Subsonic
import sys

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

subsonic = Subsonic.Subsonic(Addon.get_setting('server'), 
                             Addon.get_setting('user'), 
                             Addon.get_setting('password'))

Addon.logging.debug('plugin queries: ' + str(Addon.plugin_queries))
Addon.logging.debug('plugin handle: ' + str(Addon.plugin_handle))

if subsonic.ping():
    if Addon.plugin_queries['mode'] == 'list_indexes': 
        subsonic.get_indexes(Addon.plugin_queries['folder_id'])
    elif Addon.plugin_queries['mode'] == 'get_music_directory': 
        subsonic.get_music_directory(Addon.plugin_queries['id'])
    else:
        subsonic.get_music_folders()
else:
    Addon.show_settings()

