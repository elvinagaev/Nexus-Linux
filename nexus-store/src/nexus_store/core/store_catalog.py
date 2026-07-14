"""Application catalog for Nexus Store."""

from nexus_common.package_cache import CacheablePackage

STORE_CATALOG = [
    CacheablePackage(id="firefox", name="Firefox", packages=["firefox-esr"], description="Web browser"),
    CacheablePackage(id="vlc", name="VLC", packages=["vlc"], description="Media player"),
    CacheablePackage(id="gimp", name="GIMP", packages=["gimp"], description="Image editor"),
    CacheablePackage(
        id="libreoffice", name="LibreOffice", packages=["libreoffice"], description="Office suite",
    ),
    CacheablePackage(
        id="blender", name="Blender", packages=["blender"], description="3D creation suite",
    ),
    CacheablePackage(id="vscode", name="VS Code", packages=["code"], description="Code editor"),
    CacheablePackage(
        id="discord", name="Discord", packages=["discord"], description="Voice and text chat",
    ),
    CacheablePackage(
        id="thunderbird", name="Thunderbird", packages=["thunderbird"], description="Email client",
    ),
]
