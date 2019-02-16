import mistune

from django.views.decorators.http import require_GET

from utils.metrics import api_metric
from utils.http_tools import SuccessResponse, ParamInvalidResponse, ObjectNotExistResponse
from utils.logger import logger

from .models import Topic, Comment


@require_GET
@api_metric
def query_topics(request):
    topic_qs = Topic.objects.all()
    topic_list = []
    for topic in topic_qs:
        topic_list.append({
            'id': topic.id,
            'title': topic.title,
            'create_dt': topic.create_dt,
            'update_dt': topic.update_dt,
            'pin': topic.pin,
            'archive': topic.archive,
            'comment_count': topic.comment_set.count(),
        })
    logger.debug('query topics|%s', len(topic_list))
    return SuccessResponse(topic_list)


@require_GET
@api_metric
def query_topic_comments(request):
    try:
        id_ = int(request.GET['id'])
    except KeyError:
        logger.warning('param id not exist')
        return ParamInvalidResponse()

    try:
        topic = Topic.objects.get(id=id_)
    except Topic.DoesNotExist:
        logger.warning('topics not exist|%s', id_)
        return ObjectNotExistResponse()

    comment_qs = Comment.objects.filter(topic=topic)
    comment_list = []
    for comment in comment_qs:
        comment_list.append({
            'id': comment.id,
            'content': mistune.markdown(comment.content),
            'create_dt': comment.create_dt,
        })

    logger.debug('query topic comment|%d|%s|%d', id_, topic.title, len(comment_list))

    return SuccessResponse({
        'topic': {
            'id': topic.id,
            'title': topic.title,
            'create_dt': topic.create_dt,
            'update_dt': topic.update_dt,
            'archive': topic.archive,
        },
        'comment_list': comment_list,
    })
