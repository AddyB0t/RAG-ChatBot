import logging

logger = logging.getLogger(__name__)

class FlairLoader:
    _instance = None
    _tagger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self):
        if self._tagger is None:
            try:
                import torch
                original_load = torch.load

                def patched_load(*args, **kwargs):
                    if 'weights_only' not in kwargs:
                        kwargs['weights_only'] = False
                    return original_load(*args, **kwargs)

                torch.load = patched_load

                from flair.models import SequenceTagger
                self._tagger = SequenceTagger.load("flair/ner-english-large")
                logger.info("Flair NER model loaded successfully")

                torch.load = original_load

            except Exception as e:
                logger.error(f"Failed to load Flair model: {e}")
                self._tagger = None

        return self._tagger

_flair_loader_instance = None

def get_flair_model():
    global _flair_loader_instance
    if _flair_loader_instance is None:
        _flair_loader_instance = FlairLoader()
    return _flair_loader_instance.get_model()

