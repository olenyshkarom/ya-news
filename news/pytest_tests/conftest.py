import pytest

# Импортируем класс клиента.
from django.test.client import Client
from news.models import Comment, News

from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client

@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client

@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки.
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


# @pytest.mark.django_db
@pytest.fixture
def create_news_list(db):
    def make_news(count):
        today = datetime.today()    # Вычисляем текущую дату.
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                # Для каждой новости уменьшаем дату на index дней от today,
                # где index - счётчик цикла.
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)
    return make_news


@pytest.fixture
def create_comment_list(news, author):
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comments = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comments.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comments.save()
    return comments
