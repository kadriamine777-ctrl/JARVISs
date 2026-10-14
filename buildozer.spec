name: Build JARVIS ULTIMATE APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install system dependencies
        run: |
          sudo apt update
          sudo apt install -y python3-pip openjdk-17-jdk zip unzip ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good
          pip install --upgrade pip
          pip install buildozer cython==0.29.33 virtualenv

      - name: Build with Buildozer
        run: |
          # حاول البناء الكامل مع moviepy
          buildozer -v android debug || (
            echo "⚠️ البناء الكامل فشل، نحاول البناء الخفيف بدون moviepy..."
            # بناء خفيف بدون moviepy لو فشل
            cp buildozer.spec buildozer.spec.full
            sed -i 's/requirements =.*/requirements = python3,kivy==2.2.0,plyer,pyjnius,Pillow,gTTS,requests/' buildozer.spec
            buildozer -v android debug
          )

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: JARVIS-ULTIMATE-APK
          path: bin/*.apk
          retention-days: 10
