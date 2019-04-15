from sane_yt_subfeed.gui.views.grid_view.labels.video_tile_label import VideoTileLabel

CFG_LINES_ENTRY = ['GridView', 'tile_date_lines']
CFG_ELIDED_MOD_ENTRY = ['GridView', 'elided_text_modifier_date']


class DateLabel(VideoTileLabel):

    def __init__(self, text, parent):
        VideoTileLabel.__init__(self, text, parent, CFG_LINES_ENTRY, CFG_ELIDED_MOD_ENTRY)

