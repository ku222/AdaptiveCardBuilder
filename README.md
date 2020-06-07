
# Python Adaptive Card Builder (PREVIEW)

**Easily Build and Export Adaptive Cards Through Python**<br>
- Programmatically construct adaptive cards like Lego, without the learning curve of Adaptive Card 'Templating'
- Avoids the deeply-nested visual format of traditional JSON editing
- Build pythonically, but with minimal abstraction while preserving readability
- Send output to any channel with Adaptive Card support to be rendered.

<br>

**Learn about Adaptive Cards:** <br>
- Home Page: https://adaptivecards.io/
- Adaptive Card Designer: https://adaptivecards.io/designer/
- Schema Explorer: https://adaptivecards.io/explorer/
- Documentation: https://docs.microsoft.com/en-us/adaptive-cards/

<br>

### Adaptive Card Builder "Hello World":

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

# Serialize to a json payload with a one-liner
card.to_json()
```

Output when rendered: <br>


<img src="https://user-images.githubusercontent.com/44293915/83967653-7ac06000-a8bb-11ea-843a-d045856ddf7f.png" alt="table" width="500"/>


<br>
<br>

## Concepts

The ```AdaptiveCard``` class centrally handles all construction & element-addition operations: <br>

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

<img src="https://user-images.githubusercontent.com/44293915/83965757-ff0be680-a8ad-11ea-8936-108e3faa6fee.png" alt="table" width="500"/>

<br>
<br>


**Each individual element** is implemented as a class. <br>
These are simply Python object representations of the standard Adaptive Card elements that take keyworded arguments as parameters like so:

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

### Pointer Logic

Central to the ```AdaptiveCard``` class is an internal ```pointer``` attribute. When we add an element to the card, the element is by default **added to the item container** of whichever object is being pointed at. 
<br>

Conceptually, an object can have up to two kinds of containers (python ```list```s):
1. **Item** containers (these hold non-interactive elements like TextBlocks, Images)
2. **Action** containers (these hold interactive actions like ActionShowUrl, ActionSubmit)

For instance:
- ```AdaptiveCard``` objects have both **item** (```body=[]```) and **action** (```actions=[]```) containers
- ```ColumnSet``` objects have a single **item** (```columns=[]```) container
- ```Column``` objects have a single **item** (```items=[]```) container
- ```ActionSet``` objects have a single **action** (```actions=[]```) container


The ```card.add()``` method by default adds any new elements to the **item** container of an object being pointed at. However, we can add to the **actions** container by setting ```is_action=True```. We'll come back to examples of adding actions later.

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

## Adding Actions

The ```add()``` method has an optional ```is_action``` parameter - if we set this to ```True``` when adding an element to the object being pointed at, then the element is instead added to that object's **actions** container (if it has one).

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
Because it has an **Actions** container, we can add actions to it by setting ```is_action=True``` within the ```add()``` method:


```python
# Adding single url action
card.add(ActionOpenUrl(url="someurl.com", title="Open Me"), is_action=True)

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


<br>
<br>


## Worked Example 1 - Creating a simple table with row-specific action buttons

<br> 

**Intended Output** <br>
Table with actionable buttons unique to each row:

- Each row is represented as a ```ColumnSet```
  - Each column in the row is a ```Column``` object
    - Values in each column are ```TextBlock``` objects

<img src="https://user-images.githubusercontent.com/44293915/83948325-8442bd00-a814-11ea-9278-b2773ac9a1c2.png" alt="table" width="500"/>





<br>
<br>


**Full Code** <br>
Here's our full Adaptive Card Builder-related code for creating the table from our input data:

