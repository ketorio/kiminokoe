# test_jamendo.py
from text import search_zaycev_songs

# Проверяем разные запросы
for query in ["Queen", "Баста", "Imagine Dragons", "Макс Корж"]:
    print(f"\n🔍 Ищем: {query}")
    tracks = search_zaycev_songs(query)
    for track in tracks[:3]:  # Показываем первые 3
        print(f"   🎵 {track['artist']} - {track['title']}")
        print(f"      Ссылка: {track['url'][:80]}...")