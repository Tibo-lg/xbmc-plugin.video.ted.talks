
import re
# Custom xbmc thing for fast parsing. Can't rely on lxml being available as of 2012-03.
import CommonFunctions as xbmc_common
import httplib
import urlparse
import json
import re


def get(html, video_quality='320kbps'):
    """Extract talk details from talk html
       @param video_quality string in form '\d+kbps' that should match one of the provided TED bitrates.
    """
    init_scripts = [script for script in xbmc_common.parseDOM(html, 'script') if '"talkPage.init"' in script]
    if init_scripts:
        init_json = json.loads(re.compile(r'q[(]"talkPage.init",(.+)[)]').search(init_scripts[0]).group(1))
        talk_json = init_json['talks'][0]
        title = talk_json['title']
        speaker = talk_json['speaker']

        if talk_json['resources']['h264']:
            url = talk_json['resources']['h264'][0]['file']
            plot = xbmc_common.parseDOM(html, 'p', attrs={'class':'talk-description'})[0]

            if not video_quality == '320kbps':
                url_custom = url.replace("-320k.mp4", "-%sk.mp4" % (video_quality.split('k')[0]))

                # Test resource exists
                url_custom_parsed = urlparse.urlparse(url_custom)
                h = httplib.HTTPConnection(url_custom_parsed.netloc)
                h.request('HEAD', url_custom_parsed.path)
                response = h.getresponse()
                h.close()
                if response.status / 100 < 4:
                    url = url_custom
        else:
            # YouTube fallback
            youtube_code = talk_json['external']['code']
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % (youtube_code)
            plot = None  # Maybe it is there somewhere but this will do for now.

        return url, title, speaker, plot, talk_json

    else:
        # Vimeo fallback
        headline = xbmc_common.parseDOM(html, 'span', attrs={'id':'altHeadline'})[0].split(':', 1)
        # Note: maybe no ':' in title.
        title = headline[0].strip() if len(headline) == 1 else headline[1].strip()
        speaker = "Unknown" if len(headline) == 1 else headline[0].strip()
        plot = xbmc_common.parseDOM(html, 'p', attrs={'id':'tagline'})[0]

        vimeo_re = re.compile('https?://.*?vimeo.com/.*?/([^/?]+)')
        for link in xbmc_common.parseDOM(html, 'iframe', ret='src'):  # Can't get attrs regex to work properly with parseDOM :(
            match = vimeo_re.match(link)
            if match:
                url = 'plugin://plugin.video.vimeo?action=play_video&videoid=%s' % (match.group(1))
                break

        return url, title, speaker, plot, None
