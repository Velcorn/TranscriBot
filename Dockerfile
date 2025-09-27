# Install uv
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install locales and generate de_DE.UTF-8
# This ensures that the 'de_DE.UTF-8' locale is available for your Python script.
# Debian-based images like Bookworm use apt.
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && locale-gen de_DE.UTF-8

# Set environment variables for the locale
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE:en
ENV LC_ALL de_DE.UTF-8

# Copy project
ADD . /TranscriBot
ADD . .

# Sync project
RUN uv sync --locked

# Run main.py
CMD ["uv", "run", "main.py"]
