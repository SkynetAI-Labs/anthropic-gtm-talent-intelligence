"""Public demonstration entry point: isolate each visitor's fictional pipeline."""
import os
import runpy
from pathlib import Path
os.environ['GTM_PUBLIC_DEMO']='1'
runpy.run_path(str(Path(__file__).resolve().parent/'app/dashboard.py'),run_name='__main__')
