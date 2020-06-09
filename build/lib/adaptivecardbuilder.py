import json


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
        for_print=False
        ):
        def dictify(card):
            has_pointer = True if getattr(card, 'pointer', 'no') != 'no' else False
            has_previous = True if getattr(card, 'previous', 'no') != 'no' else False
            has_is_action = True if getattr(card, 'is_action', 'no') != 'no' else False
            if has_pointer:
                del card.pointer
            if has_previous:
                del card.previous
            if has_is_action:
                del card.is_action
            return card.__dict__
        
        self.schema = schema
        self.version = version
        if for_print:
            serialized = json.dumps(self, default=dictify, sort_keys=False, indent=4)
            print(serialized)
        else:
            serialized = json.dumps(self, default=dictify, sort_keys=False)
            return serialized
    

class AdaptiveItem:
    def get_item_container(self):
        return None
    def get_action_container(self):
        return None
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
        
        
class ActionSubmit(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.Submit"
        self.__dict__.update(kwargs)

        
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
      

class InputText(AdaptiveItem):
    def __init__(self, ID, **kwargs):
        super().__init__()
        self.type = "Input.Text"
        self.id = ID
        self.__dict__.update(kwargs)


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
        
        
class ActionToggleVisibility(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Action.ToggleVisibility"
        self.targetElements = []
        self.__dict__.update(kwargs)
    def get_item_container(self):
        return self.targetElements


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
        