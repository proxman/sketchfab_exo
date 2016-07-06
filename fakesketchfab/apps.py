from django.apps import AppConfig
from django.db.models.signals import post_save


class FakesketchfabConfig(AppConfig):
    name = 'fakesketchfab'

    def ready(self):
        from actstream import registry
        from badgesfab import signals
        models_to_register = ['SketchFabUser', 'Model3d', 'ModelDescription']
        for model in models_to_register:
            registry.register(self.get_model(model))
            post_save.connect(
                receiver=signals.modelSaveSignal,
                sender=self.get_model(model)
            )


