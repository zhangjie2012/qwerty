import json

from datetime import datetime
from collections import defaultdict
from libgravatar import Gravatar
from django.core.paginator import Paginator

from utils.md_render import md_render_with_hl
from utils.logger import logger
from utils.http_tools import SuccessResponse, \
    ParamInvalidResponse, ObjectNotExistResponse, get_client_info
from utils.restful import RESTful
from .models import Category, Article, Comment


class Blogs(RESTful):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        per_count = int(request.GET.get('per_count', 10))

        # param error auto fix
        page = 1 if page < 1 else page
        per_count = 10 if per_count < 1 else per_count

        article_qs = Article.objects.exclude(draft=True).values(
            'category__name', 'category__slug',
            'title', 'slug', 'abstract', 'publish_dt'
        )
        paginator = Paginator(article_qs, per_count)
        page_article = paginator.get_page(page)

        article_list = []
        for article in page_article.object_list:
            article_list.append({
                'category': {
                    'name': article['category__name'],
                    'slug': article['category__slug'],
                },
                'title': article['title'],
                'slug': article['slug'],
                'abstract': article['abstract'],
                'publish_dt': article['publish_dt'],
            })

        logger.debug('query blogs|%d|%d|%d', page, per_count, len(article_list))

        return SuccessResponse({
            'article_list': article_list,
            'current_page_num': page_article.number,
            'total_pages': paginator.num_pages,
        })


class Blog(RESTful):
    def get(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            logger.warning('slug article not exist|%s', slug)
            return ObjectNotExistResponse()

        article.add_pv_atomic()

        comment_qs = article.comment_set.filter(show=True).values(
            'username', 'avatar', 'website', 'content', 'publish_dt'
        ).order_by('publish_dt')
        comment_list = []
        for comment in comment_qs:
            comment_list.append({
                'username': comment['username'],
                'avatar': comment['avatar'],
                'website': comment['website'],
                'publish_dt': comment['publish_dt'],
                'content': md_render_with_hl(comment['content'])
            })

        data = {
            'category': {
                'name': article.category.name,
                'slug': article.category.slug,
            },
            'title': article.title,
            'cover_img': article.cover_img,
            'img_copyright': article.img_copyright,
            'abstract': article.abstract,
            'content': md_render_with_hl(article.content),
            'publish_dt': article.publish_dt,
            'update_dt': article.update_dt,
            'pv': article.pv,
            'comment_list': comment_list,
        }

        ip, browser, os, device = get_client_info(request)
        logger.debug('query blog detail|%s|%s|%d|%s|%s|%s|%s',
                     slug, article.title, len(comment_list),
                     ip, browser, os, device)

        return SuccessResponse(data)


class Categories(RESTful):
    def get(self, request):
        category_qs = Category.objects.all()

        data = []
        for category in category_qs:
            article_qs = category.article_set.exclude(draft=True).values(
                'title', 'slug', 'publish_dt')
            data.append({
                'category': {
                    'name': category.name,
                    'slug': category.slug,
                },
                'articles': list(article_qs),
            })

        logger.debug('query blog categories')

        return SuccessResponse(data)


class Archives(RESTful):
    def get(self, request):
        article_qs = Article.objects.exclude(
            draft=True).values('title', 'slug', 'publish_dt')

        # archive by year
        year_2_articles = defaultdict(list)
        for article in article_qs:
            year = article['publish_dt'].year
            year_2_articles[year].append(article)

        # be order
        data = []
        for year, articles in year_2_articles.items():
            data.append({
                'year': year,
                'articles': articles,
            })

        logger.debug('query archive blogs')

        return SuccessResponse(data)


class Comments(RESTful):
    def post(self, request):
        try:
            body = json.loads(request.body)
            slug = body['slug']
            username = body['username']
            email = body['email']
            website = body['website']
            content = body['comment']

            ip, browser, os, _ = get_client_info(request)
        except (KeyError, json.JSONDecodeError):
            logger.warning('param invalid|%s', request.body.decode('utf-8'))
            return ParamInvalidResponse()

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            logger.warning('article not exist|%s', slug)
            return ObjectNotExistResponse()

        comment = Comment.objects.create(
            article=article,
            username=username,
            email=email,
            avatar=Gravatar(email).get_image(),
            website=website,
            content=content,
            publish_dt=datetime.now(),
            ipv4=ip,
            browser=browser,
            os=os
        )

        logger.info('add comment|%s|%s|%s', article.slug, article.title, comment.username)

        return SuccessResponse()
