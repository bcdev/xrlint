from pathlib import Path
from urllib.error import URLError
from urllib.request import urlretrieve

ROBOTO_BASE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto"

DOWNLOADS = (
    {
        "name": "Roboto.ttf",
        "url": f"{ROBOTO_BASE_URL}/Roboto%5Bwdth,wght%5D.ttf",
    },
    {
        "name": "Roboto-Italic.ttf",
        "url": f"{ROBOTO_BASE_URL}/Roboto-Italic%5Bwdth,wght%5D.ttf",
    },
    {
        "name": "OFL.txt",
        "url": f"{ROBOTO_BASE_URL}/OFL.txt",
    },
)


def download_fonts():
    """Prepare self-hosted Roboto assets before building or previewing the site."""
    docs_dir = Path(__file__).resolve().parent.parent
    font_dir = docs_dir / "assets" / "downloaded" / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)

    for item in DOWNLOADS:
        target = font_dir / item["name"]
        if target.exists():
            continue

        try:
            print(f"Downloading Roboto asset: {item['name']}")
            urlretrieve(item["url"], target)
        except URLError as exc:
            raise RuntimeError(
                f"Could not download {item['name']} from {item['url']}. "
                "Check your network connection or place the file manually in "
                f"{font_dir}."
            ) from exc


if __name__ == "__main__":
    download_fonts()
