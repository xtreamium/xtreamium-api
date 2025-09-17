from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

import lxml.etree as ET


@dataclass
class Channel:
    """Represents a TV channel."""
    id: str
    display_names: List[Dict[str, str]] = field(default_factory=list)
    icons: List[Dict[str, str]] = field(default_factory=list)
    urls: List[Dict[str, str]] = field(default_factory=list)
    programmes: List['Programme'] = field(default_factory=list)


@dataclass
class Programme:
    """Represents a TV programme."""
    start: str
    channel: str
    stop: Optional[str] = None
    pdc_start: Optional[str] = None
    vps_start: Optional[str] = None
    showview: Optional[str] = None
    videoplus: Optional[str] = None
    clumpidx: str = "0/1"

    # Programme content
    titles: List[Dict[str, str]] = field(default_factory=list)
    sub_titles: List[Dict[str, str]] = field(default_factory=list)
    descriptions: List[Dict[str, str]] = field(default_factory=list)
    credits: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    date: Optional[str] = None
    categories: List[Dict[str, str]] = field(default_factory=list)
    keywords: List[Dict[str, str]] = field(default_factory=list)
    language: Optional[Dict[str, str]] = None
    orig_language: Optional[Dict[str, str]] = None
    length: Optional[Dict[str, str]] = None
    icons: List[Dict[str, str]] = field(default_factory=list)
    urls: List[Dict[str, str]] = field(default_factory=list)
    countries: List[Dict[str, str]] = field(default_factory=list)
    episode_nums: List[Dict[str, str]] = field(default_factory=list)
    video: Optional[Dict[str, str]] = None
    audio: Optional[Dict[str, str]] = None
    previously_shown: Optional[Dict[str, str]] = None
    premiere: Optional[Dict[str, str]] = None
    last_chance: Optional[Dict[str, str]] = None
    new: bool = False
    subtitles: List[Dict[str, Any]] = field(default_factory=list)
    ratings: List[Dict[str, Any]] = field(default_factory=list)
    star_ratings: List[Dict[str, Any]] = field(default_factory=list)
    reviews: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)


