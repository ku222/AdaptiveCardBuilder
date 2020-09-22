import json
from typing import Union, List, Tuple
import aiohttp
from aiohttp import ClientResponse, ClientSession
import asyncio
import copy

class AdaptiveObject:
    '''
    Base class for all Adaptive Objects (TextBlocks, Columns, etc.)
    The following methods can be overriden for each AdaptiveObject:
        1) _is_an_action()
        2) _get_item_container()
        3) _get_action_container()
    '''
    def _is_an_action(self) -> bool:
        return False

    def _get_item_container(self) -> Union[None, List['AdaptiveObject']]:
        '''
        Override if necessary - return the item container of this Adaptive object.
        By default returns None, indicating that this object has no item container.
        '''
        return None

    def _get_action_container(self) -> Union[None, List['AdaptiveObject']]:
        '''
        Override if necessary - return the action container of this Adaptive object.
        By default returns None, indicating that this object has no action container.
        '''
        return None

    def _translatable_attributes(self) -> List[str]:
        '''Return a string list of translatable attributes for this object'''
        return []

    def _add_item(self, item: 'AdaptiveObject') -> 'AdaptiveObject':
        """Adds an AdaptiveObject to this object's item container"""
        container = self._get_item_container()
        assert type(container) == list, "Attempted to add an item to an action container. \
        Consider using up_one_level() to back out of the current element"
        container.append(item)
        return item

    def _add_action(self, action: 'AdaptiveObject') -> 'AdaptiveObject':
        """Adds an AdaptiveObject to this object's action container"""
        container = self._get_action_container()
        assert type(container) == list, "Attempted to add an action to an item container. \
        Consider using an ActionSet to add actions into"
        container.append(action)
        return action


class Container(AdaptiveObject):
    '''
    Containers group items together.
    https://adaptivecards.io/explorer/Container.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Container"
        self.items: List[AdaptiveObject] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[AdaptiveObject]:
        return self.items


class Column(AdaptiveObject):
    '''
    Defines a container that is part of a ColumnSet.
    https://adaptivecards.io/explorer/Column.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Column"
        self.items: List[AdaptiveObject] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[AdaptiveObject]:
        return self.items


class ColumnSet(AdaptiveObject):
    '''
    ColumnSet divides a region into Columns, allowing elements to sit side-by-side.
    https://adaptivecards.io/explorer/ColumnSet.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ColumnSet"
        self.columns: List[Column] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[Column]:
        return self.columns


class TextBlock(AdaptiveObject):
    '''
    Displays text, allowing control over font sizes, weight, and color.
    https://adaptivecards.io/explorer/TextBlock.html.
    '''
    def __init__(self, text: str, **kwargs):
        super().__init__()
        self.type = "TextBlock"
        self.text = text
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['text']


class Image(AdaptiveObject):
    '''
    Displays an image. Acceptable formats are PNG, JPEG, and GIF.
    https://adaptivecards.io/explorer/Image.html.
    '''
    def __init__(self, url: str, **kwargs):
        super().__init__()
        self.type = "Image"
        self.url = url
        self.__dict__.update(kwargs)


class ImageSet(AdaptiveObject):
    '''
    The ImageSet displays a collection of Images similar to a gallery.
    Acceptable formats are PNG, JPEG, and GIF.
    https://adaptivecards.io/explorer/ImageSet.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ImageSet"
        self.images: List[Image] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[Image]:
        return self.images


class ActionSet(AdaptiveObject):
    '''
    Displays a set of actions.
    https://adaptivecards.io/explorer/ActionSet.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ActionSet"
        self.actions: List[AdaptiveObject] = []
        self.__dict__.update(kwargs)

    def _get_action_container(self) -> List[AdaptiveObject]:
        return self.actions


class ActionOpenUrl(AdaptiveObject):
    '''
    When invoked, show the given url either by launching it in an
    external web browser or showing within an embedded web browser.
    https://adaptivecards.io/explorer/Action.OpenUrl.html.
    '''
    def __init__(self, url: str, **kwargs):
        super().__init__()
        self.type = "Action.OpenUrl"
        self.url = url
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['title']

    def _is_an_action(self) -> bool:
        return True


class ActionSubmit(AdaptiveObject):
    '''
    Gathers input fields, merges with optional data field, and sends an event to the client.
    It is up to the client to determine how this data is processed.
    https://adaptivecards.io/explorer/Action.Submit.html.
    For example: With BotFramework bots, the client would send an activity through the messaging
    medium to the bot. The inputs that are gathered are those on the current card, and in the case
    of a show card those on any parent cards.
    See https://docs.microsoft.com/en-us/adaptive-cards/authoring-cards/input-validation for more details.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.Submit"
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['title']

    def _is_an_action(self) -> bool:
        return True


