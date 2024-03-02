from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from notes.models import Note
from notes.forms import WARNING
from .mixins import SetUpTestDataMixin
from . utils import assert_note_form_data, assert_note_from_database

User = get_user_model()


class TestNoteCreationEmptySlug(TestCase, SetUpTestDataMixin):

    @classmethod
    def setUpTestData(cls):
        SetUpTestDataMixin.setUpTestData()
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        note_count = Note.objects.count()
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        note_count = Note.objects.count()
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), note_count)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        note_count = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteSlugEditDelete(TestCase, SetUpTestDataMixin):

    @classmethod
    def setUpTestData(cls):
        SetUpTestDataMixin.setUpTestData()
        cls.reader = User.objects.create(username='Не автор')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
        }

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        note_count = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        assertFormError(response,
                        'form',
                        'slug',
                        errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), note_count)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        assert_note_form_data(self.note, self.form_data)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        assert_note_from_database(self.note, note_from_db)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        note_count = Note.objects.count()
        response = self.author_client.post(url)
        assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count - 1)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        note_count = Note.objects.count()
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count)
