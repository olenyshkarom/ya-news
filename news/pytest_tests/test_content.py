import pytest
from django.urls import reverse
from django.conf import settings
from news.forms import CommentForm



# Количество новостей на главной странице — не более 10.
@pytest.mark.django_db
def test_news_count_on_home_page(client, create_news_list):
    # Создаем новостей больше, чем разрешено настройками (например, 11)
    over_limit = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    create_news_list(over_limit)
    
    # Делаем запрос к главной странице
    url = reverse('news:home')
    response = client.get(url)
    
    # Проверяем количество новостей в контексте (object_list из ListView)
    news_count = len(response.context['object_list'])
    
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE
    assert news_count == 10  # Если NEWS_COUNT_ON_HOME_PAGE = 10


# Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
@pytest.mark.django_db
def test_news_order(client, create_news_list):

    over_limit = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    create_news_list(over_limit)
    url = reverse('news:home')
    response = client.get(url)

    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
    # assert len(all_dates) > 1


# Комментарии на странице отдельной новости отсортированы от старых к новым: старые в начале списка, новые — в конце.
@pytest.mark.django_db
def test_comments_order(client, news, create_comment_list):
    detail_url = reverse('news:detail', args=(news.id,))
    response =client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


# Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости, а авторизованному доступна.
# Тест наличия формы в словаре контекста
# при запросе анонимного пользователя форма не передаётся в словаре контекста,
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


# при запросе авторизованного пользователя форма передаётся в словаре контекста.
@pytest.mark.django_db
def test_authorized_client_has_form(client, news, author):
    # Авторизуем клиент при помощи ранее созданного пользователя.
    detail_url = reverse('news:detail', args=(news.id,))
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
    # Проверим, что объект формы соответствует нужному классу формы.
    assert isinstance(response.context['form'], CommentForm)
