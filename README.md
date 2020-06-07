
# Adaptive Card Builder (Python)

<br>

**Build and Export Adaptive Cards Programmatically**<br>
Construct adaptive cards element-by-element, like lego. <br>
Build pythonically, with minimal abstraction and maximum readability.

<br>


```python
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

# Output to json
card.to_json()
```

<br>


<img src="https://user-images.githubusercontent.com/44293915/83967653-7ac06000-a8bb-11ea-843a-d045856ddf7f.png" alt="table" width="400"/>


<br>
<br>

## Concepts

The **AdaptiveCard** class centrally handles all construction operations: <br>

```python
from adaptivecardbuilder.classes import *

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
<br>

When rendered:

<img src="https://user-images.githubusercontent.com/44293915/83965757-ff0be680-a8ad-11ea-8936-108e3faa6fee.png" alt="table" width="400"/>

<br>
<br>


**Each individual element** is implemented as a class. <br>
These are simply object representations of the standard Adaptive Card elements:

```python
element = TextBlock(text="Header", weight="Bolder")
print(element)

>>> {
        "type": "TextBlock",
        "text": "Header",
        "weight": "Bolder"
    }
```

<br>
<br>

**General Logic** <br>
The AdaptiveCard class has an internal 'pointer'. When we add an element to the card, the element is **added to the container** of whichever object is being pointed at. 
<br>

**When adding elements that can contain other elements** (e.g. column sets and columns), the pointer will by default **recurse into the added element**, so that any elements added thereafter will go straight into the added element's container. <br>

This is essentially a **depth-first** approach to building cards:

```python
card = AdaptiveCard() 
card.add(TextBlock(text="Header", weight="Bolder"))
card.add(TextBlock(text="Subheader"))
card.add(TextBlock(text="*Quote*", isSubtle="true"))

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body               <- Pointer
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |   |--Actions

card.add(ColumnSet())

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet        <- Pointer
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
    # |           |--Column         <- Pointer
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
    # |               |--TextBlock
    # |   |--Actions

```
<br>
Rendered: <br>

<img src="https://user-images.githubusercontent.com/44293915/83966745-fd452180-a8b3-11ea-9115-0056f8667102.png" alt="table" width="400"/>


<br>
<br>


As a depth-first approach, we'll need to **back ourselves out** of a container once we are done adding elements to it. <br>
We can do so easily using the *up_one_level()* method, which just moves us back up the element tree:

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
    # |               |--TextBlock
    # |   |--Actions

card.up_one_level()

    # |--Card
    # |   |--Schema="XXX"
    # |   |--Version="1.0"
    # |   |--Body
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--TextBlock
    # |       |--ColumnSet       <- Pointer
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
    # |           |--Column         <- Pointer
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
    # |               |--TextBlock
    # |   |--Actions
```



