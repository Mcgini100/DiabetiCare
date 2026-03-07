import sys
import os

# Add project root to Python path so imports work in Vercel serverless
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import create_app

app = create_app()
