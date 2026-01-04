import pytest
from http import HTTPStatus

from django.urls import reverse
# from news.models import News
from pytest_django.asserts import assertRedirects


# Главная страница доступна анонимному пользователю.
@pytest.mark.django_db
# Указываем в фикстурах встроенный клиент.
def test_home_availability_for_anonymous_user(client):
    # Адрес страницы получаем через reverse():
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.
@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# Страница отдельной новости доступна анонимному пользователю.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
def test_pages_availability_news_for_anonymous_user(client, name, news):
    url = reverse(name, args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Страницы удаления и редактирования комментария доступны автору комментария.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_availability_comment_for_author(author_client, comment, name):
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


# При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirects(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


# Авторизованный пользователь не может зайти на страницы редактирования или удаления чужих комментариев (возвращается ошибка 404).
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_availability_for_different_users(not_author_client, comment, name):
    url = reverse(name, args=(comment.id,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
