

#%%


import json


class AdaptiveCard:
    def __init__(self, schema="http://adaptivecards.io/schemas/adaptive-card.json", version="1.0"):
        self.schema = schema
        self.version = version
        self.type = "AdaptiveCard"
        self.body = []
        self.actions = []
        self.pointer = self
    
    def set_pointer(self, item):
        self.pointer = item
        
    def save_level(self):
        return self.pointer
    
    def load_level(self, level):
        self.set_pointer(level)
    
    def add(self, element, recurse=True, is_action=False):
        self.pointer.add_action(element) if is_action else self.pointer.add_item(element)
        element.previous = self.pointer
        if recurse:
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
    
#%%
# initialize card
card = AdaptiveCard()

# Add a textblock
card.add(TextBlock(text="0.45 miles away", separator="true", spacing="large"))

# add column set
card.add(ColumnSet())

# First column contents
card.add(Column(width=2))
card.add(TextBlock(text="BANK OF LINGFIELD BRANCH"))
card.add(TextBlock(text="NE Branch", size="ExtraLarge", weight="Bolder", spacing="None"))
card.add(TextBlock(text="4.2 stars", isSubtle=True, spacing="None"))
card.add(TextBlock(text=f"Some review text for illustration", size="Small", wrap="true"))

# Back up to column set
card.up_one_level() 

# Second column contents
card.add(Column(width=1))
card.add(Image(url="https://s17026.pcdn.co/wp-content/uploads/sites/9/2018/08/Business-bank-account-e1534519443766.jpeg"))

# Output to json
card.to_json()
#%%
element = ActionShowCard()
print(element)

#%%

card = AdaptiveCard()
card.add(TextBlock("Publish Adaptive Card Schema", weight="Bolder", size="medium"))
card.add(ColumnSet())
card.add(Column(width="auto"))
card.add(Image(url='https://pbs.twimg.com/profile_images/3647943215/d7f12830b3c17a5a9e4afcc370e3a37e_400x400.jpeg',
               size="small",
               style="person"))
card.up_one_level()
card.add(Column(width="stretch"))
card.add(TextBlock("Matt Hidinger", weight="Bolder", wrap="true"))
card.add(TextBlock("Created {{DATE(2017-02-14T06:08:39Z, SHORT)}}", isSubtle="true", wrap="true"))
card.up_one_level()
card.up_one_level()
card.add(Container())
card.add(TextBlock("Now that we have defined the main rules and features of the format, we need to produce a schema and publish it to GitHub. The schema will be the starting point of our reference documentation.",
                   wrap="true"))
card.add(FactSet())
card.add(Fact("Board", "Adaptive Card"))
card.add(Fact("List", "Backlog"))
card.add(Fact("Assigned to", "Matt Hidinger"))
card.add(Fact("Due date", "Not set"))
card.up_one_level()
card.add(ActionSet())
card.add(ActionShowCard(title="Comment"), is_action=True)
card.add(InputText(ID='comment', isMultiline="true", placeholder="Enter your comment"), is_action=True)
card.add(ActionSubmit(title="OK"), is_action=True)
card.up_one_level()
card.add(ActionOpenUrl(url="someurl.com", title="View"), is_action=True)
card.to_json(for_print=False)

#%%

card = AdaptiveCard() # initialize
card.add(TextBlock(text="Header", weight="Bolder"))
card.add(TextBlock(text="Subheader"))
card.add(TextBlock(text="*Quote*", isSubtle="true"))

card.add(ColumnSet())
card.add(Column(width=1))
card.add(TextBlock(text="<Column 1 Contents>"))

card.up_one_level() # move back to the column set level

card.add(Column(width=1))
card.add(TextBlock(text="<Column 2 Contents>"))

card.back_to_top() # back to top level

# Adding single url action
card.add(ActionOpenUrl(url="someurl.com", title="Open Me"), is_action=True)

# Add show card
card.add(ActionShowCard(title="Click to Comment"), is_action=True)
card.add(InputText(ID="input", placeholder="Add Comment Here"))
card.add(ActionSubmit(title="OK"), is_action=True)

card.to_json()

#%%

card = AdaptiveCard()
card.add(TextBlock("This is some text"))
card.add(Container(style="emphasis"))
card.add(TextBlock("Emphasis Container"))
card.up_one_level()
card.up_one_level()
card.add(TextBlock("Default container again"))
card.add(InputText(ID="1"))
card.add(ActionSubmit(title="Submit Action"), is_action=True)
card.to_json()

#%%

card = AdaptiveCard()
card.add(Container(bleed="true", style="emphasis"))
card.add(TextBlock("This textbox bleeds into its container"))
card.up_one_level()
card.add(Container(style="good"))
card.add(TextBlock("This textbox does not bleed into its container"))
card.to_json(version="1.0")


