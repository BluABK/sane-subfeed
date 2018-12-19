from __future__ import unicode_literals

from youtube_dl.postprocessor.embedthumbnail import EmbedThumbnailPP
from youtube_dl.postprocessor.execafterdownload import ExecAfterDownloadPP
from youtube_dl.postprocessor.metadatafromtitle import MetadataFromTitlePP
from youtube_dl.postprocessor.xattrpp import XAttrMetadataPP

from .ffmpeg import (
    SaneFFmpegPostProcessor,
    SaneFFmpegEmbedSubtitlePP,
    SaneFFmpegExtractAudioPP,
    SaneFFmpegFixupStretchedPP,
    SaneFFmpegFixupM3u8PP,
    SaneFFmpegFixupM4aPP,
    SaneFFmpegMergerPP,
    SaneFFmpegMetadataPP,
    SaneFFmpegVideoConvertorPP,
    SaneFFmpegSubtitlesConvertorPP,
)


def get_postprocessor(key):
    return globals()[key + 'PP']


__all__ = [
    'EmbedThumbnailPP',
    'ExecAfterDownloadPP',
    'SaneFFmpegEmbedSubtitlePP',
    'SaneFFmpegExtractAudioPP',
    'SaneFFmpegFixupM3u8PP',
    'SaneFFmpegFixupM4aPP',
    'SaneFFmpegFixupStretchedPP',
    'SaneFFmpegMergerPP',
    'SaneFFmpegMetadataPP',
    'SaneFFmpegPostProcessor',
    'SaneFFmpegSubtitlesConvertorPP',
    'SaneFFmpegVideoConvertorPP',
    'MetadataFromTitlePP',
    'XAttrMetadataPP',
]
