def calc_simpson_coefficient(x, y):
    x_size, y_size = len(x), len(y)
    intersection = x & y
    intersection_size = len(intersection)
    denominator = min(x_size, y_size)
    if denominator == 0:
        return 0
    return intersection_size / denominator

def calc_similarity(tweets_set, lyrics_list):
    similarity = [0] * len(lyrics_list)
    if len(tweets_set) == 0:
        return similarity
    for i, lyrics in enumerate(lyrics_list):
        terms_in_lyrics = set(lyrics.split())
        similarity[i] = calc_simpson_coefficient(terms_in_lyrics, tweets_set)
    return similarity

def get_most_similar_song(api, tweets_set, songs_data):
    lyrics_list = [song.lyrics for song in songs_data]
    similarity = calc_similarity(tweets_set, lyrics_list)
    max_index = similarity.index(max(similarity))
    return max_index
