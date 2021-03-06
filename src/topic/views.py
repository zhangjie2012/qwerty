from utils.md_render import md_render_with_hl
from utils.http_tools import SuccessResponse, ParamInvalidResponse, \
    ObjectNotExistResponse, get_client_info
from utils.restful import RESTful
from utils.logger import logger

from .models import Topic, Comment


class Topics(RESTful):
    def get(self, request):
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


class Comments(RESTful):
    def get(self, request):
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

        topic.add_pv_atomic()

        comment_qs = Comment.objects.filter(topic=topic).order_by('create_dt')
        comment_list = []
        for comment in comment_qs:
            comment_list.append({
                'id': comment.id,
                'content': md_render_with_hl(comment.content),
                'create_dt': comment.create_dt,
            })

        ip, browser, os, device = get_client_info(request)
        logger.debug('query topic comment|%d|%s|%d|%s|%s|%s|%s',
                     id_, topic.title, len(comment_list),
                     ip, browser, os, device,)

        return SuccessResponse({
            'topic': {
                'id': topic.id,
                'title': topic.title,
                'create_dt': topic.create_dt,
                'update_dt': topic.update_dt,
                'archive': topic.archive,
                'pv': topic.pv,
            },
            'comment_list': comment_list,
        })
