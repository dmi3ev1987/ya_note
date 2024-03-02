def assert_note_form_data(note, form_data):
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def assert_note_from_database(note, note_from_db):
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug
