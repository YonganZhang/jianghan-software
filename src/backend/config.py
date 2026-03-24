import os

import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "wenjie.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get("SECRET_KEY", "WANGwenjie-yunyun")
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

# Supported locale regions for date/number formatting
LOCALE_DB = os.path.join(BASE_DIR, "instance", "metrics_data.dat")
LOCALE_REGIONS = {
    "Hubei": "zh_CN", "Zhejiang": "zh_CN", "Shaanxi": "zh_CN",
    "Shanxi": "zh_CN", "Beijing": "zh_CN",
}
