from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from sane_yt_subfeed.database.orm import PermanentBase, db_session


class DBCategory(PermanentBase):
    """
    Category for a video.

    SQLAlchemy Database mapped table object.

    Columns:
            Self:
                id:                 Integer identifier for a category.
                name:               Name of the category.
                icon:               Optional icon (filepath) in addition to or instead of name.
                color:              Color of GUI label (hexadecimal).
                enabled:            Whether or not category is enabled.
            Relational:
                primary_videos:     List of video IDs with this as their primary category.
                                    (In terms of sorting etc only one category can truly be the master one)
                videos:             List of Video objects labeled with this category.
                channels:           List of Channel objects that sets this category by default.
            Foreign:
                video_ids:          List of all video IDs
                channel_ids:        List of all channel IDs.

            TODO: Add primary category column to Video table!!
    """
    # Table name in actual DB file.
    __tablename__ = 'category'

    # Table primary key column.
    id = Column('id', Integer, primary_key=True)

    # Table columns.
    # Self
    name = Column(String)
    color = Column(String)
    enabled = Column(Boolean)
    icon = Column(String)
    # Relational
    primary_videos = Column(String, ForeignKey('video.video_id'), unique=True)
    videos = Column(String, ForeignKey('video.video_id'), unique=True)
    channels = Column(String, ForeignKey('channel.id'), unique=True)
    # Foreign
    # video_ids = Column(String, ForeignKey('video.video_id'), unique=True)
    # channel_ids = Column(String, ForeignKey('channel.id'), unique=True)

    def __init__(self, category):
        self.update(category)

    def __repr__(self):
        return "<DBCategory(id={}, name={}, color={}, enabled={}, icon={}, primary_videos={}, videos={})>".format(
            self.id, self.name, self.color, self.enabled, self.icon, self.primary_videos, self.videos)

    def __str__(self):
        return self.__repr__()

    def update(self, category):
        """
        Update table values from a given category object.
        :return:
        """
        # self.id = category.id
        self.name = category.name
        self.color = category.color
        self.enabled = category.enabled
        self.icon = category.icon
        self.primary_videos = category.primary_videos
        self.videos = category.videos
        self.channels = category.channels
        # self.video_ids = category.video_ids
        # self.channel_ids = category.channel_ids
