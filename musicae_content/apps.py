from django.apps import AppConfig

class MusicaeContentConfig(AppConfig):
    name = 'musicae_content'

    def ready(self):
        # ensure modeltranslation is imported
        import musicae_content.translation
