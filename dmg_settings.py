"""
DMG Settings for GitHub Actions macOS build
"""

application = defines.get('app', 'dist/DooMP-1.0-macos.app')
appname = defines.get('appname', 'DooMP')
format = defines.get('format', 'UDBZ')
size = defines.get('size', None)
files = [application]
symlinks = {'Applications': '/Applications'}
badge_icon = None
icon_locations = {
    appname: (140, 120),
    'Applications': (500, 120)
}
background = None
window_rect = ((100, 100), (640, 280))
default_view = 'icon-view'
show_icon_preview = False
include_icon_view_settings = True
include_list_view_settings = False