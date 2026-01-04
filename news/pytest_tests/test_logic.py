import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

# Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    response = client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count == 0


@pytest.mark.django_db
# Авторизованный пользователь может отправить комментарий.
def test_user_can_create_comment(author_client, author, news):
    # Совершаем запрос через авторизованный клиент.
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    response = author_client.post(url, data=form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{url}#comments')
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Убеждаемся, что есть один комментарий.
    assert comments_count == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


# Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=bad_words_data)
    form = response.context['form']
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


# Авторизованный пользователь может редактировать или удалять свои комментарии.

@pytest.mark.django_db
# Проверим, что автор может удалить свой комментарий:
def test_author_can_delete_comment(author_client, news, comment, not_author_client):
    
    news_url = reverse('news:detail', args=(news.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.

    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    assertRedirects(response, url_to_comments)
    # Заодно проверим статус-коды ответов.
    assert response.status_code == HTTPStatus.FOUND
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert comments_count == 0

@pytest.mark.django_db
# Теперь проверим, что пользователь не может удалить чужой комментарий.
def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    # Выполняем запрос на удаление от пользователя-читателя.
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, news, comment):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': NEW_COMMENT_TEXT}

    # Выполняем запрос на редактирование от имени автора комментария.
    response = author_client.post(edit_url, data=form_data)
    # Проверяем, что сработал редирект.
    assertRedirects(response, url_to_comments)
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == NEW_COMMENT_TEXT


# редактирование комментария недоступно для другого пользователя.
def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': NEW_COMMENT_TEXT}

    # Выполняем запрос на редактирование от имени другого пользователя.
    response = not_author_client.post(edit_url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == COMMENT_TEXT
