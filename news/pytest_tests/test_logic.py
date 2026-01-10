from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_anonymous_user_cant_create_comment(client, news, news_detail_url):
    comments_count_before = Comment.objects.count()
    form_data = {'text': COMMENT_TEXT}
    client.post(news_detail_url, data=form_data)
    comments_count_now = Comment.objects.count()

    assert comments_count_before == comments_count_now


def test_user_can_create_comment(author_client, author, news, news_detail_url):
    Comment.objects.all().delete()
    assert Comment.objects.count() == 0
    form_data = {'text': COMMENT_TEXT}
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, news_detail_url):
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    comments_count_now = Comment.objects.count()
    assert comments_count_before == comments_count_now
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
    author_client,
    news,
    comment,
    not_author_client,
    news_detail_url,
    news_delete_url
):
    comments_count_before = Comment.objects.count()
    url_to_comments = news_detail_url + '#comments'
    response = author_client.delete(news_delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_before - 1 == comments_count_after


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment, news_delete_url
):
    comments_count_before = Comment.objects.count()
    response = not_author_client.delete(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_author_can_edit_comment(
    author_client, news, comment, news_detail_url, news_edit_url
):
    url_to_comments = news_detail_url + '#comments'
    form_data = {'text': NEW_COMMENT_TEXT}

    response = author_client.post(news_edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == NEW_COMMENT_TEXT
    assert comment.author == comment_from_db.author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
    not_author_client, news, comment, news_edit_url
):
    form_data = {'text': NEW_COMMENT_TEXT}
    response = not_author_client.post(news_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == news
