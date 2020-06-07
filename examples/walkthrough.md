# Examples
Some examples of using the Adaptive Card Builder classes

<br/>


##  1. Creating a "Table"-type card to display tabular data

**Intended Output - table with actionable buttons unique to each row**
![enter image description here](https://user-images.githubusercontent.com/44293915/83948325-8442bd00-a814-11ea-9278-b2773ac9a1c2.png)
<br>
<br>

**Raw Data Format**
Picture this kind of HTTP response from a SQL database query regarding transactions data:
```js
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
```

<br>
<br>

**Formatting data**
Let's convert this JSON into a list of lists:

```python
# Helper function
def to_tabular(json_list):
    first_element = json_list[0]
    headers = list(first_element.keys())
    result_table = []
    for item in json_list:
        item_values = list(item.values())
        result_table.append(item_values)
        return (headers, result_table)

(headers, table) = to_tabular(sql_output['Table1'])

print(headers)
print(table)
>>>['ID', 'Amount', 'Receiver', 'Date']
>>>[['TRN-349824', '$400.50', 'Walmart', '29-05-2020'],
    ['TRN-334244', '$50.35', 'Delta Airlines', '01-06-2020'],
    ['TRN-503134', '$60.50', 'Smoothie King', '03-06-2020']]
```

<br>
<br>

**Initialize our Adaptive Card and add headers**
```python
card = AdaptiveCard() # Initialize our card

card.add(ColumnSet()) # Add a ColumnSet

for header in headers:
    card.add(Column()) 
    card.add(TextBlock(text=header, horizontalAlignment="center")) # add text
    card.up_one_level() # Back to ColumnSet level, ready to add more columns
```

<br>

|ID|Amount|Reciever|Date
|--|--|--|--|



<br>
<br>

**Add a final "Suspicious" column, where we'll place buttons on each row later**

```python
card.add(Column())
card.add(TextBlock(text="Suspicious", horizontalAlignment="center", weight="Bolder"))
card.back_to_top() # Back to ColumnSet level again
```
<br>

|ID|Amount|Reciever|Date|Suspicious
|--|--|--|--|--|

<br> 
<br>

**Let's now add the transactions, line by line**

```python
for transaction in table:
    card.add(ColumnSet()) # 'add' pointer is now inside the ColumnSet
    
    for element in transaction:
        card.add(Column()) # 'add' pointer is now inside the Column
        card.add(TextBlock(text=element, horizontalAlignment="center"))
        card.up_one_level() # move pointer back to ColumnSet level
```

|ID|Amount|Reciever|Date|Suspicious
|--|-------|-------|-----|---------|
|TRN-349824|$400.50|Walmart|29-05-2020


<br>
Now add the button as the last column entry

```python
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
    card.add(ActionSubmit(iconUrl=flag_url, data={"Transaction_ID": transaction_id}))
    card.back_to_top() # Go back to the top level, ready to add our next row
```


