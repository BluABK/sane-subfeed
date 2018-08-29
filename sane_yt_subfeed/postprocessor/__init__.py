from __future__ import unicode_literals

from youtube_dl.postprocessor.embedthumbnail import EmbedThumbnailPP
from .ffmpeg import (
    FFmpegPostProcessor,
    FFmpegEmbedSubtitlePP,
    FFmpegExtractAudioPP,
    FFmpegFixupStretchedPP,
    FFmpegFixupM3u8PP,
    FFmpegFixupM4aPP,
    FFmpegMergerPP,
    FFmpegMetadataPP,
    FFmpegVideoConvertorPP,
    FFmpegSubtitlesConvertorPP,
)
from youtube_dl.postprocessor.xattrpp import XAttrMetadataPP
from youtube_dl.postprocessor.execafterdownload import ExecAfterDownloadPP
from youtube_dl.postprocessor.metadatafromtitle import MetadataFromTitlePP


def get_postprocessor(key):
    return globals()[key + 'PP']


__all__ = [
    'EmbedThumbnailPP',
    'ExecAfterDownloadPP',
    'FFmpegEmbedSubtitlePP',
    'FFmpegExtractAudioPP',
    'FFmpegFixupM3u8PP',
    'FFmpegFixupM4aPP',
    'FFmpegFixupStretchedPP',
    'FFmpegMergerPP',
    'FFmpegMetadataPP',
    'FFmpegPostProcessor',
    'FFmpegSubtitlesConvertorPP',
    'FFmpegVideoConvertorPP',
    'MetadataFromTitlePP',
    'XAttrMetadataPP',
]