class Fact(AdaptiveObject):
    '''
    Describes a Fact in a FactSet as a key/value pair.
    https://adaptivecards.io/explorer/Fact.html.
    '''
    def __init__(self, title, value):
        super().__init__()
        self.type = "FactSet"
        self.title = title
        self.value = value

    def _translatable_attributes(self):
        return ['title', 'value']


class FactSet(AdaptiveObject):
    '''
    The FactSet element displays a series of facts (i.e. name/value pairs) in a tabular form.
    https://adaptivecards.io/explorer/FactSet.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "FactSet"
        self.facts: List[Fact] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[Fact]:
        return self.facts


class InputText(AdaptiveObject):
    '''
    Lets a user enter text.
    https://adaptivecards.io/explorer/Input.Text.html.
    '''
    def __init__(self, ID: str, **kwargs):
        super().__init__()
        self.type = "Input.Text"
        self.id = ID
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['title', 'placeholder', 'value']


class MediaSource(AdaptiveObject):
    '''
    Defines a source for a Media element.
    https://adaptivecards.io/explorer/MediaSource.html.
    '''
    def __init__(self, mime_type: str, url: str):
        super().__init__()
        self.mimeType = mime_type
        self.url = url


class Media(AdaptiveObject):
    '''
    Displays a media player for audio or video content.
    https://adaptivecards.io/explorer/Media.html
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Media"
        self.sources: List[MediaSource] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[MediaSource]:
        return self.sources


class TextRun(AdaptiveObject):
    '''
    Defines a single run of formatted text.
    https://adaptivecards.io/explorer/TextRun.html.
    '''
    def __init__(self, text: str, **kwargs):
        super().__init__()
        self.type = "TextRun"
        self.text = text
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['text']


class RichTextBlock(AdaptiveObject):
    '''
    Defines an array of inlines, allowing for inline text formatting.
    https://adaptivecards.io/explorer/RichTextBlock.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "RichTextBlock"
        self.inlines: List[TextRun] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[TextRun]:
        return self.inlines


class TargetElement(AdaptiveObject):
    '''
    Represents an entry for Action.ToggleVisibility's targetElements property.
    https://adaptivecards.io/explorer/TargetElement.html.
    '''
    def __init__(self, element_id: str, **kwargs):
        super().__init__()
        self.elementId = element_id
        self.__dict__.update(kwargs)


class ActionToggleVisibility(AdaptiveObject):
    '''
    An action that toggles the visibility of associated card elements.
    https://adaptivecards.io/explorer/Action.ToggleVisibility.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.ToggleVisibility"
        self.targetElements: List[TargetElement] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[TargetElement]:
        return self.targetElements

    def _translatable_attributes(self) -> List[str]:
        return ['title']

    def _is_an_action(self) -> bool:
        return True


class InputNumber(AdaptiveObject):
    '''
    Allows a user to enter a number.
    https://adaptivecards.io/explorer/Input.Number.html.
    '''
    def __init__(self, ID: str, **kwargs):
        super().__init__()
        self.type = "Input.Number"
        self.id = ID
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['placeholder']


class InputDate(AdaptiveObject):
    '''
    Lets a user choose a date.
    https://adaptivecards.io/explorer/Input.Date.html.
    '''
    def __init__(self, ID: str, **kwargs):
        super().__init__()
        self.type = "Input.Date"
        self.id = ID
        self.__dict__.update(kwargs)


class InputTime(AdaptiveObject):
    '''
    Lets a user select a time.
    https://adaptivecards.io/explorer/Input.Time.html.
    '''
    def __init__(self, ID: str, **kwargs):
        super().__init__()
        self.type = "Input.Time"
        self.id = ID
        self.__dict__.update(kwargs)


class InputToggle(AdaptiveObject):
    '''
    Lets a user choose between two options.
    https://adaptivecards.io/explorer/Input.Toggle.html.
    '''
    def __init__(self, title: str, ID: str, **kwargs):
        super().__init__()
        self.type = "Input.Toggle"
        self.title = title
        self.id = ID
        self.__dict__.update(kwargs)

    def _translatable_attributes(self) -> List[str]:
        return ['title']


