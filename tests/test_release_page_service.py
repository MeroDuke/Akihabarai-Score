from app.services.release_page_service import open_release_page


def test_open_release_page_opens_url():
    opened_urls = []

    open_release_page(
        "https://github.com/MeroDuke/Akihabarai-Score/releases",
        lambda url: opened_urls.append(url.toString()),
    )

    assert opened_urls == [
        "https://github.com/MeroDuke/Akihabarai-Score/releases",
    ]
