from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def create_news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comment_list(news, author):
    now = timezone.now()
    for index in range(10):
        comments = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comments.created = now + timedelta(days=index)
        comments.save()


@pytest.fixture()
def home_url():
    url = reverse('news:home')
    return url


@pytest.fixture()
def news_detail_url(news):
    url = reverse('news:detail', args=(news.id,))
    return url


@pytest.fixture()
def news_delete_url(comment):
    url = reverse('news:delete', args=(comment.id,))
    return url


@pytest.fixture()
def news_edit_url(comment):
    url = reverse('news:edit', args=(comment.id,))
    return url


@pytest.fixture()
def users_login_url():
    url = reverse('users:login')
    return url


@pytest.fixture()
def users_signup_url():
    url = reverse('users:signup')
    return url
