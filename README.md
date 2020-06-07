
# Adaptive Card Builder (Python)

**Build and Export Adaptive Cards Pythonically**<br>
Construct adaptive cards element-by-element, like lego. <br>
Build with minimal abstraction and maxiumum readability.

<br>

The **AdaptiveCard** class centrally handles all construction operations: <br>

```python
from adaptivecardbuilder.classes import *

card = AdaptiveCard() # initialize
card.add(TextBlock(text="Header", weight="Bolder"))
card.add(TextBlock(text="Subheader"))
card.add(TextBlock(text="*Quote*", isSubtle="true"))

card_json = card.to_json() # output to json
```

<br>
When rendered:

![Simple Table](https://user-images.githubusercontent.com/44293915/83965757-ff0be680-a8ad-11ea-8936-108e3faa6fee.png)

<br>



**Each individual element** is implemented as a class <br>
These are simply object representations of the standard Adaptive Card elements

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

**General Logic** <br>
The AdaptiveCard class has an internal 'pointer'. When we add an element to the card, the element is added to wherever that pointer is. 
<br>

**When adding elements that can contain other elements** (e.g. column sets and columns), the card's pointer will, by default, **recurse into the added container**, so that any elements added thereafter will go straight into this container. <br>

This is essentially a **depth-first** approach to building cards.

```python
card.add(ColumnSet()) # pointer now at the column set level
card.add(Column(width=1)) # pointer now at the column level
card.add(TextBlock(text="<Column 1 Contents>"))
```


![Column 1 added](https://user-images.githubusercontent.com/44293915/83966745-fd452180-a8b3-11ea-9115-0056f8667102.png)

<br>


As a depth-first approach, we'll need to **back ourselves out** of a container once we are done adding elements to it.

We can do so easily using the *up_one_level()* method, which essentially just moves us back up the element tree

```python
card.add(ColumnSet()) # pointer now at the column set level
card.add(Column(width=1)) # pointer now at the column level
card.add(TextBlock(text="<Column 1 Contents>"))

card.up_one_level() # move back to the column set level

card.add(Column(width=1)) # pointer now at the column level
card.add(TextBlock(text="Column 2 Contents"))
```

