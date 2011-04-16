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

import sys
import xbmcaddon, xbmcgui

__plugin_url = sys.argv[0]
__plugin_handle = int(sys.argv[1])
__plugin_query = sys.argv[2]
__settings = xbmcaddon.Addon(id='plugin.video.subsonic')

def show_error(details):
    error = ['', '', '']
    text = ''
    for k, v in enumerate(details):
        error[k] = v
        text += v + ' '
    print 'Subsonic: ' + text
    dialog = xbmcgui.Dialog()
    ok = dialog.ok(get_string(30000), error[0], error[1], error[2])
    
def get_setting(setting):
    return __settings.getSetting(setting)
    
def get_string(string_id):
    return __settings.getLocalizedString(string_id)   

