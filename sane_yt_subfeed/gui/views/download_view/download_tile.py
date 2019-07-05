from collections import Counter

import copy

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGridLayout, QWidget, QMenu
from datetime import datetime

from sane_yt_subfeed.handlers.config_handler import read_config
from sane_yt_subfeed.controller.listeners.gui.views.download_view.download_view_listener import DownloadViewListener
from sane_yt_subfeed.database.detached_models.d_db_download_tile import DDBDownloadTile
from sane_yt_subfeed.gui.views.download_view.download_thumbnail import DownloadThumbnailWidget
from sane_yt_subfeed.gui.views.download_view.progress_bar import DownloadProgressBar
from sane_yt_subfeed.gui.views.download_view.small_label import SmallLabel
from sane_yt_subfeed.handlers.log_handler import create_logger


class DownloadTile(QWidget):
    def __init__(self, parent, download_progress_listener, db_download_tile=None, *args, **kwargs):
        super(DownloadTile, self).__init__(parent, *args, **kwargs)
        self.logger = create_logger(__name__)
        self.root = parent.root
        self.parent = parent

        if download_progress_listener:
            self.download_progress_listener = download_progress_listener
            self.video = download_progress_listener.video
            self.download_progress_listener.updateProgress.connect(self.update_progress)
            self.download_progress_listener.finishedDownload.connect(self.finished_download)
            self.download_progress_listener.failedDownload.connect(self.failed_download)
        elif db_download_tile:
            self.download_progress_listener = None
            self.video = db_download_tile.video

        self.total_bytes = None
        self.total_bytes_video = None
        self.total_bytes_audio = None
        self.video_downloaded = False
        self.finished = False
        self.paused = False
        self.failed = False
        self.finished_date = None
        self.started_date = None
        self.last_event = None
        self.cleared = False

        self.setFixedHeight(read_config('DownloadView', 'download_tile_height'))

        self.sane_layout = QGridLayout()
        # self.sane_layout.setAlignment(Qt.AlignLeading)
        self.sane_layout.setContentsMargins(0, 1, 10, 0)
        # self.setContentsMargins(0, 1, 50, 0)

        self.title_bar = SmallLabel(self.video.title, parent=self)
        self.thumbnail = DownloadThumbnailWidget(self, self.video)
        self.progress_bar = DownloadProgressBar(self)

        self.percentage_downloaded = 0
        # self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.status = SmallLabel("Status:", parent=self)
        self.start_finish_dates = SmallLabel("Started/Finished on:", parent=self)
        self.duration = SmallLabel("Duration:", parent=self)
        self.upload = SmallLabel("Uploaded:", parent=self)
        self.eta = SmallLabel("ETA:", parent=self)
        self.speed = SmallLabel("Speed:", parent=self)
        self.total_size = SmallLabel("Total size:", parent=self)

        self.status_value = SmallLabel("No update", parent=self)
        self.start_finish_dates_value = SmallLabel("No update", parent=self)
        self.duration_value = SmallLabel(format(self.video.duration), parent=self)
        self.upload_value = SmallLabel(self.video.date_published.strftime("%Y-%m-%d %H:%M:%S"), parent=self)
        self.eta_value = SmallLabel("No update", parent=self)
        self.common_eta_str = "N/A"
        self.common_eta_calc_tick = 0
        self.etas = []
        self.speed_value = SmallLabel("No update:", parent=self)
        self.avg_speed_str = "N/A"
        self.avg_speed_calc_tick = 0
        self.speeds = []
        self.avg_calc_ticks = 50
        self.total_size_value = SmallLabel("No update:", parent=self)

        self.sane_layout.addWidget(self.title_bar, 0, 0, 1, 4)
        self.sane_layout.addWidget(self.thumbnail, 1, 0, 6, 1)
        self.sane_layout.addWidget(self.progress_bar, 8, 0, 1, 4)

        self.sane_layout.addWidget(self.status, 1, 1)
        self.sane_layout.addWidget(self.duration, 2, 1)
        self.sane_layout.addWidget(self.upload, 3, 1)
        self.sane_layout.addWidget(self.eta, 4, 1)
        self.sane_layout.addWidget(self.speed, 5, 1)
        self.sane_layout.addWidget(self.total_size, 6, 1)
        self.sane_layout.addWidget(self.start_finish_dates, 7, 1)

        self.sane_layout.addWidget(self.status_value, 1, 2)
        self.sane_layout.addWidget(self.duration_value, 2, 2)
        self.sane_layout.addWidget(self.upload_value, 3, 2)
        self.sane_layout.addWidget(self.eta_value, 4, 2)
        self.sane_layout.addWidget(self.speed_value, 5, 2)
        self.sane_layout.addWidget(self.total_size_value, 6, 2)
        self.sane_layout.addWidget(self.start_finish_dates_value, 7, 2)

        self.setLayout(self.sane_layout)

        if db_download_tile:
            self.update_from_db_tile(db_download_tile)
        else:
            pass
        self.logger.info("Added DL tile from DB: {}".format(self.video))

    def retry_existing(self, download_progress_listener):
        """
        Retry failed video download using the existing tile
        :param download_progress_listener:
        :return:
        """
        # TODO: Complete function for a more smoother non-destructive solution than regular retry()
        self.download_progress_listener = download_progress_listener

    def retry(self):
        """
        Retry failed video download by adding a new tile (and then deleting self)
        :return:
        """
        self.logger.warning("Retrying download (EXPERIMENTAL): {}".format(self.video))
        # Hook into the download process at the least messy level
        self.root.main_model.playback_grid_view_listener.tileDownloaded.emit(copy.deepcopy(self.video))

        # Commit seppuku!
        self.parent.clear_download_forced(self)

    def set_started_finished_on_label(self):
        if not self.started_date:
            started_date_str = "-"
        else:
            try:
                started_date_str = self.started_date.strftime("%Y-%m-%d %H:%M:%S")
            except NameError as ne_exc:
                self.logger.error("A NameError exception occurred: started_date_str.strftime", exc_info=ne_exc)
                started_date_str = "ERROR"
            except Exception as exc:
                self.logger.error("An unexpected exception occurred: started_date_str.strftime", exc_info=exc)
                started_date_str = "ERROR"
        if not self.finished_date:
            finished_date_str = "-"
        else:
            try:
                finished_date_str = self.finished_date.strftime("%Y-%m-%d %H:%M:%S")
            except NameError as ne_exc:
                self.logger.error("A NameError exception occurred: finished_date_str.strftime", exc_info=ne_exc)
                finished_date_str = "ERROR"
            except Exception as exc:
                self.logger.error("An unexpected exception occurred: finished_date_str.strftime", exc_info=exc)
                finished_date_str = "ERROR"

        self.start_finish_dates_value.setText(("{} / {}".format(started_date_str, finished_date_str)))

    def update_from_db_tile(self, db_download_tile):
        self.finished = db_download_tile.finished
        self.started_date = db_download_tile.started_date
        self.finished_date = db_download_tile.finished_date
        self.video = db_download_tile.video
        self.video_downloaded = db_download_tile.video_downloaded
        self.total_bytes = db_download_tile.total_bytes
        self.last_event = db_download_tile.last_event

        if self.last_event:
            self.update_progress(self.last_event)

        if self.finished:
            self.status_value.setText("Finished")
            self.progress_bar.finish()
        if self.paused:
            self.status_value.setText("Paused")
            self.progress_bar.pause()
        if self.failed:
            self.status_value.setText("FAILED")
            self.progress_bar.fail()

        # Started/Finished on info
        self.set_started_finished_on_label()

        self.speed_value.setText("")
        self.eta_value.setText("")

    def finished_download(self):
        self.finished = True
        self.progress_bar.setValue(1000)
        self.progress_bar.setFormat("100.0%")
        self.status_value.setText("Finished")
        self.eta_value.setText("")
        self.speed_value.setText("Was {}".format(self.speed_value.text()))
        self.finished_date = datetime.utcnow()
        self.set_started_finished_on_label()
        try:
            combined_size = self.total_bytes_video + self.total_bytes_audio
            self.total_size_value.setText(self.determine_si_unit(combined_size))
        except TypeError as te_exc:
            self.logger.error("A TypeError exception occurred while combining video+audio track sizes", exc_info=te_exc)
            self.total_size_value.setText("BUG: GitHub Issue #28")
        self.progress_bar.finish()
        DownloadViewListener.static_self.updateDownloadTile.emit(DDBDownloadTile(self))

    def humanize_dl_error(self, e):
        """
        Takes an Exception and returns a more human readable string.
        :param e:
        :return:
        """
        # Strip redundant parts of string added by modules like youtube_dl
        head, sep, tail = str(e).partition('ERROR: ')
        if tail == '':
            # If tail is empty, no match was found and the original string is stored in head.
            human_readable_error = head
        else:
            human_readable_error = tail

        if ' (caused by ' in human_readable_error:
            head, sep, tail = human_readable_error.partition(' (caused by ')
            human_readable_error = head

        # Go through a list of known errors and humanize where needed:
        if 'Unable to download webpage: <urlopen error [Errno 111] Connection refused>' in human_readable_error:
            human_readable_error = "Connection refused (Errno 111). Do you have a syntax error in proxy config?"
        # elif isinstance(e, ValueError):
        elif 'Port out of range 0-65535' in human_readable_error:
            human_readable_error += '. Check your proxy config.'

        return human_readable_error

    @pyqtSlot(Exception)
    def failed_download(self, e):
        """
        How to handle a failed download.

        Called by PyQtSignal connected to the download listener.
        :return:
        """
        human_readable_error = self.humanize_dl_error(e)
        self.logger.error("Failed download: {}".format(self.video))
        self.failed = True
        self.status_value.setText("FAILED: {}".format(human_readable_error))
        self.eta_value.setText("")
        self.speed_value.setText("Was {}".format(self.speed_value.text()))
        self.finished_date = datetime.utcnow()
        self.set_started_finished_on_label()
        self.download_progress_listener.threading_event.clear()
        self.progress_bar.fail()
        DownloadViewListener.static_self.updateDownloadTile.emit(DDBDownloadTile(self))

    def paused_download(self):
        self.logger.debug5("Paused download: {}".format(self.video))
        self.paused = True
        self.download_progress_listener.threading_event.clear()
        self.progress_bar.pause()

    def resumed_download(self):
        self.logger.debug5("Resumed download: {}".format(self.video))
        self.paused = False
        self.download_progress_listener.threading_event.set()
        self.progress_bar.resume()

    def determine_si_unit(self, byte_value):
        """
        Walks a size of bytes through SI Units until it finds the appropriate one to use.
        :param byte_value:
        :return:
        """
        si_units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
        for unit in si_units:
            if byte_value < 1024:
                # Cannot switch from manual field specification to automatic field numbering, thus separate variable.
                byte_value_formatted = "{0:.2f}".format(byte_value)
                return "{}{}".format(byte_value_formatted, unit)
            byte_value = byte_value / 1024

        # You should never reach this point
        self.logger.error("BUG in determine_si_unit: Bytes received larger than YiB unit!!!")
        return "Uh oh... (see log)"

    @staticmethod
    def determine_bytes(speed_str):
        """
        Determines how many actual bytes there is in a youtube_dl formatted speed rate string.
        :param speed_str: youtube_dl formatted speed rate string
        :return:
        """
        si_units_speed = {'B/s': 1, 'KiB/s': 1024, 'MiB/s': 1048576, 'GiB/s': 1073741824, 'TiB/s': 1099511627776,
                          'PiB/s': 1125899906842624, 'EiB/s': 1152921504606846976, 'ZiB/s': 1180591620717411303424,
                          'YiB/s': 1208925819614629174706176}
        if speed_str[-5:] in si_units_speed:
            speed_unit = speed_str[-5:].strip()  # Case: All other matches.
        elif speed_str[-3:] in si_units_speed and speed_str[-5:] not in si_units_speed:
            speed_unit = speed_str[:-3].strip()  # Case: 'B/s'.
        else:
            return None  # Skip invalid matches

        speed = float(speed_str[:-5].strip())

        return speed * si_units_speed[speed_unit]

    def calc_avg_speed(self, speed_str, ticks=None, debug=False):
        """
        Calculates the average speed during n amount of ticks
        :param speed_str:
        :param ticks: if not given self.avg_calc_ticks is used
        :return:
        """
        if not ticks:
            ticks = self.avg_calc_ticks
        if 'Unknown' not in speed_str:
            # Enough ticks to reach a verdict on avg rate
            if self.avg_speed_calc_tick >= ticks:
                try:
                    # Get average speed (float)
                    avg_speed = sum(self.speeds) / float(len(self.speeds))
                    # Determine human readable SI unit for speed given in bytes
                    self.avg_speed_str = self.determine_si_unit(avg_speed)
                    self.speeds.clear()
                    self.avg_speed_calc_tick = 0
                except Exception as exc:
                    # Log warning and skip until it gets a good speed value
                    self.logger.warning("Bad input to determine_bytes('{}')".format(speed_str), exc_info=exc)
            else:
                # Add speed in bytes to list of speeds
                try:
                    speed = self.determine_bytes(speed_str)
                    if speed:
                        # Only add valid speeds
                        self.speeds.append(speed)
                    else:
                        return
                except KeyError as ke_exc:
                    # FIXME: Handle B/s speed in determine_bytes (currently results in a KeyError).
                    # Non critical exception that only serves to spam down the logger.
                    if debug:
                        self.logger.debug5("KeyError exception occurred in calc_avg_speed: {}".format(speed_str),
                                           exc_info=ke_exc)
                    return

                # Increment tick (for valid speeds)
                self.avg_speed_calc_tick += 1

    def most_common_eta(self, time_str, ticks=None):
        """
        Calculates the most common ETA during n amount of ticks in order to give a more stable statistic.
        :param time_str:
        :param ticks: if not given self.avg_calc_ticks is used
        :return:
        """
        if not ticks:
            ticks = self.avg_calc_ticks
        if 'Unknown' not in time_str:
            # Enough ticks to reach a verdict on avg rate
            if self.avg_speed_calc_tick >= ticks:
                # Get most common ETA
                try:
                    self.common_eta_str = Counter(self.etas).most_common(1)[0][0]
                # Debug some unexpected 'IndexError: Out of range' cases (GH Issue #36).
                except IndexError as ie_exc:
                    self.logger.error("Unexpected IndexError in most_common_eta(time_str=={}, ticks={})"
                                      ", self.etas on next line:".format(time_str, ticks), exc_info=ie_exc)
                    self.logger.error(self.etas)
                    return None

                self.etas.clear()
                self.common_eta_calc_tick = 0
            else:
                # Add ETA str to a list
                self.etas.append(time_str)
                self.common_eta_calc_tick += 1

    def delete_incomplete_entry(self):
        """
        Deletes an incomplete entry from the parent (DownloadView).
        :return:
        """
        message = "Are you sure you want to remove '{}' from Downloads?".format(self.video.title)
        action = self.parent.clear_download_forced
        # Prompt user for a confirmation dialog which applies actions to caller if confirmed.
        self.root.confirmation_dialog(message, action, caller=self)

    def update_progress(self, event):
        self.last_event = event
        if not self.started_date:
            self.started_date = datetime.utcnow()
        if "status" in event:
            if event["status"] == "finished":
                if not self.video_downloaded:
                    self.video_downloaded = True
                    self.status_value.setText("Finished downloading video")
                else:
                    # It's not really finished until it calls finished_download()
                    self.status_value.setText("Postprocessing...")
            elif "downloading" == event["status"]:
                if self.paused:
                    self.status_value.setText("Download paused")
                elif self.failed:
                    self.status_value.setText("Download FAILED!")
                else:
                    if self.video_downloaded:
                        self.status_value.setText("Downloading audio")
                    else:
                        self.status_value.setText("Downloading video")
            else:
                self.status_value.setText(event["status"])
        # Started/Finished on info
        self.set_started_finished_on_label()
        if "_eta_str" in event:
            self.most_common_eta(event["_eta_str"])
            self.eta_value.setText("{} (avg: {})".format(event["_eta_str"], self.common_eta_str))
        if "_speed_str" in event:
            self.calc_avg_speed(event["_speed_str"])
            self.speed_value.setText("{} (avg: {}/s)".format(event["_speed_str"], self.avg_speed_str))
        if "_total_bytes_str" in event:
            self.total_size_value.setText(event["_total_bytes_str"])
        if "total_bytes" in event or "total_bytes_estimate" in event:
            if "total_bytes" not in event:
                event["total_bytes"] = event["total_bytes_estimate"]
            if self.total_bytes == int(event["total_bytes"]):
                pass
            else:
                self.logger.debug("Downloading new item: {}".format(event))
                self.total_bytes = int(event["total_bytes"])
                # Store total bytes for video and audio track in a safe place
                if not self.video_downloaded:
                    self.total_bytes_video = self.total_bytes
                self.total_bytes_audio = self.total_bytes
                # self.progress_bar.setMaximum(int(event["total_bytes"]))
        else:
            self.logger.warning("total_bytes not in: {}".format(event))
        if "downloaded_bytes" in event and self.total_bytes:
            self.progress_bar.setValue(int(int((event["downloaded_bytes"] / self.total_bytes) * 1000)))
            percentage_downloaded = int((event["downloaded_bytes"] / self.total_bytes) * 100)
            if percentage_downloaded > self.percentage_downloaded:
                self.percentage_downloaded = percentage_downloaded
                DownloadViewListener.static_self.updateDownloadTileEvent.emit(DDBDownloadTile(self))
        else:
            if "downloaded_bytes" not in event:
                self.logger.warning("downloaded_bytes not in: {}".format(event))
        if "_percent_str" in event:
            self.progress_bar.setFormat(event["_percent_str"])

    def contextMenuEvent(self, event):
        """
        Override context menu event to set own custom menu
        :param event:
        :return:
        """
        if self.download_progress_listener:
            menu = QMenu(self)

            is_paused = not self.download_progress_listener.threading_event.is_set()

            pause_action = None
            continue_dl_action = None
            retry_dl_action = None
            mark_dl_failed = None

            if is_paused and not self.failed:
                continue_dl_action = menu.addAction("Continue download")
            else:
                if not self.finished and not self.failed:
                    pause_action = menu.addAction("Pause download")

            if self.failed or (is_paused and self.failed):
                retry_dl_action = menu.addAction("Retry failed download")

            if not self.finished:
                delete_incomplete_entry = menu.addAction("Delete incomplete entry")

            if read_config('Debug', 'debug'):
                if not self.failed:
                    menu.addSeparator()
                    mark_dl_failed = menu.addAction("Mark download as FAILED")

            action = menu.exec_(self.mapToGlobal(event.pos()))

            if not self.finished and not self.failed:
                if action == pause_action and pause_action:
                    self.paused_download()
                elif action == continue_dl_action and continue_dl_action:
                    self.resumed_download()
                elif action == delete_incomplete_entry:
                    self.delete_incomplete_entry()

            if self.failed and not self.finished:
                if action == delete_incomplete_entry:
                    self.delete_incomplete_entry()

            if self.failed:
                if action == retry_dl_action:
                    self.logger.error("Implement retry failed download handling!")
                    self.retry()  # Highly experimental, brace for impact!

            if read_config('Debug', 'debug'):
                if not self.failed:
                    if action == mark_dl_failed:
                        self.logger.critical("DEBUG: Marking FAILED: {}".format(self.video))
                        # Send a custom Exception, due to failed_download requiring one by design (signal reasons).
                        self.failed_download(Exception("Manually marked as failed."))
