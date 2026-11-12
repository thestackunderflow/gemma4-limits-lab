# Part 13 filming container (SHOTLIST-13 §0.3): screen-lab kit base + jq + Firefox ESR (K7) + the Ollama CLIENT binary
# from the same pinned server image (no server runs here). Build: docker build -t film13:1 docker/film13
FROM ollama/ollama:0.40.16@sha256:910d0d8107b538fb0894e63163eb195de0cc7aefcbc666dc62d3b18f71124592 AS ollama
FROM screen-lab-base:1
RUN apt-get update && apt-get install -y --no-install-recommends jq curl ca-certificates gnupg wget \
 && install -d -m 0755 /etc/apt/keyrings \
 && wget -qO /etc/apt/keyrings/packages.mozilla.org.asc https://packages.mozilla.org/apt/repo-signing-key.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" > /etc/apt/sources.list.d/mozilla.list \
 && printf 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' > /etc/apt/preferences.d/mozilla \
 && apt-get update && apt-get install -y --no-install-recommends firefox-esr \
 && rm -rf /var/lib/apt/lists/*
COPY --from=ollama /bin/ollama /usr/local/bin/ollama