#%%

card = AdaptiveCard()
card.add()

#%%

#%%

card = AdaptiveCard()
card.add(ImageSet())
url = "https://adaptivecards.io/content/cats/1.png"
for _ in range(8):
    card.add(Image(url=url))


#%%

card = AdaptiveCard()
for _ in range(2):
    card.add(TextBlock(text="0.45 miles away", separator="true", spacing="large"))
    card.add(ColumnSet())
    card.add(Column(width=2))
    card.add(TextBlock(text="BANK OF LINGFIELD BRANCH"))
    card.add(TextBlock(text="NE Branch", size="ExtraLarge", weight="Bolder", spacing="None"))
    card.add(TextBlock(text="4.2 stars", isSubtle=True, spacing="None"))
    card.add(TextBlock(text="Some review"*10, size="Small", wrap="true"))
    card.up_one_level() # Back up to column set
    card.add(Column(width=1))
    card.add(Image(url="https://s17026.pcdn.co/wp-content/uploads/sites/9/2018/08/Business-bank-account-e1534519443766.jpeg"))
    card.up_one_level() #Back up to column set
    card.up_one_level() #Back up to Container

    card.add(ActionSet())
    card.add(ActionOpenUrl(url="https://adaptivecards.io/content/cats/1.png", title="cats here"), is_action=True)
    card.add(ActionShowCard(title="Action Item"), is_action=True)
    card.add(TextBlock(text="ALL APPOINTMENTS"))

    appointments = [("04:00", "08:00") for _ in range(5)]
    action_showcard_level = card.save_level()

    for (start_time, end_time) in appointments:
        card.add(ColumnSet())
        card.add(Column())
        card.add(TextBlock(text="Appointment"))
        card.up_one_level()
        card.add(Column())
        card.add(TextBlock(text=f"{start_time}"))
        card.up_one_level()
        card.add(Column())
        card.add(TextBlock(text=f"{end_time}"))
        card.up_one_level()
        card.add(Column())
        card.add(ActionSet())
        card.add(ActionSubmit(title="Book this!"), is_action=True)
        card.load_level(action_showcard_level)
    
    card.back_to_top()
    
card.to_json()

#%%

# Creating columns


# Create some rows and columns

sql_output = {
    "Table1": [
        {
            'ID': 'TRN-349824',
            'Amount': '$400.50',
            'Receiver': "Walmart",
            'Date': '29-05-2020'
        },
        {
            'ID': 'TRN-334244',
            'Amount': '$50.35',
            'Receiver': 'Delta Airlines',
            'Date': '01-06-2020'
        },
        {
            'ID': 'TRN-503134',
            'Amount': '$60.50',
            'Receiver': 'Smoothie King',
            'Date': '03-06-2020'
        }
    ]
}

def to_tabular(json_list):
    first_element = json_list[0]
    headers = list(first_element.keys())
    result_table = []
    for item in json_list:
        item_values = list(item.values())
        result_table.append(item_values)
    return (headers, result_table)

(headers, table) = to_tabular(sql_output['Table1'])

#%%
headers 
#%%
card = AdaptiveCard() # Initialize our card
card.add(ColumnSet())

for header in headers:
    card.add(Column())
    card.add(TextBlock(text=header, horizontalAlignment="center", weight="Bolder"))
    card.up_one_level()

card.add(Column())
card.add(TextBlock(text="Suspicious", horizontalAlignment="center", weight="Bolder"))
card.back_to_top()

# Now let's add our transactions
for transaction in table:
    card.add(ColumnSet()) # 'add' pointer is now inside the ColumnSet
    
    for element in transaction:
        card.add(Column()) # 'add' pointer is now inside the Column
        card.add(TextBlock(text=element, horizontalAlignment="center"))
        card.up_one_level() # move pointer back to ColumnSet level
     
    # Add a "Flag" button to allow users to report suspicious transactions 
    card.add(Column())
    card.add(ActionSet())
    transaction_id = transaction[0]
    flag_url = "https://pngimage.net/wp-content/uploads/2018/06/red-flag-png-5.png"
    card.add(ActionSubmit(iconUrl=flag_url, data={"ID": transaction_id}), is_action=True)
    card.back_to_top() # Go back to the top level, ready to add our next row

card.to_json()


#%%

card = AdaptiveCard()
card.add(Container())
card.add(TextBlock(text="Text as the first item, at the container level"))

# create checkpoint
container_level = card.save_level()

# add nested columnsets and columns for fun
for i in range(1, 6):
    card.add(ColumnSet())
    card.add(Column(style="emphasis"))
    card.add(TextBlock(text=f"Nested Column {i}"))

# jump back to container level
card.load_level(container_level)
card.add(TextBlock(text="Text at the container level, below all the nested containers"))
card.to_json()
