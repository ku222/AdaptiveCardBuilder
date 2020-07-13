
import json
import requests

class AdaptiveCard:
    # An Adaptive Card, containing a free-form body of card elements, and an optional set of actions.
    def __init__(self, schema="http://adaptivecards.io/schemas/adaptive-card.json", version="1.2", **kwargs):
        self.schema = schema
        self.version = version
        self.type = "AdaptiveCard"
        self.body = []
        self.actions = []
        self.pointer = self
        self.is_action = False
        self.__dict__.update(kwargs)
    
    def set_pointer(self, item):
        self.pointer = item
        
    def save_level(self):
        return self.pointer
    
    def load_level(self, level):
        self.set_pointer(level)
    
    def add(self, element, is_action=None):
        # If none, default to self's action setting
        if is_action == None:
            is_action = self.is_action
        # check for list - recurse into list if true
        if type(element) == list:
            for e in element:
                self.add(e)
        # check for codewords in our string input
        elif type(element) == str:
            back_to_top = "^" in element
            up_one_level = "<" in element
            item = "item" in element.lower()
            action = "action" in element.lower()
            if back_to_top:
                self.back_to_top()
            elif up_one_level:
                self.up_one_level()
            elif item:
                self.is_action = False
            elif action:
                self.is_action = True
        # else default addition of adaptive elements
        elif issubclass(type(element), AdaptiveItem):
            self.pointer.add_action(element) if is_action else self.pointer.add_item(element)
            element.previous = self.pointer
            # check if added element has any containers of its own
            element_item_container = element.get_item_container()
            element_action_container = element.get_action_container()
            if type(element_item_container) == list or type(element_action_container) == list:
                self.set_pointer(element)
            return element
    
    def add_item(self, item):
        self.body.append(item)
        
    def add_action(self, action):
        self.actions.append(action)
    
    def up_one_level(self):
        has_previous = True if getattr(self.pointer, 'previous', 'no') != 'no' else False
        if has_previous:
            self.set_pointer(self.pointer.previous)
 
    def back_to_top(self):
        self.set_pointer(self)
    
    def to_json(
        self,
        version="1.2",
        schema="http://adaptivecards.io/schemas/adaptive-card.json",
        translator_to_lang=None,
        translator_key=None,
        translator_region='global',
        translator_base_url="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
        ):
        def dictify(card):
            has_pointer = True if getattr(card, 'pointer', 'no') != 'no' else False
            has_previous = True if getattr(card, 'previous', 'no') != 'no' else False
            has_is_action = True if getattr(card, 'is_action', 'no') != 'no' else False
            has_dont_translate = True if getattr(card, 'dont_translate', 'no') != 'no' else False
            if has_pointer:
                del card.pointer
            if has_previous:
                del card.previous
            if has_is_action:
                del card.is_action
            if has_dont_translate:
                del card.dont_translate
            return card.__dict__
        
        self.schema = schema
        self.version = version
        # Try translate if needed first
        if translator_to_lang:
            assert translator_key
            self._translate_elements(
                to_lang=translator_to_lang,
                translator_key=translator_key,
                region=translator_region,
                base_url=translator_base_url
            )
        
        # Return serialized card
        serialized = json.dumps(self, default=dictify, sort_keys=False)
        return serialized
        
    def _prepare_elements_for_translation(self):
        '''
        Utility function to recursively pull out all pairs of objects and their attributes
        Called by the _translate_elements() method
        '''
        object_attribute_pairs = []
        # Recursive method to explore items, pull out translatable attributes
        def recursive_find(adaptive_object):
            nonlocal object_attribute_pairs
            translatable_attributes = adaptive_object.translatable_attributes()
            # First double check for a dont_translate attribute
            has_dont_translate = True if getattr(adaptive_object, 'dont_translate', 'no') != 'no' else False
            # Pull out translatable attr
            if not has_dont_translate:
                if translatable_attributes:
                    for attribute in translatable_attributes:
                        if hasattr(adaptive_object, attribute):
                            object_attribute_pairs.append((adaptive_object, attribute))
            # Recurse into own items
            item_container = adaptive_object.get_item_container()
            action_container = adaptive_object.get_action_container()
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
    
    def _translate_elements(self, to_lang, translator_key, region='global', base_url="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"):
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
        assert to_lang in supported_languages
        # Pull out object attribute pairs
        object_attribute_pairs = self._prepare_elements_for_translation()
        # The array can have at most 100 elements.
        assert len(object_attribute_pairs) <= 100
        
        # Prep HTTP request
        headers = {
            "Ocp-Apim-Subscription-Key": translator_key,
            "Ocp-Apim-Subscription-Region": region,
            "Content-Type": "application/json; charset=UTF-8",
            "Content-Length": str(len(object_attribute_pairs)),
            }
        
        # Construct body
        body = []
        for (adaptive_object, attribute) in object_attribute_pairs:
            item_to_add = {"Text": getattr(adaptive_object, attribute)}
            body.append(item_to_add)
        
        # Post request, return
        response = requests.post(url=f"{base_url}&to={to_lang}", headers=headers, json=body)
        assert response.status_code == 200
        
        # Unpack translations
        for (i, response_dict) in enumerate(response.json()):
            translations_array = response_dict['translations']
            first_result = translations_array[0]
            translated_text = first_result['text']
            # Update own objects
            (adaptive_object, attribute) = object_attribute_pairs[i]
            setattr(adaptive_object, attribute, translated_text)
    