```python
card = AdaptiveCard()

# Add our first "row" for table headers
card.add(ColumnSet()) 

# Add headers as columns + bold textblocks
for header in headers:
    card.add(Column()) 
    card.add(TextBlock(text=header, horizontalAlignment="center", weight="Bolder"))
    card.up_one_level() # Back to ColumnSet level

# Back to Card's main body
card.back_to_top()

# Adding our transactions
for transaction in table:
    card.add(ColumnSet()) 
    
    for element in transaction:
        card.add(Column()) 
        card.add(TextBlock(text=element, horizontalAlignment="center"))
        card.up_one_level() # move pointer back to ColumnSet level

    # Before moving to the next row, add a "Flag" button
    card.add(Column())
    card.add(ActionSet())
    flag_url = "https://pngimage.net/wp-content/uploads/2018/06/red-flag-png-5.png"
    transaction_id = transaction[0]
    data = {"ID": transaction_id} # data to submit to our hosting interface
    card.add(ActionSubmit(iconUrl=flag_url, data=data), is_action=True)
    card.back_to_top() # Go back to the top level, ready to add our next row
```


<br>
<br>

### Step-by-Step Walkthrough <br>

**Raw Data Format** <br>
Picture this kind of HTTP response from a SQL database query regarding transactions data:
```json
sql_output = {
	"Table1": [
		{
			"ID": "TRN-349824",
			"Amount": "$400.50",
			"Receiver": "Walmart",
			"Date": "29-05-2020"
		},
		{
			"ID": "TRN-334244",
			"Amount": "$50.35",
			"Receiver": "Delta Airlines",
			"Date": "01-06-2020"
		},
		{
			"ID": "TRN-503134",
			"Amount": "$60.50",
			"Receiver": "Smoothie King",
			"Date": "03-06-2020"
		}
	]
}
```

<br>
<br>

**Formatting data** <br>
Let's convert this JSON into a list of lists which makes it a bit more workable

```python
# One-off helper function
def to_tabular(json_list):
    first_element = json_list[0]
    headers = list(first_element.keys())
    result_table = []
    for item in json_list:
        item_values = list(item.values())
        result_table.append(item_values)
        return (headers, result_table)

(headers, table) = to_tabular(sql_output['Table1'])
headers.append('Suspicious') # Add 'suspicious' column

print(headers)
print(table)
>>>['ID', 'Amount', 'Receiver', 'Date', 'Suspicious']
>>>[['TRN-349824', '$400.50', 'Walmart', '29-05-2020'],
    ['TRN-334244', '$50.35', 'Delta Airlines', '01-06-2020'],
    ['TRN-503134', '$60.50', 'Smoothie King', '03-06-2020']]
```

<br>
<br>

**Initialize our Adaptive Card and add headers**
```python
card = AdaptiveCard()

# Add our first "row" for table headers
card.add(ColumnSet()) 

# Add headers as columns + bold textblocks
for header in headers:
    card.add(Column()) 
    card.add(TextBlock(text=header, horizontalAlignment="center", weight="Bolder"))
    card.up_one_level() # Back to ColumnSet level
```

<br>

Here's what we have so far:

|ID|Amount|Reciever|Date|Suspicious
|--|--|--|--|--|

<br> 
<br>

**Let's now add the transactions, line by line**

```python
...
# Back to Card's main body
card.back_to_top()

# Adding our transactions
for transaction in table:
    card.add(ColumnSet()) 
    
    for element in transaction:
        card.add(Column()) 
        card.add(TextBlock(text=element, horizontalAlignment="center"))
        card.up_one_level() # move pointer back to ColumnSet level
```

Here's what we have after the inner loop is complete (first row):

|ID|Amount|Reciever|Date|Suspicious
|--|-------|-------|-----|---------|
|TRN-349824|$400.50|Walmart|29-05-2020


<br>
Now let's add the button as the last column entry

```python
...
    for element in transaction:
        card.add(Column()) 
        card.add(TextBlock(text=element, horizontalAlignment="center"))
        card.up_one_level() # move pointer back to ColumnSet level

    # Before moving to the next row, add a "Flag" button
    card.add(Column())
    card.add(ActionSet())
    flag_url = "https://pngimage.net/wp-content/uploads/2018/06/red-flag-png-5.png"
    transaction_id = transaction[0]
    data = {"ID": transaction_id} # data to submit to our hosting interface
    card.add(ActionSubmit(iconUrl=flag_url, data=data), is_action=True)
    card.back_to_top() # Go back to the top level, ready to add our next row
```


|ID|Amount|Reciever|Date|Suspicious
|--|-------|-------|-----|---------|
|TRN-349824|$400.50|Walmart|29-05-2020| [FLAG-BUTTON]

