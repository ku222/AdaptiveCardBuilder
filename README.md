
# Python Adaptive Card Builder

**Easily Build and Export Multilingual Adaptive Cards Through Python**<br>
- Programmatically construct adaptive cards like Lego, without the learning curve of Adaptive Card 'Templating'
- Avoid the curly-braces jungle of traditional JSON editing
- Build pythonically, but with minimal abstraction while preserving readability
- Output built cards to JSON or a Python Dictionary in a single method call
- Auto-translate all text elements in a card with a single method call
- Send output to any channel with Adaptive Card support to be rendered.

<br>

**View this package on pypi** <br>
https://pypi.org/project/adaptivecardbuilder/

<br>

**Installation via pip** <br>
```python
pip install adaptivecardbuilder
```

<br>

**Learn about Adaptive Cards:** <br>
- Home Page: https://adaptivecards.io/
- Adaptive Card Designer: https://adaptivecards.io/designer/
- Schema Explorer: https://adaptivecards.io/explorer/
- Documentation: https://docs.microsoft.com/en-us/adaptive-cards/

<br>

### Adaptive Card Builder "Hello World":

```python
from adaptivecardbuilder import *

# initialize card
card = AdaptiveCard()

# Add a textblock
card.add(TextBlock(text="0.45 miles away", separator="true", spacing="large"))

# add column set
card.add(ColumnSet())

# First column contents
card.add(Column(width=2))
card.add(TextBlock(text="BANK OF LINGFIELD BRANCH"))
card.add(TextBlock(text="NE Branch", size="ExtraLarge", weight="Bolder"))
card.add(TextBlock(text="4.2 stars", isSubtle=True, spacing="None"))
card.add(TextBlock(text=f"Some review text for illustration", size="Small"))

# Back up to column set
card.up_one_level() 

# Second column contents
card.add(Column(width=1))
card.add(Image(url="https://s17026.pcdn.co/wp-content/uploads/sites/9/2018/08/Business-bank-account-e1534519443766.jpeg"))

# Serialize to a json payload with a one-liner
await card.to_json()
```

Output when rendered: <br>


<img src="https://user-images.githubusercontent.com/44293915/83967653-7ac06000-a8bb-11ea-843a-d045856ddf7f.png" alt="table" width="500"/>


<br>
<br>
<br>

## A "Visual" Alternative

The ```AdaptiveCard``` class also supports a more visual approach to building cards by passing a list of elements to the ```add()``` method instead. <br> 

This allows us to freely indent our code within the method call and better illustrate card structure.

When using this visual alternative approach to building cards, we can use specific strings to execute logic.
- Strings containing ```"<"``` move us up/back a level in the tree
- Strings containing ```"^"``` will move us back to the top of the tree

```python
card = AdaptiveCard()

# Add a list of elements
card.add([
    TextBlock("Top Level"),
    ColumnSet(),
        Column(),
            TextBlock("Column 1 Top Item"),
            TextBlock("Column 1 Second Item"),
            "<",
        Column(),
            TextBlock("Column 2 Top Item"),
            TextBlock("Column 2 Second Item"),
            "<",
        "<",
    TextBlock("Lowest Level"),
    
    ActionOpenUrl(title="View Website", url="someurl.com"),
    ActionShowCard(title="Click to Comment"),
        InputText(ID="comment", placeholder="Type Here"),
        ActionSubmit(title="Submit Comment")
])

await card.to_json()
```
<br>

<img src="https://user-images.githubusercontent.com/44293915/84180249-177f2b00-aa7f-11ea-94ec-c2923a9d3bd1.png"  width="400"/>

<br>
<br>
<br>


## Translating Card Elements

Passing translator arguments to the ```to_json()``` method will translate cards. <br>
Using the example above, we can translate the created card in the same method call. <br>
To view a list of supported languages and language codes, go to:
https://docs.microsoft.com/en-us/azure/cognitive-services/translator/language-support



```python
# Translate all text in card to Malay
await card.to_json(translator_to_lang='ms', translator_key='<YOUR AZURE API KEY>')
```

