import json


class AdaptiveCard:
    def __init__(self, schema="http://adaptivecards.io/schemas/adaptive-card.json", version="1.0"):
        self.schema = schema
        self.version = version
        self.type = "AdaptiveCard"
        self.body = []
        self.actions = []
        self.pointer = self.body
                
    def __repr__(self):
        return str(self.__dict__)
    
    def set_pointer(self, item):
        self.pointer = item
        
    def save_level(self):
        return self.pointer
    
    def load_level(self, level):
        self.set_pointer(level)
    
    def add(self, item, recurse=True):
        if type(self.pointer) == list:
            self.pointer.append(item)
        else:
            self.pointer.add(item)
        item.previous = self.pointer
        if recurse:
            if type(item.get_container()) == list:
                self.set_pointer(item)
        return item
    
    def up_one_level(self):
        has_previous = True if getattr(self.pointer, 'previous', 'no') != 'no' else False
        if has_previous:
            self.set_pointer(self.pointer.previous)
 
    def back_to_top(self):
        self.set_pointer(self.body)
    
    def to_json(
        self,
        version="1.0",
        schema="http://adaptivecards.io/schemas/adaptive-card.json",
        for_print=False
        ):
        def dictify(card):
            has_pointer = True if getattr(card, 'pointer', 'no') != 'no' else False
            has_previous = True if getattr(card, 'previous', 'no') != 'no' else False
            if has_pointer:
                del card.pointer
            if has_previous:
                del card.previous
            return card.__dict__
        
        self.schema = schema
        self.version = version
        serialized = json.dumps(self, default=dictify, sort_keys=False)
        return serialized if not for_print else json.loads(serialized)
    
    

class AdaptiveItem:
    def get_container(self):
        return None
    def add(self, item):
        container = self.get_container()
        assert type(container) == list
        container.append(item)
        return item
    def print_self(self):
        return self.__dict__
    
    
class Container(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Container"
        self.items = []
        self.__dict__.update(kwargs)
    def get_container(self):
        return self.items


class ColumnSet(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "ColumnSet"
        self.columns = []
        self.__dict__.update(kwargs)
    def get_container(self):
        return self.columns
    

class Column(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "Column"
        self.items = []
        self.__dict__.update(kwargs)
    def get_container(self):
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
    def get_container(self):
        return self.images
    def add(self, item):
        assert type(item) == Image
        container = self.get_container()
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
    def get_container(self):
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
    def get_container(self):
        return self.card.body
    
    
class FactSet(AdaptiveItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.type = "FactSet"
        self.facts = []
        self.__dict__.update(kwargs)
    def get_container(self):
        return self.facts


class Fact(AdaptiveItem):
    def __init__(self, title, value):
        super().__init__()
        self.type = "FactSet"
        self.title = title
        self.value = value