class XMLTVParser:
    """High-performance XMLTV parser using lxml."""

    def __init__(self):
        self.channels: Dict[str, Channel] = {}

    def parse_file(self, file_path: str) -> List[Channel]:
        """Parse XMLTV file and return list of channels with programmes."""
        try:
            # Use iterparse for memory-efficient parsing of large files
            context = ET.iterparse(file_path, events=('start', 'end'))
            context = iter(context)
            event, root = next(context)

            for event, elem in context:
                if event == 'end':
                    if elem.tag == 'channel':
                        self._parse_channel(elem)
                        # Clear the element to free memory AFTER parsing
                        elem.clear()
                        # Also eliminate now-empty references from the root node
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]
                    elif elem.tag == 'programme':
                        self._parse_programme(elem)
                        # Clear the element to free memory AFTER parsing
                        elem.clear()
                        # Also eliminate now-empty references from the root node
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]

            return list(self.channels.values())

        except ET.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise RuntimeError(f"Error parsing XMLTV file: {e}")

    def parse_string(self, xml_content: str) -> List[Channel]:
        """Parse XMLTV from string content."""
        try:
            root = ET.fromstring(xml_content.encode('utf-8'))

            # Parse channels first
            for channel_elem in root.xpath('//channel'):
                self._parse_channel(channel_elem)

            # Parse programmes
            for programme_elem in root.xpath('//programme'):
                self._parse_programme(programme_elem)

            return list(self.channels.values())

        except ET.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise RuntimeError(f"Error parsing XMLTV content: {e}")

    def _parse_channel(self, elem: ET.Element) -> None:
        """Parse a channel element."""
        channel_id = elem.get('id')
        if not channel_id:
            return

        channel = Channel(id=channel_id)

        # Parse display names
        for display_name in elem.xpath('./display-name'):
            channel.display_names.append({
                'text': display_name.text or '',
                'lang': display_name.get('lang', '')
            })

        # Parse icons
        for icon in elem.xpath('./icon'):
            channel.icons.append({
                'src': icon.get('src', ''),
                'width': icon.get('width', ''),
                'height': icon.get('height', '')
            })

        # Parse URLs
        for url in elem.xpath('./url'):
            channel.urls.append({
                'url': url.text or '',
                'system': url.get('system', '')
            })

        self.channels[channel_id] = channel

    def _parse_programme(self, elem: ET.Element) -> None:
        """Parse a programme element."""
        channel_id = elem.get('channel')
        start = elem.get('start')

        if not channel_id or not start:
            return

        # Ensure channel exists
        if channel_id not in self.channels:
            self.channels[channel_id] = Channel(id=channel_id)

        programme = Programme(
            start=start,
            channel=channel_id,
            stop=elem.get('stop'),
            pdc_start=elem.get('pdc-start'),
            vps_start=elem.get('vps-start'),
            showview=elem.get('showview'),
            videoplus=elem.get('videoplus'),
            clumpidx=elem.get('clumpidx', '0/1')
        )

        # Parse titles
        for title in elem.xpath('./title'):
            programme.titles.append({
                'text': title.text or '',
                'lang': title.get('lang', '')
            })

        # Parse sub-titles
        for sub_title in elem.xpath('./sub-title'):
            programme.sub_titles.append({
                'text': sub_title.text or '',
                'lang': sub_title.get('lang', '')
            })

        # Parse descriptions
        for desc in elem.xpath('./desc'):
            programme.descriptions.append({
                'text': desc.text or '',
                'lang': desc.get('lang', '')
            })

        # Parse credits
        credits_elem = elem.find('./credits')
        if credits_elem is not None:
            programme.credits = self._parse_credits(credits_elem)

        # Parse date
        date_elem = elem.find('./date')
        if date_elem is not None:
            programme.date = date_elem.text

        # Parse categories
        for category in elem.xpath('./category'):
            programme.categories.append({
                'text': category.text or '',
                'lang': category.get('lang', '')
            })

        # Parse keywords
        for keyword in elem.xpath('./keyword'):
            programme.keywords.append({
                'text': keyword.text or '',
                'lang': keyword.get('lang', '')
            })

        # Parse language
        language_elem = elem.find('./language')
        if language_elem is not None:
            programme.language = {
                'text': language_elem.text or '',
                'lang': language_elem.get('lang', '')
            }

        # Parse original language
        orig_language_elem = elem.find('./orig-language')
        if orig_language_elem is not None:
            programme.orig_language = {
                'text': orig_language_elem.text or '',
                'lang': orig_language_elem.get('lang', '')
            }

        # Parse length
        length_elem = elem.find('./length')
        if length_elem is not None:
            programme.length = {
                'text': length_elem.text or '',
                'units': length_elem.get('units', '')
            }

        # Parse icons
        for icon in elem.xpath('./icon'):
            programme.icons.append({
                'src': icon.get('src', ''),
                'width': icon.get('width', ''),
                'height': icon.get('height', '')
            })

        # Parse URLs
        for url in elem.xpath('./url'):
            programme.urls.append({
                'url': url.text or '',
                'system': url.get('system', '')
            })

        # Parse countries
        for country in elem.xpath('./country'):
            programme.countries.append({
                'text': country.text or '',
                'lang': country.get('lang', '')
            })

        # Parse episode numbers
        for episode_num in elem.xpath('./episode-num'):
            programme.episode_nums.append({
                'text': episode_num.text or '',
                'system': episode_num.get('system', 'onscreen')
            })

        # Parse video info
        video_elem = elem.find('./video')
        if video_elem is not None:
            programme.video = self._parse_video_audio(video_elem)

        # Parse audio info
        audio_elem = elem.find('./audio')
        if audio_elem is not None:
            programme.audio = self._parse_video_audio(audio_elem)

        # Parse previously shown
        prev_shown = elem.find('./previously-shown')
        if prev_shown is not None:
            programme.previously_shown = {
                'start': prev_shown.get('start', ''),
                'channel': prev_shown.get('channel', '')
            }

        # Parse premiere
        premiere_elem = elem.find('./premiere')
        if premiere_elem is not None:
            programme.premiere = {
                'text': premiere_elem.text or '',
                'lang': premiere_elem.get('lang', '')
            }

        # Parse last chance
        last_chance_elem = elem.find('./last-chance')
        if last_chance_elem is not None:
            programme.last_chance = {
                'text': last_chance_elem.text or '',
                'lang': last_chance_elem.get('lang', '')
            }

        # Check for new flag
        programme.new = elem.find('./new') is not None

        # Parse subtitles
        for subtitle in elem.xpath('./subtitles'):
            subtitle_data = {'type': subtitle.get('type', '')}
            lang_elem = subtitle.find('./language')
            if lang_elem is not None:
                subtitle_data['language'] = {
                    'text': lang_elem.text or '',
                    'lang': lang_elem.get('lang', '')
                }
            programme.subtitles.append(subtitle_data)

        # Parse ratings
        for rating in elem.xpath('./rating'):
            rating_data = {
                'system': rating.get('system', ''),
                'value': '',
                'icons': []
            }
            value_elem = rating.find('./value')
            if value_elem is not None:
                rating_data['value'] = value_elem.text or ''

            for icon in rating.xpath('./icon'):
                rating_data['icons'].append({
                    'src': icon.get('src', ''),
                    'width': icon.get('width', ''),
                    'height': icon.get('height', '')
                })
            programme.ratings.append(rating_data)

        # Parse star ratings
        for star_rating in elem.xpath('./star-rating'):
            star_rating_data = {
                'system': star_rating.get('system', ''),
                'value': '',
                'icons': []
            }
            value_elem = star_rating.find('./value')
            if value_elem is not None:
                star_rating_data['value'] = value_elem.text or ''

            for icon in star_rating.xpath('./icon'):
                star_rating_data['icons'].append({
                    'src': icon.get('src', ''),
                    'width': icon.get('width', ''),
                    'height': icon.get('height', '')
                })
            programme.star_ratings.append(star_rating_data)

        # Parse reviews
        for review in elem.xpath('./review'):
            programme.reviews.append({
                'text': review.text or '',
                'type': review.get('type', ''),
                'source': review.get('source', ''),
                'reviewer': review.get('reviewer', ''),
                'lang': review.get('lang', '')
            })

        # Parse images
        for image in elem.xpath('./image'):
            programme.images.append({
                'url': image.text or '',
                'type': image.get('type', ''),
                'size': image.get('size', ''),
                'orient': image.get('orient', ''),
                'system': image.get('system', '')
            })

        self.channels[channel_id].programmes.append(programme)

    def _parse_credits(self, credits_elem: ET.Element) -> Dict[str, List[Dict[str, Any]]]:
        """Parse credits element."""
        credits = {}

        credit_types = ['director', 'actor', 'writer', 'adapter', 'producer',
                        'composer', 'editor', 'presenter', 'commentator', 'guest']

        for credit_type in credit_types:
            credits[credit_type] = []
            for elem in credits_elem.xpath(f'./{credit_type}'):
                credit_data = {
                    'name': elem.text or '',
                    'images': [],
                    'urls': []
                }

                # Special handling for actors
                if credit_type == 'actor':
                    credit_data['role'] = elem.get('role', '')
                    credit_data['guest'] = elem.get('guest', 'no') == 'yes'

                # Parse images and URLs within credits
                for image in elem.xpath('./image'):
                    credit_data['images'].append({
                        'url': image.text or '',
                        'type': image.get('type', ''),
                        'size': image.get('size', ''),
                        'orient': image.get('orient', ''),
                        'system': image.get('system', '')
                    })

                for url in elem.xpath('./url'):
                    credit_data['urls'].append({
                        'url': url.text or '',
                        'system': url.get('system', '')
                    })

                credits[credit_type].append(credit_data)

        return credits

    def _parse_video_audio(self, elem: ET.Element) -> Dict[str, str]:
        """Parse video or audio element."""
        result = {}

        for child in elem:
            result[child.tag] = child.text or ''

        return result


def parse_xmltv_file(file_path: str) -> List[Channel]:
    """Parse XMLTV file and return channels with programmes."""
    parser = XMLTVParser()
    return parser.parse_file(file_path)


def parse_xmltv_string(xml_content: str) -> List[Channel]:
    """Parse XMLTV from string content."""
    parser = XMLTVParser()
    return parser.parse_string(xml_content)