class AdaptiveItem:
    def get_item_container(self):
        return None
    def get_action_container(self):
        return None
    def translatable_attributes(self):
        return []
    def add_item(self, item):
        container = self.get_item_container()
        assert type(container) == list
        container.append(item)
        return item
    def add_action(self, action):
        container = self.get_action_container()
        assert type(container) == list
        container.append(action)
        return action
    def __str__(self):
        def dictify(item):
            has_pointer = True if getattr(item, 'pointer', 'no') != 'no' else False
            has_previous = True if getattr(item, 'previous', 'no') != 'no' else False
            if has_pointer:
                del item.pointer
            if has_previous:
                del item.previous
            return item.__dict__
        serialized = json.dumps(self, default=dictify, sort_keys=False, indent=4)
        return serialized
    
    
class Container(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Container"
        self.items = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.items


class ColumnSet(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ColumnSet"
        self.columns = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.columns
    

class Column(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Column"
        self.items = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.items
    
    
class TextBlock(AdaptiveItem):
    def __init__(self, text, **kwargs):
        super().__init__()
        self.type = "TextBlock"
        self.text = text
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['text']
        

class ImageSet(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ImageSet"
        self.images = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.images
    def add(self, item):
        assert type(item) == Image
        container = self.get_item_container()
        container.append(item)
        return item
    
    
class Image(AdaptiveItem):
    def __init__(self, url, **kwargs):
        super().__init__()
        self.type = "Image"
        self.url = url
        self.__dict__.update(kwargs)


class ActionSet(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ActionSet"
        self.actions = []
        self.__dict__.update(kwargs)
    def get_action_container(self):
        return self.actions
    
    
class ActionOpenUrl(AdaptiveItem):
    def __init__(self, url, **kwargs):
        super().__init__()
        self.type = "Action.OpenUrl"
        self.url = url
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['title']
        
        
class ActionSubmit(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.Submit"
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['title']

        
class ActionShowCard(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.ShowCard"
        self.card = AdaptiveCard()
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.card.body
    def get_action_container(self):
        return self.card.actions
    def translatable_attributes(self):
        return ['title']
    
    
class FactSet(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "FactSet"
        self.facts = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.facts


class Fact(AdaptiveItem):
    def __init__(self, title, value):
        super().__init__()
        self.type = "FactSet"
        self.title = title
        self.value = value
    def translatable_attributes(self):
        return ['title', 'value']
      

class InputText(AdaptiveItem):
    def __init__(self, ID, **kwargs):
        super().__init__()
        self.type = "Input.Text"
        self.id = ID
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['title', 'placeholder', 'value']


class Media(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Media"
        self.sources = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.sources
    
    
class MediaSource(AdaptiveItem):
    def __init__(self, mime_type, url):
        super().__init__()
        self.mimeType = mime_type
        self.url = url
        
        
class RichTextBlock(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "RichTextBlock"
        self.inlines = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.inlines
    
    
class TextRun(AdaptiveItem):
    def __init__(self, text, **kwargs):
        super().__init__()
        self.type = "TextRun"
        self.text = text
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['text']
        
        
class ActionToggleVisibility(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.ToggleVisibility"
        self.targetElements = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.targetElements
    def translatable_attributes(self):
        return ['title']


class TargetElement(AdaptiveItem):
    def __init__(self, element_id, **kwargs):
        super().__init__()
        self.elementId = element_id
        self.__dict__.update(kwargs)
        
        
class InputNumber(AdaptiveItem):
    def __init__(self, ID, **kwargs):
        super().__init__()
        self.type = "Input.Number"
        self.id = ID
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['placeholder']
        

class InputDate(AdaptiveItem):
    def __init__(self, ID, **kwargs):
        super().__init__()
        self.type = "Input.Date"
        self.id = ID
        self.__dict__.update(kwargs)


class InputTime(AdaptiveItem):
    def __init__(self, ID, **kwargs):
        super().__init__()
        self.type = "Input.Time"
        self.id = ID
        self.__dict__.update(kwargs)
        
        
class InputToggle(AdaptiveItem):
    def __init__(self, title, ID, **kwargs):
        super().__init__()
        self.type = "Input.Toggle"
        self.title = title
        self.id = ID
        self.__dict__.update(kwargs)
    def translatable_attributes(self):
        return ['title']
        

class InputChoiceSet(AdaptiveItem):
    def __init__(self, ID, **kwargs):
        super().__init__()
        self.type = "Input.ChoiceSet"
        self.id = ID
        self.choices = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.choices


class InputChoice(AdaptiveItem):
    def __init__(self, title, value):
        super().__init__()
        self.title = title
        self.value = value
    def translatable_attributes(self):
        return ['title', 'value']
        