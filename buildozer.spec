name: Build JARVIS ULTIMATE APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v5

      - name: Set up Java 17
        uses: actions/setup-java@v5
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Set up Python 3.10
        uses: actions/setup-python@v6
        with:
          python-version: '3.10'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y python3-pip openjdk-17-jdk zip unzip libffi-dev libssl-dev libbz2-dev libsqlite3-dev zlib1g-dev libncurses5-dev
          pip install --upgrade pip
          pip install cython==0.29.33 buildozer

      - name: Build with Buildozer
        run: |
          yes | buildozer -v android debug || (
            echo "⚠️ البناء الكامل فشل، نحاول البناء الخفيف بدون moviepy..."
            cp buildozer.spec buildozer.spec.full
            sed -i 's/requirements =.*/requirements = python3,kivy,plyer,pyjnius,Pillow,gTTS,requests/' buildozer.spec
            yes | buildozer -v android debug
          )

      - name: Upload APK
        uses: actions/upload-artifact@v5
        with:
          name: JARVIS-ULTIMATE-APK
          path: bin/*.apk
          retention-days: 10
