from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


class SetUpTestDataMixin:
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'note-slug'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'
    NEW_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Не автор')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
