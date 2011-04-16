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

subsonic = Subsonic.Subsonic(Addon.get_setting('server'), 
                    Addon.get_setting('user'), 
                    Addon.get_setting('password'))
if subsonic.ping():
    Addon.add_music_item('12345', {'title': 'a title', 'artist': 'an artist'})
    Addon.add_directory({'mode': 'something'}, 'a folder')
    Addon.end_of_directory()

else:
    Addon.show_settings()

