"""Built-in mappings from Debian to Arch Linux packages."""

# Direct package name mappings
# format: "debian_name": "arch_name"
NAME_MAPPINGS = {
    # Base system
    "libc6": "glibc",
    "libssl3": "openssl",
    "zlib1g": "zlib",
    "libbz2-1.0": "bzip2",
    "liblzma5": "xz",
    "libzstd1": "zstd",
    
    # Python
    "python3": "python",
    "python3-dev": "python",
    "python3-pip": "python-pip",
    "python3-venv": "python",  # Included in python package
    "python3-setuptools": "python-setuptools",
    "python3-wheel": "python-wheel",
    
    # Common libraries
    "libgl1": "libglvnd",
    "libx11-6": "libx11",
    "libxext6": "libxext",
    "libxi6": "libxi",
    "libxrender1": "libxrender",
    "libxtst6": "libxtst",
    "libasound2": "alsa-lib",
    "libfreetype6": "freetype2",
    "libfontconfig1": "fontconfig",
    "libexpat1": "expat",
    "libdbus-1-3": "dbus",
    "libsqlite3-0": "sqlite",
    "libncurses5": "ncurses",
    "libncurses6": "ncurses",
    "libtinfo5": "ncurses",
    "libtinfo6": "ncurses",
    "libreadline8": "readline",
    "libffi8": "libffi",
    
    # GTK/Glib
    "libglib2.0-0": "glib2",
    "libgtk-3-0": "gtk3",
    "libgdk-pixbuf2.0-0": "gdk-pixbuf2",
    "libpango-1.0-0": "pango",
    "libcairo2": "cairo",
    
    # Qt
    "libqt5core5a": "qt5-base",
    "libqt5gui5": "qt5-base",
    "libqt5widgets5": "qt5-base",
    
    # X11/Wayland
    "libwayland-client0": "wayland",
    "libwayland-cursor0": "wayland",
    "libwayland-egl1": "wayland",
    
    # Tools
    "curl": "curl",
    "wget": "wget",
    "git": "git",
    "make": "make",
    "gcc": "gcc",
}

# Virtual package mappings
# Can map to multiple alternatives, listing preferred first
VIRTUAL_MAPPINGS = {
    "www-browser": ["firefox", "chromium", "lynx"],
    "x-terminal-emulator": ["gnome-terminal", "alacritty", "kitty", "xterm"],
    "editor": ["vim", "nano", "vi"],
}
