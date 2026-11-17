import argparse
import sys
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(
        description="Замер скорости скачивания: 10 последовательных запросов."
    )
    parser.add_argument("url", help="Прямая HTTP(S)-ссылка на файл")
    args = parser.parse_args()
    address = urlsplit(args.url)
    if address.scheme not in ("http", "https") or not address.netloc:
        parser.error("Укажите полный URL с http:// или https://")

    request = Request(args.url, headers={"User-Agent": "InternetSpeedPractice/0.1"})
    total_bytes = 0
    total_time = 0.0

    try:
        for i in range(10):
            downloaded_bytes = 0
            start = perf_counter()
            with urlopen(request, timeout=30) as response:
                while True:
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    downloaded_bytes += len(chunk)
            elapsed = perf_counter() - start
            total_bytes += downloaded_bytes
            total_time += elapsed
            print(f"Запрос {i + 1}/10: {downloaded_bytes} байт за {elapsed:.3f} с")
    except HTTPError as error:
        print(f"Ошибка HTTP {error.code}: {error.reason}", file=sys.stderr)
        retry_after = error.headers.get("Retry-After")
        if retry_after:
            print(f"Retry-After: {retry_after}", file=sys.stderr)
        return 1
    except (URLError, OSError, ValueError) as error:
        print(f"Не удалось скачать данные: {error}", file=sys.stderr)
        return 1

    average_time = total_time / 10
    speed = total_bytes / total_time / (1024 ** 2)
    print(f"\nСреднее время запроса: {average_time:.3f} с")
    print(f"Всего скачано: {total_bytes} байт")
    print(f"Скорость скачивания: {speed:.3f} МиБ/с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
