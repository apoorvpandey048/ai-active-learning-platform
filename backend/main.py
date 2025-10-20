"""Entrypoint for cloud deployment (Hugging Face Space or generic host).

This script preloads HF models synchronously at startup so users don't wait
for downloads on first request. Run with: python main.py
It will start the existing Flask `app` defined in backend/app.py.
"""
import os
import logging
import importlib.util
import sys

# Load backend/app.py as a module named 'backend_app' so we can reference the Flask app
BACKEND_APP_PATH = os.path.join(os.path.dirname(__file__), 'app.py')
spec = importlib.util.spec_from_file_location('backend_app', BACKEND_APP_PATH)
webapp_module = importlib.util.module_from_spec(spec)
sys.modules['backend_app'] = webapp_module
spec.loader.exec_module(webapp_module)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger('main')


def preload_models_if_needed():
    """Preload HF models synchronously by invoking the function in app.py
    or by building pipelines directly if necessary."""
    try:
        # If the app module exposes the background loader, call it now (synchronously)
        if hasattr(webapp_module, '_background_load_models'):
            log.info('Preloading models via app._background_load_models()')
            webapp_module._background_load_models()
            log.info('Preloading complete')
            return
    except Exception:
        log.exception('Preloading via app._background_load_models failed; will try fallback')

    # Fallback: try to import transformers and load commonly used pipelines
    try:
        from transformers import pipeline
        log.info('Fallback preload: loading summarizer and generator pipelines')
        webapp_module._hf_summarizer = pipeline('summarization', model=webapp_module.SUMMARIZER_MODEL)
        webapp_module._hf_summarizer_ready = True
        webapp_module._hf_generator = pipeline('text2text-generation', model=webapp_module.GENERATOR_MODEL)
        webapp_module._hf_generator_ready = True
        log.info('Fallback preload complete')
    except Exception:
        log.exception('Fallback preload failed; models may not be available')


def main():
    # Explicitly enable HF background flag so app logs reflect intended behavior
    os.environ.setdefault('ENABLE_HF_BACKGROUND', '1')

    # Preload models before starting the server
    preload_models_if_needed()

    # Start Flask app on the port provided by the host (Hugging Face Spaces uses PORT env var)
    port = int(os.environ.get('PORT', os.environ.get('HF_SPACE_PORT', '7860')))
    host = '0.0.0.0'
    log.info('Starting Flask app on %s:%d', host, port)
    # webapp_module.app is the Flask app defined in backend/app.py
    webapp_module.app.run(host=host, port=port)


if __name__ == '__main__':
    main()