<img src="https://i.ibb.co/kBTJb1m/Malay-screenshot.png" width="400"/>

<br>
<br>

If any ```translator_to_lang``` argument is passed, translation will apply to all elements with translatable text attributes. <br>

To specify that a given Adaptive element **should not** be translated, simply pass the keyworded argument ```dont_translate=True``` during the construction of any element, and AdaptiveCardBuilder will leave this specific element untranslated.

<br>
<br>

## Concepts

The ```AdaptiveCard``` class centrally handles all construction & element-addition operations: <br>

```python
from adaptivecardbuilder import *

card = AdaptiveCard() # initialize

    # Structure:
    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body=[]
    # |   |--Actions=[]

card.add(TextBlock(text="Header", weight="Bolder"))
card.add(TextBlock(text="Subheader"))
card.add(TextBlock(text="*Quote*", isSubtle="true"))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |   |--Actions

card_json = card.to_json() # output to json
```

<br>

When rendered:

<img src="https://user-images.githubusercontent.com/44293915/83965757-ff0be680-a8ad-11ea-8936-108e3faa6fee.png" alt="table" width="500"/>

<br>
<br>
<br>

**Each individual adaptive object (e.g. TextBlock, Column)** is implemented as a class. <br>

These are simply Python object representations of the standard Adaptive Card elements that take keyworded arguments as parameters. <br>
View the Schema Explorer at https://adaptivecards.io/explorer/ to see which keyword arguments each Adaptive Object is allowed to take.


```python
TextBlock(text="Header", weight="Bolder")

# Internal representation
>>> {
        "type": "TextBlock",
        "text": "Header",
        "weight": "Bolder"
    }
```



<br>
<br>

### Pointer Logic

Central to the ```AdaptiveCard``` class is an internal ```_pointer``` attribute. When we add an element to the card, the element is by default **added to the item container** of whichever object is being pointed at. 
<br>

Conceptually, an adaptive object (e.g. Column, Container) can have up to two kinds of containers (python ```list```s):
1. **Item** containers (these hold non-interactive elements like TextBlocks, Images)
2. **Action** containers (these hold interactive actions like ActionShowUrl, ActionSubmit)

For instance:
- ```AdaptiveCard``` objects have both **item** (```body=[]```) and **action** (```actions=[]```) containers
- ```ColumnSet``` objects have a single **item** (```columns=[]```) container
- ```Column``` objects have a single **item** (```items=[]```) container
- ```ActionSet``` objects have a single **action** (```actions=[]```) container


The ```card.add()``` method will add a given AdaptiveObject to the appropriate container. For instance, if an Action-type object is passed, such as a ```ActionSubmit``` or ```ActionOpenUrl```, then this will be added to the parent object's **action** container.

If the parent object does not have the appropriate container for the element being added, then this will throw an ```AssertionError``` and a corresponding suggestion.

<br>
<br>

### Recursing Into an Added Element

**When adding elements that can *themselves* contain other elements** (e.g. column sets and columns), the pointer will by default **recurse into the added element**, so that any elements added thereafter will go straight into the added element's container (making our code less verbose). <br>

This is essentially a **depth-first** approach to building cards:

```python
card = AdaptiveCard() 
       
    # |--Card               <- Pointer
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body=[]
    # |   |--Actions=[]

card.add(TextBlock(text="Header", weight="Bolder"))

    # |--Card               <- Pointer
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body               
    # |       |--TextBlock     <- added
    # |   |--Actions

card.add(TextBlock(text="Subheader"))
card.add(TextBlock(text="*Quote*", isSubtle="true"))

    # |--Card               <- Pointer
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body               
    # |       |--TextBlock
    # |       |--TextBlock     <- added
    # |       |--TextBlock     <- added
    # |   |--Actions

card.add(ColumnSet())

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet        <- Pointer <- added
    # |   |--Actions

card.add(Column(width=1))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet
    # |           |--Column         <- Pointer <- added
    # |   |--Actions

card.add(TextBlock(text="<Column 1 Contents>"))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet
    # |           |--Column         <- Pointer
    # |               |--TextBlock  <- added
    # |   |--Actions

```
<br>
Rendered: <br>

