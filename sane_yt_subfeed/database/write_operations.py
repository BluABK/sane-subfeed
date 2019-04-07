import threading

from sane_yt_subfeed.controller.listeners.database.database_listener import DatabaseListener
from sane_yt_subfeed.database.category import Category
from sane_yt_subfeed.database.db_download_tile import DBDownloadTile
from sane_yt_subfeed.database.engine_statements import update_video_statement_full, get_video_by_vidd_stmt, insert_item, \
    get_video_ids_by_video_ids_stmt, update_extra_information_stmt, update_video_stmt, update_channel_from_remote
from sane_yt_subfeed.database.models import Channel
from sane_yt_subfeed.database.orm import engine, db_session
from sane_yt_subfeed.database.video import Video
from sane_yt_subfeed.handlers.log_handler import create_logger

lock = threading.Lock()


def engine_execute_first(stmt):
    return engine.execute(stmt).first()


def engine_execute(stmt):
    engine.execute(stmt)


class UpdateVideosThread(threading.Thread):
    logger = create_logger(__name__ + ".UpdateVideosThread")

    def __init__(self, video_list, update_existing=False, uniques_check=True, finished_listeners=None,
                 only_thumbnails=False):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.video_list = video_list
        self.update_existing = update_existing
        self.uniques_check = uniques_check
        self.finished_listeners = finished_listeners
        self.db_id = 0
        self.only_thumbnails = only_thumbnails

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        self.db_id = threading.get_ident()
        if self.uniques_check:
            self.video_list = check_for_unique(self.video_list)

        items_to_add = []
        items_to_update = []
        # bulk_items_to_add = []
        lock.acquire()
        self.logger.debug6("Thread {} - Acquired lock".format(self.db_id, len(items_to_update)))
        DatabaseListener.static_instance.startRead.emit(self.db_id)
        select_step = 500
        for i in range(0, len(self.video_list), select_step):
            videos_bulk = self.video_list[i:i + select_step]
            video_ids_bulk = set(video.video_id for video in videos_bulk)
            stmt = get_video_ids_by_video_ids_stmt(video_ids_bulk)
            db_videos = Video.to_video_ds(engine.execute(stmt))
            db_videos_ids = set(video.video_id for video in db_videos)
            items_to_add.extend(insert_item(video) for video in videos_bulk if video.video_id not in db_videos_ids)
            if self.update_existing:
                items_to_update.extend(video for video in videos_bulk if video.video_id in db_videos_ids)

        DatabaseListener.static_instance.finishRead.emit(self.db_id)
        DatabaseListener.static_instance.startWrite.emit(self.db_id)
        step = 1000
        if len(items_to_add) > 0:
            self.logger.debug6("Thread {} - inserting {} new videos".format(self.db_id, len(items_to_add)))
            for i in range(0, len(items_to_add), step):
                engine.execute(Video.__table__.insert(), items_to_add[i:i + step])
        if len(items_to_update) > 0:
            self.logger.debug6("Thread {} - updating {} items".format(self.db_id, len(items_to_update)))
            update_list = []
            # FIXME: add step to update
            for item in items_to_update:
                item_dict = item.__dict__
                item_dict["_video_id"] = item.video_id
                update_list.append(item_dict)
            engine.execute(update_video_stmt(), update_list)
        DatabaseListener.static_instance.finishWrite.emit(self.db_id)
        lock.release()
        if self.finished_listeners:
            for listener in self.finished_listeners:
                listener.emit()


