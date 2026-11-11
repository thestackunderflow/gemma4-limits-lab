# Test and measurement runner: Python + pytest + requests/jsonschema + Pillow/matplotlib (lab images and charts)
# + espeak-ng / ffmpeg (audio control clip and resampling). Nothing here is installed on the host.
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends espeak-ng ffmpeg fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.3.3 requests==2.32.3 jsonschema==4.23.0 matplotlib==3.9.2 pillow==11.0.0 numpy==2.1.2
WORKDIR /work
