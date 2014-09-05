from segments.models import Segment, SegmentExecutionError
from celery import task
from time import time
import logging

logger = logging.getLogger(__name__)


@task
def refresh_segments():
    """Celery task to refresh all segments, with timing information. Writes to the logger."""
    start = time()
    failed = []
    segments = list(Segment.objects.all())
    for s in segments:
        start_seg = time()

        try:
            s.refresh()
        except SegmentExecutionError:
            failed.append(s)

        end_seg = time()
        logger.info("SEGMENTS: Refreshed segment %s (id: %s) in %s milliseconds", (s.name, s.id, (end_seg - start_seg) * 1000))

    end = time()
    logger.info("SEGMENTS: Successfully refreshed %s segments. Failed to refresh %s segments. Complete in %s seconds"
                % (len(segments)-len(failed), len(failed), end - start))

@task
def refresh_segment(segment_id):
    """Celery task to refresh an individual Segment."""
    try:
        s = Segment.objects.get(pk=segment_id)
        s.refresh()
    except Segment.DoesNotExist:
        logger.exception("SEGMENTS: Unable to refresh segment id %s. DoesNotExist.", segment_id)