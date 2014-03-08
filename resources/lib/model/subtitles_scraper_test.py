import unittest
import subtitles_scraper
import urllib
import tempfile
import talk_scraper


class TestSubtitlesScraper(unittest.TestCase):

    def test_format_time(self):
        self.assertEqual('00:00:00,000', subtitles_scraper.format_time(0))
        self.assertEqual('03:25:45,678', subtitles_scraper.format_time(12345678))

    def test_format_subtitles(self):
        subtitles = [{'content': 'Hello', 'start': 500, 'duration': 2500}, {'content': 'World', 'start': 3000, 'duration': 2500}]
        formatted_subs = subtitles_scraper.format_subtitles(subtitles, 666)
        self.assertEquals('''1
00:00:01,166 --> 00:00:03,666
Hello

2
00:00:03,666 --> 00:00:06,166
World

''', formatted_subs)

    def test_get_subtitles_bad_language(self):
        subs = subtitles_scraper.get_subtitles('1253', 'panda')
        # It returns the English subtitles :(
        self.assertEqual('You all know the truth of what I\'m going to say.', subs[0]['content'])

    def test_get_languages(self):
        talk_json = self.__get_talk_json__('http://www.ted.com/talks/richard_wilkinson.html')
        expected = set(['sq', 'ar', 'hy', 'bg', 'ca', 'zh-cn', 'zh-tw', 'hr', 'cs', 'da', 'nl', 'en', 'fr', 'ka', 'de', 'el', 'he', 'hu', 'id', 'it', 'ja', 'ko', 'fa', 'mk', 'pl', 'pt', 'pt-br', 'ro', 'ru', 'sr', 'sk', 'es', 'th', 'tr', 'uk', 'vi', 'eu', 'sv', 'nb'])
        self.assertEqual(expected, set(subtitles_scraper.__get_languages__(talk_json)), msg="New translations are likely to appear; please update the test if so :)")

    def test_get_subtitles_for_talk(self):
        talk_json = self.__get_talk_json__('http://www.ted.com/talks/richard_wilkinson.html')

        subs = subtitles_scraper.get_subtitles_for_talk(talk_json, ['banana', 'fr', 'en'], None)
        self.assertTrue(subs.startswith('''1
00:00:11,820 --> 00:00:14,820
Vous savez tous que ce que je vais dire est vrai.

2'''))

    def __get_talk_json__(self, url):
        html = urllib.urlopen(url).read()
        foo, fi, fo, fum, talk_json = talk_scraper.get(html)
        return talk_json
