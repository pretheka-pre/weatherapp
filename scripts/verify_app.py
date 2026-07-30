import unittest
import base64
from pathlib import Path
icon_path = Path(__file__).resolve().parent.parent / 'static' / 'images' / 'icon.png'
icon_path.parent.mkdir(parents=True, exist_ok=True)
icon_bytes = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQwAAwABJQ0fHAAAAAElFTkSuQmCC')
icon_path.write_bytes(icon_bytes)
suite = unittest.defaultTestLoader.discover('tests')
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