<br>


**When the outer loop is complete**, we have a fully populated table complete with buttons on each row that a user can click on to report suspicious transactions. Each button is specific to the row, and will submit the transaction ID of that row (or whatever data we like) to whichever interface is hosting the Adaptive Card.


<br>
<br>

# Worked Example 2: Banks and Appointments


### List of nearest banks and their free appointment slots


Example of the finished product: <br>

<img src="https://user-images.githubusercontent.com/44293915/83976434-ba09a380-a8f1-11ea-9ec6-711fe357e128.png" alt="table" width="500"/>

<br>


Here's an example of the data behind this:

```python
# branch names
branches = ["NE Branch", "SE Branch", "SW Branch", "NW Branch"]

# distances in miles
distances = { 
    "NE Branch": 4.5,
    "SE Branch": 5.0,
    "SW Branch": 6.5,
    "NW Branch": 7.0
}

# appointment slots per bank (start time, end time)
appointments = {
    "NE Branch": [("08:00", "09:00"), ("09:15", "10:30")],
    "SE Branch": [("09:00", "09:30"), ("13:15", "14:15"), ("15:00", "17:00")],
    "SW Branch": [("11:00", "13:30")],
    "NW Branch": [("08:15", "08:45"), ("13:15", "14:15"), ("15:00", "17:00"), ("17:00", "18:00")]
}

```

<br>

Adaptive Card Builder allows us to break up the construction of this into more manageable programmatic blocks. 
<br>

We'll utilize loops to construct a card for each bank, complete with its appointment info and a link to view the banks location on a map. 
<br>

Let's first add our bank info and an image onto the card:

```python
# initialize our card
card = AdaptiveCard()

# loop over branches - each one will have a mini-card to itself
for branch in branches:
    card.add(TextBlock(text=f"{distances[branch]} miles away", separator="true", spacing="large"))
    card.add(ColumnSet())
    
    # First column - bank info
    card.add(Column(width=2))
    card.add(TextBlock(text="BANK OF LINGFIELD BRANCH"))
    card.add(TextBlock(text=branch, size="ExtraLarge", weight="Bolder", spacing="None"))
    card.add(TextBlock(text="5 stars", isSubtle=True, spacing="None"))
    card.add(TextBlock(text="Bank Review"*10, size="Small", wrap="true"))
    
    card.up_one_level() # Back up to column set
    
    # Second column - image
    card.add(Column(width=1))
    img = "https://s17026.pcdn.co/wp-content/uploads/sites/9/2018/08/Business-bank-account-e1534519443766.jpeg"
    card.add(Image(url=img))
    
    card.up_one_level() #Back up to column set
    card.up_one_level() #Back up to Container
```

<br>

**Now to add our interactive elements:**
- The "View on Map" button
- Expandible "View Appointments" card

```python
    # add action set to contain our interactive elements
    card.add(ActionSet())

    # First add our "View on Map" button
    card.add(ActionOpenUrl(url="map_url.com", title="View on Map"), is_action=True)
    
    # create expandible card to show all our bank-specific appointment items
    card.add(ActionShowCard(title="View Appointments"), is_action=True)
    
    # Save a checkpoint at this level to come back to later
    action_showcard_level = card.save_level()

    # now loops over appointment items and add them
    for (start_time, end_time) in appointments[branch]:
        card.add(ColumnSet())
        
        # Add our slots, start, end times
        row_items = ["Slot", start_time, end_time]
        for item in row_items:
            card.add(Column(style="emphasis", verticalContentAlignment="Center"))
            card.add(TextBlock(text=item, horizontalAlignment="Center"))
            card.up_one_level() # Back to column set level

        # Add the "Book This!" button, in the final column
        card.add(Column())
        card.add(ActionSet())
        card.add(ActionSubmit(title="Book this!", data={"Appt": f"({start_time}, {end_time})"}), is_action=True)
        card.load_level(action_showcard_level) # back to showcard's body
    
    # Go back to the main body of the card, ready for next branch
    card.back_to_top()
```

<br>

**Finally, output the result to a JSON**:

```python
card.to_json()
```