import datetime
import os
import re

import discogs_client
import lyricsgenius
import requests
from django.conf import settings

from demo.models import (
    CompositionAudd,
    CompositionDiscogs,
    CompositionGenius,
    SearchName
)


def get_artist_and_track(file_path):
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    filename_without_ext = filename_without_ext.replace("_", " ")
    match = re.match(r"(\d+)\. ", filename_without_ext)
    if match:
        track_number = match.group(1)
        filename_without_ext = re.sub(rf"{track_number}\. ", "",
                                      filename_without_ext)
    filename_without_ext = re.sub(r"\([^)]*\)", "", filename_without_ext)

    parts = filename_without_ext.split(" - ")
    if len(parts) == 2:
        artist = parts[0]
        track = parts[1]
    elif len(parts) == 1:
        artist = ''
        track = filename_without_ext
    else:
        artist = parts[0]
        track = " ".join(parts[1:])
    return artist, track


def search_discogs(track='', artist=''):
    # search_string = 'Queen - The Show Must Go On'
    if artist and track:
        search_string = f"{artist} - {track}"
    elif artist:
        search_string = artist
    elif track:
        search_string = track
    else:
        raise ValueError('Укажите название трека или артиста.')
    d = discogs_client.Client(user_agent='marketradiodemo/0.1',
                              user_token=settings.DISCOGS_TOKEN)

    try:
        results = d.search(search_string, type='release')
        result = results[0]
        print(result.data)

        discogs = CompositionDiscogs(
            release=result.id,
            title=result.title,
            genre=result.genres,
            style=result.styles,
        )
        try:
            release_date = datetime.datetime.strptime(
                result.data.get('released'), "%Y-%m-%d"
            ).date()
            discogs.release_date = release_date
        except (TypeError, ValueError):
            pass
        try:
            artist = result.artists[0].name
            discogs.artist = artist
        except IndexError:
            pass
        discogs.save()
        return discogs
    except IndexError:
        print("Error discogs: Упс. Кажется пусто.")
    except discogs_client.exceptions.HTTPError:
        print("Error discogs:  401: You must authenticate to access this resource.")
    return None


def search_genius(track: str, artist=''):
    try:
        genius = lyricsgenius.Genius(settings.GENIUS_CLIENT_ACCESS_TOKEN)
    except TypeError:
        print("Error genius: Invalid token")
        return None
    result = genius.search_song(track, artist)
    if result:
        genius = CompositionGenius(
            release=result.id,
            title=result.title,
            artist=result.artist,
        )
        try:
            release_date = result._body.get("release_date_components")
            genius.release_date = datetime.date(**release_date)
        except TypeError:
            pass
        genius.save()
        return genius
    return None


def search_audd(obj: SearchName):
    def _save_audd_model(response_json):
        print(response_json)
        result = response_json.get("result")
        release_date = datetime.datetime.strptime(
            result.get("release_date"), "%Y-%m-%d"
        ).date()
        audd_model = CompositionAudd(
            title=result.get("title"),
            artist=result.get("artist"),
            release_date=release_date,
        )
        audd_model.save()
        return audd_model

    def _post_request(url, headers, data, files=None):
        response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code != 200:
            print(f"Error audd: {response.text}")
            return None
        return response.json()

    url = "https://api.audd.io/"
    data = {"api_token": settings.AUDD_TOKEN}

    # try:
    #     files = {"file": open(obj.file.path, "rb")}
    # except ValueError:
    #     print("Error audd: Нет файла")
    #     return False

    # headers = {"Content-Type": "multipart/form-data"}
    # response_json = _post_request(url, headers, data, files)
    # if response_json is None:
    #     print("Error audd: Не удалось отправить файл")
    #     return False
    #
    # if response_json.get("status") == "success":
    #     audd_model = _save_audd_model(response_json)
    #     obj.audd = audd_model
    #     obj.save()
    #     return True
    # print(f"Error audd: {response_json}")
    if not settings.NGROK_DOMAIN:
        print("Error audd: Установите валидный домен ngrok")
        return False
    data['url'] = obj.get_file_url()
    print(f"Пробуем отправить ссылку на файл: {data['url']}")
    response_json = _post_request(url, {}, data)
    if response_json is None:
        return False

    if response_json.get("status") == "success":
        audd_model = _save_audd_model(response_json)
        obj.audd = audd_model
        obj.save()
        return True

    print(f"Error audd: {response_json}")
    return False


def start_search(obj: SearchName):
    if search_audd(obj):
        artist = obj.audd.artist
        track = obj.audd.title
    else:
        if obj.file_name:
            file_name = obj.file_name
        else:
            file_name = obj.file.path
        artist, track = get_artist_and_track(file_name)

    print(f"artist: {artist}")
    print(f"track: {track}")

    discogs = search_discogs(track, artist)
    genius = search_genius(track, artist)
    obj.discogs = discogs
    obj.genius = genius
    obj.save()