class UpdateVideosExtraInfoThreaded(threading.Thread):

    def __init__(self, video_list, finished_listeners=None):
        """
        Init GetUploadsThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        self.logger = create_logger(__name__ + ".UpdateVideosThread")
        threading.Thread.__init__(self)
        self.video_list = video_list
        self.finished_listeners = finished_listeners
        self.db_id = 0

    # TODO: Handle failed requests
    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        self.db_id = threading.get_ident()

        lock.acquire()
        DatabaseListener.static_instance.startWrite.emit(self.db_id)
        update_list = []
        if len(self.video_list):
            for item in self.video_list:
                vid_info = "{}".format(item)
                if item.thumbnail_path is None:
                    self.logger.warning("Video missing thumbnail for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.duration is None:
                    self.logger.warning("Video missing duration for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.has_caption is None:
                    self.logger.warning("Video missing has_caption for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.dimension is None:
                    self.logger.warning("Video missing dimension for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.definition is None:
                    self.logger.warning("Video missing definition for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.projection is None:
                    self.logger.warning("Video missing projection for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.region_restriction_allowed is None:
                    self.logger.warning("Video missing region_restriction_allowed for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.region_restriction_blocked is None:
                    self.logger.warning("Video missing region_restriction_blocked for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                elif item.kind is None:
                    self.logger.warning("Video missing kind for update: {}".format(vid_info))
                    self.logger.error(self.obj_attrs_to_dict(item))
                else:
                    update_list.append(
                        {"thumbnail_path": item.thumbnail_path, "_video_id": item.video_id, "duration": item.duration,
                         "has_caption": item.has_caption, "dimension": item.dimension, "definition": item.definition,
                         "projection": item.projection, "region_restriction_allowed": item.region_restriction_allowed,
                         "region_restriction_blocked": item.region_restriction_blocked,
                         "kind": item.kind})
            try:
                engine.execute(update_extra_information_stmt(), update_list)
            except Exception as e:
                self.logger.critical("Failed to update extra information: {} - {}".format(e, update_list), exc_info=1)
        else:
            self.logger.info("Skipping update as self.video_list is empty")
        DatabaseListener.static_instance.finishWrite.emit(self.db_id)
        lock.release()
        if self.finished_listeners:
            for listener in self.finished_listeners:
                listener.emit()

    def obj_attrs_to_dict(self, obj):
        """
        Finds all non-builtin attributes of an object and puts attrib: value in a dict
        :param obj:
        :return:
        """
        attrs = {}
        for attr in dir(obj):
            if not attr.startswith('__'):
                attrs.update({attr: getattr(obj, attr)})
        return attrs


class UpdateVideo(threading.Thread):
    logger = create_logger(__name__ + ".UpdateVideo")

    def __init__(self, video_d, update_existing=False, finished_listeners=None):
        """
        Init GetUploadsThread
        :param video_d:
        """
        threading.Thread.__init__(self)
        self.finished_listeners = finished_listeners
        self.video_d = video_d
        self.update_existing = update_existing
        self.db_id = 0

    # TODO: Handle failed requests
    def run(self):
        self.db_id = threading.get_ident()
        DatabaseListener.static_instance.startWrite.emit(self.db_id)
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        # self.logger.debug("Run")
        # start = default_timer()
        lock.acquire()
        stmt = get_video_by_vidd_stmt(Video.video_d_to_video(self.video_d))
        db_video = engine.execute(stmt).first()
        if db_video:
            if self.update_existing:
                engine.execute(update_video_statement_full(self.video_d))
            else:
                pass
        else:
            engine.execute(Video.__table__.insert(), insert_item(self.video_d))
        # print('Updated: {}'.format(self.video_d.title))
        lock.release()

        if self.finished_listeners:
            for listener in self.finished_listeners:
                listener.emit()
        DatabaseListener.static_instance.finishWrite.emit(self.db_id)


def check_for_unique(vid_list):
    compare_set = set()
    for vid in vid_list:
        if vid.video_id in compare_set:
            vid_list.remove(vid)
        else:
            compare_set.add(vid.video_id)
    return vid_list


def update_event_download_tile(download_tile):
    lock.acquire()
    stmt = DBDownloadTile.__table__.update().where(DBDownloadTile.video_id == download_tile.video.video_id).values({
        'last_event': download_tile.last_event})
    engine.execute(stmt)
    lock.release()


def update_category(category):
    lock.acquire()
    stmt = Category.__table__.update().where(Category.id == category.id).values({
        'name': category.name,
        'color': category.color,
        'enabled': category.enabled,
        'icon': category.icon,
        'primary_videos': category.primary_videos,
        'videos': category.videos,
        'channels': category.channels})
    engine.execute(stmt)
    lock.release()


def delete_sub_not_in_list(subs):
    delete_channels = db_session.query(Channel).filter(~Channel.id.in_(subs)).all()
    for channel in delete_channels:
        if channel.subscribed or channel.subscribed is None:
            channel.subscribed = False
            create_logger(__name__).warning(
                "Setting unsubscribed for channel: {} - {}".format(channel.title, channel.__dict__))
            stmt = update_channel_from_remote(channel)
            engine.execute(stmt)
    # stmt = Channel.__table__.delete().where(~Channel.id.in_(subs))
