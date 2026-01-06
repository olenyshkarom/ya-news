from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

pytestmark = pytest.mark.django_db


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


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    [
        (lf('news_edit_url'), lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('news_delete_url'), lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('news_edit_url'), lf('author_client'), HTTPStatus.OK),
        (lf('news_delete_url'), lf('author_client'), HTTPStatus.OK),
        (lf('news_detail_url'), lf('client'), HTTPStatus.OK),
        (lf('home_url'), lf('client'), HTTPStatus.OK),
        (lf('users_login_url'), lf('client'), HTTPStatus.OK),
        (lf('users_signup_url'), lf('client'), HTTPStatus.OK)
    ],
)
def test_pages_availability_for_different_users(
    comment, reverse_url, parametrized_client, expected_status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == expected_status