<img src="https://user-images.githubusercontent.com/44293915/83966745-fd452180-a8b3-11ea-9115-0056f8667102.png" alt="table" width="500"/>


<br>
<br>


Observe that when adding a ```TextBlock``` to a ```Column```'s items, the pointer stays at the ```Column``` level, rather than recursing into the ```TextBlock```. The ```add()``` method will only recurse into the added element if it has an **item** or **action** container within it.

Because of the depth-first approach, we'll need to **back ourselves out** of a container once we are done adding elements to it. <br>
One easy method to doing so is by using the ```up_one_level()``` method, can be called multiple times and just moves the pointer one step up the element tree.


```python
card = AdaptiveCard()
card.add(TextBlock(text="Header", weight="Bolder"))
card.add(TextBlock(text="Subheader"))
card.add(TextBlock(text="*Quote*", isSubtle="true"))

card.add(ColumnSet())
card.add(Column(width=1))
card.add(TextBlock(text="<Column 1 Contents>"))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet
    # |           |--Column         <- Pointer
    # |               |--TextBlock  <- added
    # |   |--Actions

card.up_one_level()

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet          <- Pointer
    # |           |--Column        
    # |               |--TextBlock  
    # |   |--Actions

card.add(Column(width=1))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet       
    # |           |--Column        
    # |               |--TextBlock
    # |           |--Column         <- Pointer <- added
    # |   |--Actions

card.add(TextBlock(text="Column 2 Contents"))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet       
    # |           |--Column        
    # |               |--TextBlock
    # |           |--Column         <- Pointer
    # |               |--TextBlock  <- added
    # |   |--Actions
```

<br>

Rendered: <br>

<img src="https://user-images.githubusercontent.com/44293915/83967818-d17a6980-a8bc-11ea-9518-1a3e15dfa38e.png" alt="table" width="500"/>

<br>
<br>

We can also use the ```card.save_level()``` method to create a "checkpoint" at any level if we intend to back ourselves out to the level we are currently at in our code block. To "reload" to that checkpoint, use ```card.load_level(checkpoint)```.

```python
# checkpoints example
card = AdaptiveCard()
card.add(Container())
card.add(TextBlock(text="Text as the first item, at the container level"))

# create checkpoint here
container_level = card.save_level()

# add nested columnsets and columns for fun
for i in range(1, 6):
    card.add(ColumnSet())
    card.add(Column(style="emphasis"))
    card.add(TextBlock(text=f"Nested Column {i}"))
    # our pointer continues to move downwards into the nested structure

# reset pointer back to container level
card.load_level(container_level)
card.add(TextBlock(text="Text at the container level, below all the nested containers"))
card.to_json()
```


<img src="https://user-images.githubusercontent.com/44293915/83975014-3055d800-a8e9-11ea-8f6a-3284ee9a48db.png" alt="table" width="450"/>

<br>
<br>
<br>

## Adding Actions

As previously mentioned, the AdaptiveCard's ```add()``` method will automatically add action elements to the appropriate containers.

Let's first move our pointer back to the top level using the ```back_to_top()``` method:

```python
card.back_to_top() # back to top of tree

    # |--Card                   <- Pointer
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body               
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet       
    # |           |--Column        
    # |               |--TextBlock
    # |           |--Column         
    # |               |--TextBlock
    # |   |--Actions
```

<br>

Our pointer is now pointing at the main Card object. <br>
Because it has an **Actions** container, the next action element to be added will be sent there.


```python
# Adding single url action
card.add(ActionOpenUrl(url="someurl.com", title="Open Me"))

    # |--Card                       <- Pointer
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body               
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet       
    # |           |--Column        
    # |               |--TextBlock
    # |           |--Column         
    # |               |--TextBlock
    # |   |--Actions                    
    # |       |--ActionOpenUrl      <- added

```

<br>

<img src="https://user-images.githubusercontent.com/44293915/83968535-da216e80-a8c1-11ea-8dd2-33ff5aa21fc3.png" alt="table" width="500"/>
