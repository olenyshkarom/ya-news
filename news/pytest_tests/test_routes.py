from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

# from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db
STATUS_OK = HTTPStatus.OK
STATUS_NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    (lf('news_edit_url'), lf('news_delete_url'))
)
def test_redirects(client, comment, name, users_login_url):
    url = name
    expected_url = f'{users_login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    [
        (lf('news_edit_url'), lf('not_author_client'), STATUS_NOT_FOUND),
        (lf('news_delete_url'), lf('not_author_client'), STATUS_NOT_FOUND),
        (lf('news_edit_url'), lf('author_client'), STATUS_OK),
        (lf('news_delete_url'), lf('author_client'), STATUS_OK),
        (lf('news_detail_url'), lf('client'), STATUS_OK),
        (lf('home_url'), lf('client'), STATUS_OK),
        (lf('users_login_url'), lf('client'), STATUS_OK),
        (lf('users_signup_url'), lf('client'), STATUS_OK)
    ],
)
def test_pages_availability_for_different_users(
    comment, reverse_url, parametrized_client, expected_status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == expected_status




# @pytest.mark.parametrize(
#     'reverse_url, parametrized_client, expected_status',
#     [
#         (
#             pytest.lazy_fixture('news_edit_url'),
#             pytest.lazy_fixture('not_author_client'),
#             HTTPStatus.NOT_FOUND
#         ),
#         (
#             pytest.lazy_fixture('news_delete_url'),
#             pytest.lazy_fixture('not_author_client'),
#             HTTPStatus.NOT_FOUND
#         ),
#         (
#             pytest.lazy_fixture('news_edit_url'),
#             pytest.lazy_fixture('author_client'),
#             HTTPStatus.OK
#         ),
#         (
#             pytest.lazy_fixture('news_delete_url'),
#             pytest.lazy_fixture('author_client'),
#             HTTPStatus.OK
#         ),
#         (
#             pytest.lazy_fixture('news_detail_url'),
#             pytest.lazy_fixture('client'),
#             HTTPStatus.OK
#         ),
#         (
#             pytest.lazy_fixture('home_url'),
#             pytest.lazy_fixture('client'),
#             HTTPStatus.OK
#         ),
#         (
#             pytest.lazy_fixture('users_login_url'),
#             pytest.lazy_fixture('client'),
#             HTTPStatus.OK
#         ),
#         (
#             pytest.lazy_fixture('users_signup_url'),
#             pytest.lazy_fixture('client'),
#             HTTPStatus.OK
#         )
#     ],
# )
# def test_pages_availability_for_different_users(
#     comment, reverse_url, parametrized_client, expected_status
# ):
#     response = parametrized_client.get(reverse_url)
#     assert response.status_code == expected_status