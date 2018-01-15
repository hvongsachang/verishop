We started from CS50 Finance as a baseline and worked from there.  Then we executed our idea step by step, creating core needs of
the website as we went along.

First, we created a SQL database (shoppers.db) using phpLiteAdmin with three tables.  The first table "items" contains information on a item id,
the user id associated with the item wanted, the item name, the store name at which the user wants to buy said item, and the
quantity of the item wanted.  The second table "stores" contains information on all stores in our database.  It's as simple as store
id and store name.  The third and last table "users" is just composed of user id, user name, and hashed password.  Using these three
tables, it was very straightforward to connect information across tables and get the data we want in any capacity.

As for layout.html and index.html, we had to decide which elements of the three tables (items, stores, and users) were relevant to
the user, and thus guiding us on how to display their personal shopping list. This was done through an SQL SELECT statement.
In the def index() in application.py, we created a list of the items the user wishes to buy by grabbing the item name, store from
which they wish to buy the item from, the sum of the quantities if multiple rows in shoppers.db contain the same item name and
store name, and the user's user id. The name of the item, the store from which they wish to buy the item from, and the quantities
make up 3 columns of the overall shopping list that is most useful to the user (store id and item id wouldn't make no sense to them).
This table was generated using Jinja and iterating over the list.

The 4th and last column created in the iteration is an update button, which, when pressed, displays an HTML form above the shopping list,
giving the user the option to change the item name, or where
they want to buy it, or how much they want to buy, or whether they want to delete that item as a whole. To make this HTML form pop-up,
we created a div class called "edit-item" that currently has no HTML code inside it. In the CSS file, we set this 'edit-item' class to
automatically be not shown. In the index.html file, when the button is clicked, it triggers a JavaScript function that adds HTML code
into this "edit-item" class, which includes the HTML form as previously stated, and then makes the div class visible. We decided to take
this approach instead of redirecting the user to another webpage because 1) redirecting the user to a different page to change an item
isn't user-friendly and 2) redirecting the user to a different page would mean that we would have to pass in the values from that row to
a new HTML file, which creates an unnecessary step if all of it ends up in application.py anyway. We used JavaScript to update the inner
HTML of the 'edit-item' div block because we needed to use JavaScript to pass in each row's value when iterating over each row.

One of the most important things that a user should be able to do is to edit/update the items in their list (as mentioned in the previous paragraph).
When a user inputs an item from a store into their list, the user may want to change it or remove it later, as if the user were to carry a
paper list and pen around in their hand, checking off or changing the items as they go along. The main shopping list page (index) and the specific
store list page (list.html) both contain this update button functionality. An update button, when clicked, triggers a JavaScript function that
updates a div class to be shown (as said previously) that contains the values from its row as a default. The user can edit the values
in the input text boxes, and once update is clicked, it sends a post method to application.py in the /edit function, where /edit compares
the new values that the user inputted to the original values from that row, taking into account if the store exists or not. For editing
the quantity, the minimum quantity is 1 because if it were 0, it is essentially "deleting" that row, whose function is already implemented
in the delete button next to the update button. This delete button passes a post method, the values of that row, and triggers a SQL DELETE statement
that deletes rows from the 'items' table that contains the item name and store name of the user's user id.

Central to the index.html home page is our ability to add items.  This is somewhat similar to the buy stock option from pset7, and
we created a simple form with some filler text on top to prompt the reader to fill out a form.  It triggers an action in the
application.py functions to either not add an item succesfully if a) there was no item inputted, b) if there was no recognized store
inputted, or c) if no quantity was specified.  Once complete, it brings the user back to the home page, which is all that is needed
of the add items function.

But given that a user might not type in a recognized store for an item that he or she might buy.  So we decided to make a page for
the user to ensure that the store typed exists.  If yes, the user is redirected to the home page.  If not, they are thus given the
option to add it, thus allowing the user to add an item from the store on that list. When this store is added, application.py capitalizes()
that store name in order to maintain a standard naming convention for the stores. Item names were not automatically capitalized because
in the cases where people wanted to buy 'iPhones' (for example) would want their I's to be lowercase, and not show up as "IPhone". However,
when trying to add 'apple' from a certain store when a user has already inputted 'Apple' from that store, application.py's add() function
will recognize that 'Apple' from a certain store already exists using a SQL SELECT statement comparing 'apple' to 'Apple' using the LIKE
operator, and will update the existing 'Apple''s quantity instead of adding 'apple' to the database.

The last core need is the ability for the website to create a list of items that need to bought from the store of interest. This was
done by querying the items for the current user based on store wanted.  All items associated with the store for the user will be
taken and then printed onto a page for the user to view.  Here, there is an option to edit the item, which helps the user change the
item once viewing it in an organized location.

In terms of cleaning up code from CS50 Finance, we got rid of code that did not pertain to ours. For example,  one small thing that we
changed was the apology function, which occured when a user did an invalid action. We got rid of the apology function and replaced it
with flash messages and redirects to different pages instead (dependent on success or failure), which makes it slightly more
professional than looking at a cat. Other functions include getting rid of usd() and lookup().

From here, once all implementations were complete, we moved on to rework the website design.  We included fonts standard to modern
day design standards and added a color that was deemed as both pleasing to the eye and encouraging for further consumption.  We
designed the table so that some text was in the right orientation and the button colors matched the schemes.