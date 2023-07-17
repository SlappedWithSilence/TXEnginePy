from game.cache import from_cache, get_cache, get_loader, cache_element


def test_get_cache():
    assert type(get_cache()) == dict


def test_from_cache():
    cache = get_cache()
    cache["element"] = 1

    assert from_cache("element") == 1

    cache["root"] = {"branch": "leaf"}

    assert from_cache("root.branch") == "leaf"


def test_cache_element():
    pass