class InputChoice(AdaptiveObject):
    '''
    Describes a choice for use in a ChoiceSet.
    https://adaptivecards.io/explorer/Input.Choice.html.
    '''
    def __init__(self, title: str, value: str):
        super().__init__()
        self.title = title
        self.value = value

    def _translatable_attributes(self) -> List[str]:
        return ['title', 'value']


class InputChoiceSet(AdaptiveObject):
    '''
    Allows a user to input a Choice.
    https://adaptivecards.io/explorer/Input.ChoiceSet.html.
    '''
    def __init__(self, ID: str, **kwargs):
        super().__init__()
        self.type = "Input.ChoiceSet"
        self.id = ID
        self.choices: List[InputChoice] = []
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[InputChoice]:
        return self.choices


class AdaptiveCard:
    '''
    An Adaptive Card, containing a free-form body of card elements, and an optional set of actions.
    https://adaptivecards.io/explorer/AdaptiveCard.html.
    '''
    def __init__(self, schema="http://adaptivecards.io/schemas/adaptive-card.json", version="1.2", **kwargs):
        self.schema = schema
        self.version = version
        self.type = "AdaptiveCard"
        self.body: List[AdaptiveObject] = []
        self.actions: List[AdaptiveObject] = []
        self._pointer = self
        self.__dict__.update(kwargs)

    def __add__(self, card: "AdaptiveCard") -> "AdaptiveCard":
        '''
        Adds two cards together by combining the elements in their bodies.
        To preserve intra-card ordering of elements, it moves all actions
        in the outermost action container of each card into their bodies,
        by placing them in ActionSets instead.
        '''
        self_ = copy.deepcopy(self)
        card = copy.deepcopy(card)
        if self_.actions:
            # Move own actions into body
            action_set = ActionSet()
            action_set.actions.extend(self_.actions)
            self_.body.append(action_set)
            self_.actions = []
        if card.actions:
            # Move other card's actions into body
            action_set = ActionSet()
            action_set.actions.extend(card.actions)
            card.body.append(action_set)
            card.actions = []
        self_.body.extend(card.body)
        return self_

    def save_level(self) -> AdaptiveObject:
        '''
        Saves the current pointer level into a variable, allowing us
        to return back to this level in future via the load level method.

        Usage is as follows:
            card = AdaptiveCard()
            checkpoint = card.save_level()
            .......
            card.load_level(checkpoint)
        '''
        return self._pointer

    def load_level(self, level: AdaptiveObject) -> None:
        """
        Sets card's current pointer level to the given level/checkpoint.

        Usage is as follows:
            card = AdaptiveCard()
            checkpoint = card.save_level()
            .......
            card.load_level(checkpoint)
        """
        self._pointer = level

    def add(self, element: Union[str, list, AdaptiveObject], preserve_level=False):
        """
        Main method allowing AdaptiveItems to be added to the card.
        Can accept either a String, AdaptiveObject or List of either.
        In the case of a list of objects being added, it will recurse
        into the list and add each constituent element individually.

        Codeword strings can be passed - card will execute logic based
        on the exact string passed.

        If preserve_level argument is set to True, then the pointer will
        return back to the level the add function was first used at
        """
        # Preserve level if required
        if preserve_level:
            self._preserve_level = self.save_level()
        # check for list - recurse into list if true
        if isinstance(element, list):
            for e in element:
                self.add(e, preserve_level=False)
        # check for codewords in our string input
        elif isinstance(element, str):
            self.back_to_top() if "^" in element else None
            self.up_one_level() if "<" in element else None
        # else default addition of adaptive elements
        elif issubclass(type(element), AdaptiveObject):
            self._pointer._add_action(element) if element._is_an_action() else self._pointer._add_item(element)
            # Add link between this element and the current pointer item
            element._previous = self._pointer
            # check if added element has any containers of its own
            element_item_container = element._get_item_container()
            element_action_container = element._get_action_container()
            if isinstance(element_item_container, list) or isinstance(element_action_container, list):
                # Set pointer to this new element if it has its own containers
                self._pointer = element
        # Reload original level if applicable
        if preserve_level:
            self.load_level(self._preserve_level)
        return self

    def _add_item(self, item: AdaptiveObject) -> None:
        """Adds an AdaptiveObject to this card's body (item) list"""
        self.body.append(item)

    def _add_action(self, action: AdaptiveObject) -> None:
        """Adds an AdaptiveObject to this card's actions list"""
        self.actions.append(action)

    def up_one_level(self) -> None:
        """
        Use the current adaptive object's previous link to go back
        up one level in the card's item tree.
        """
        has_previous = True if getattr(self._pointer, '_previous', 'no') != 'no' else False
        if has_previous:
            self._pointer = self._pointer._previous

    def back_to_top(self) -> None:
        '''Go back to the top of the card (sets pointer to the card itself)'''
        self._pointer = self

    async def to_json(self, version="1.2", schema="http://adaptivecards.io/schemas/adaptive-card.json",
        translator_to_lang=None, translator_key=None, translator_region='global',
        translator_base_url="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
        ) -> str:
        '''
        Asynchronous method which serializes this card object into a JSON string.
        Deletes any construction-related attributes from all constituent AdaptiveItems,
        translates any attributes if required, and then returns a JSON string.

        Translation occurs if a translator_to_lang code is provided.
        See https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator?tabs=python
        for details on how the translator API works.
        '''
        self.schema = schema
        self.version = version
        # Try translate if needed first
        if translator_to_lang:
            assert translator_key, "Translation step requires an Azure Translation API key"
            await self._translate_elements(to_lang=translator_to_lang, translator_key=translator_key,
                                           region=translator_region, base_url=translator_base_url)
        # Define helper method prior to serializing
        def dictify(item: object):
            '''Helper method to delete construction-related attributes'''
            has_pointer = True if getattr(item, '_pointer', 'no') != 'no' else False
            has_previous = True if getattr(item, '_previous', 'no') != 'no' else False
            has_preserve_level = True if getattr(item, '_preserve_level', 'no') != 'no' else False
            has_dont_translate = True if getattr(item, 'dont_translate', 'no') != 'no' else False
            if has_pointer: del item._pointer
            if has_previous: del item._previous
            if has_preserve_level: del item._preserve_level
            if has_dont_translate: del item.dont_translate
            return item.__dict__
        # Return serialized card
        serialized = json.dumps(self, default=dictify, sort_keys=False)
        return serialized

    async def to_dict(self, version="1.2", schema="http://adaptivecards.io/schemas/adaptive-card.json",
        translator_to_lang=None, translator_key=None, translator_region='global',
        translator_base_url="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
        ) -> dict:
        '''
        Asynchronous method which turns this card object into a plain python dictionary representation by
        sequentially calling its own to_json() method then re-serializing back into a python dictionary.

        Translation occurs if a translator_to_lang code is provided.
        See https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator?tabs=python
        for details on how the translator API works.
        '''
        serialized = await self.to_json(version=version, schema=schema, translator_to_lang=translator_to_lang,
                                        translator_key=translator_key, translator_region=translator_region,
                                        translator_base_url=translator_base_url)
        return json.loads(serialized)

    async def _translate_elements(self, to_lang, translator_key, region='global',
                            base_url="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0") -> None:
        '''
        Utility function to translate all our card's elements for us
        First calls the _prepare_elements_for_translation method to recursively pull out items and their text attributes
        Then calls the Azure Translator 3.0 API to translate all elements
        Then swaps the current text with the corresponding translated text
        '''
        supported_languages = ['af', 'ar', 'bn', 'bs', 'bg', 'yue', 'ca', 'zh-Hans', 'zh-Hant', 'hr', 'cs', 'da', 'nl',
                                'en', 'et', 'fj', 'fil', 'fi', 'fr', 'de', 'el', 'gu', 'ht', 'he', 'hi', 'mww', 'hu', 'is',
                                'id', 'ga', 'it', 'ja', 'kn', 'kk', 'sw', 'tlh-Latn', 'tlh-Piqd', 'ko', 'lv', 'lt', 'mg', 'ms',
                                'ml', 'mt', 'mi', 'mr', 'nb', 'fa', 'pl', 'pt-br', 'pt-pt', 'pa', 'otq', 'ro', 'ru', 'sm', 'sr-Cyrl',
                                'sr-Latn', 'sk', 'sl', 'es', 'sv', 'ty', 'ta', 'te', 'th', 'to', 'tr', 'uk', 'ur', 'vi', 'cy', 'yua']
        # to_lang value must be supported
        assert to_lang in supported_languages, "Given language code not supported by Azure"
        # Pull out object attribute pairs
        object_attribute_pairs = self._prepare_elements_for_translation()

        # Make/send translation request given these object attribute pairs
        response_batches: List[List[dict]] = await self._send_translation_requests(to_lang,
                                                                                   translator_key,
                                                                                   region,
                                                                                   base_url,
                                                                                   object_attribute_pairs)
        # Unpack translations
        i = 0
        for batch in response_batches:
            for response_dict in batch: # up to 100 dicts per batch
                translations_array = response_dict.get('translations')
                first_result = translations_array[0]
                translated_text = first_result['text']
                # Update own objects
                (adaptive_object, attribute) = object_attribute_pairs[i]
                setattr(adaptive_object, attribute, translated_text)
                i += 1

    async def _send_translation_requests(self, to_lang: str, translator_key: str, region: str,
                                        base_url: str, object_attribute_pairs: list) -> List[List[dict]]:
        '''
        Asynchronously sends translation requests to our Translator API instance.
        Breaks the body of the requests into 100-length batches to respect
        max request limits. Returns a List of List of Dicts.
        '''
        # Construct request body
        body: List[dict] = []
        for (adaptive_object, attribute) in object_attribute_pairs:
            item_to_add = {"Text": getattr(adaptive_object, attribute)}
            body.append(item_to_add)
        # Chunk body into a list of lists with size 100 to respect request limits
        chunked_bodies = self._chunk_into_batches(body)

        # Define single post request method
        async def _post_request(session: ClientSession, a_body: List[dict]) -> dict:
            headers = {
                    "Ocp-Apim-Subscription-Key": translator_key,
                    "Ocp-Apim-Subscription-Region": region,
                    "Content-Type": "application/json; charset=UTF-8",
                    }
            response: ClientResponse = await session.post(url=f"{base_url}&to={to_lang}", headers=headers, json=a_body)
            return await response.json()

        async with ClientSession() as session:
            requests = []
            for body in chunked_bodies:
                requests.append(_post_request(session=session, a_body=body))
            responses = await asyncio.gather(*requests, return_exceptions=True)
            return responses

    def _prepare_elements_for_translation(self) -> List[Tuple[AdaptiveObject, str]]:
            '''
            Utility function to recursively pull out all pairs of objects and their attributes
            Called by the _translate_elements() method.
            Returns a List of (AdaptiveObject, str) Tuples, where str is one attribute of the
            AdaptiveObject that should be translated
            '''
            object_attribute_pairs = []
            # Recursive method to explore items, pull out translatable attributes
            def recursive_find(thisItem: AdaptiveObject) -> None:
                '''
                For a given AdaptiveObject, turns its attributes into a list of
                (self, attribute) tuples, then adds this to the outer list.
                If the item itself has any item or action containers, it will
                then recurse into those containers and repeat.
                '''
                nonlocal object_attribute_pairs
                # Extract (hypothetically) translatable attribs for this particular AdpativeObject
                translatable_attributes: List[str] = thisItem._translatable_attributes()
                # First double check for a dont_translate attribute
                has_dont_translate: bool = True if getattr(thisItem, 'dont_translate', 'no') != 'no' else False
                # Pull out translatable attr
                if not has_dont_translate:
                    for attribute in translatable_attributes:
                        if hasattr(thisItem, attribute):
                            object_attribute_pairs.append((thisItem, attribute))
                # Recurse into own items
                item_container = thisItem._get_item_container()
                action_container = thisItem._get_action_container()
                if item_container:
                    for item in item_container:
                        recursive_find(item)
                if action_container:
                    for action in action_container:
                        recursive_find(action)
            # Call recursive find
            self.back_to_top()
            for item in self.body:
                recursive_find(item)
            for action in self.actions:
                recursive_find(action)
            return object_attribute_pairs

    def _chunk_into_batches(self, a_list: list, n=100) -> List[list]:
        '''Chunks a list into a list of lists with size n'''
        n = max(1, n)
        return [a_list[i:i+n] for i in range(0, len(a_list), n)]


def combine_adaptive_cards(cards: List[AdaptiveCard]) -> AdaptiveCard:
    '''
    Combines a list of adaptive cards into a single adaptive card.
    Uses the first card as the base card, then adds all subsequent
    cards to this first card.
    '''
    first_card = cards[0]
    if len(cards) < 2:
        return first_card
    for card in cards[1:]:
        first_card += card
    return first_card


class ActionShowCard(AdaptiveObject):
    '''
    Defines an AdaptiveCard which is shown to the user when the button or link is clicked.
    https://adaptivecards.io/explorer/Action.ShowCard.html.
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.ShowCard"
        self.card = AdaptiveCard()
        self.__dict__.update(kwargs)

    def _get_item_container(self) -> List[AdaptiveObject]:
        return self.card.body

    def _get_action_container(self) -> List[AdaptiveObject]:
        return self.card.actions

    def _is_an_action(self) -> bool:
        return True

    def _translatable_attributes(self) -> List[str]:
        return ['title']

