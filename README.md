# trifacta-wrangler

This tutorial walks through editing a sample dataset using the free tool Trifacta Wrangler, which is available for download [here](https://www.trifacta.com/start-wrangling/). The sample dataset used here is a csv of play-by-play data from the 2016 NFL season, which can be downloaded [here](https://github.com/jlove29/trifacta-wrangler/blob/master/sampleData.csv.zip). [This](https://github.com/jlove29/trifacta-wrangler/blob/master/additionalData.csv) second dataset will also come in handy for the last part of the tutorial.

Once Trifacta Wrangler is downloaded, select **new flow**—this will create a new flow in which you can organize your dataset. Then select **add datasets to flow**, and then **import dataset**. 

From the import dataset window, you can either drag and drop playbyplay.csv, or **choose file** from your computer. Once you have done that, make sure your dataset is selected, then **add**.

Trifacta Wrangler works by generating *scripts* that apply *transformations* to your data, and then compiling multiple scripts into a *recipe*. Multiple datasets and recipes are organized in a *flow*.
 
Trifacta Wrangler will automatically generate an initial recipe for your dataset that will convert it from is original format to something Wrangler can transform. Because it is a CSV, this recipe will include steps such as converting newline characters and commas into new rows and columns. However, it will generate similar scripts from JSON files as well.

Select **edit recipe** to bring up the transform builder and a preview of the dataset. Here is a quick rundown of the editor's important features:

Data Quality indications
- For each column, Wrangler displays the percentage of the data that is *valid* (the same format as the selected or inferred data type), *invalid* (a different format), and *empty*.
- This is visible for each column directly below the column name. If the bar is completely green, the data is 100% valid values; invalid values are red and empty values are gray. 
- In the NFL dataset, the first columns are all 100% complete, but other columns are missing values—for example, the column *OffenseTeam* has many empty values. Hovering over the gray part of the bar shows that there are 3,376 empty values in that column.

Data Types
- Wrangler will also guess at the data type of each of your columns, and display an icon of the data type next to the column name.
- Knowing the data type helps Wrangler suggest which transformations might be useful/applicable.
- There are many different supported types, which can be viewed, along with more on data types [here](https://docs.trifacta.com/display/PE/Supported+Data+Types).

Grid vs. Column view
- With large datasets and/or datasets with many columns, you may want to see only a few of them when writing transformations.
- Selecting *columns* will allow you to select which columns are visible in the grid view.
- It will also give you the data quality indication for each column.

Transformation Builder
- This is the main feature of the tool. It allows you to choose from broad types of transformations and then customize them to edit your own data.
- Below, I'll walk through a quick tutorial of how to edit the NFL data set you've just imported. I'll include both how to make and customize the transformations and the wrangle script that accompanies them.
- While you can switch directly to the editor (*Switch to editor*) and enter your script that way, it is much easier and better for understanding your data to use the builder, and it doesn't decrease functionality at all.

First things first: matching the data types. For the most part, Wrangler is good at guessing your data types, but it thinks our first column *GameId* is a phone number. 
- In the transform builder, choose the **settype** transform, *GameId* as the column, and enter *Integer* as the new type, then select **add to recipe**.
- `settype col: GameId type: 'Integer'`

Next, the *Second* column (not the 2nd column, but the one labeled *Second*) doesn't seem like it would be very valuable all alone; however, it could be used to add more detail to the *Minutes* column. However, we want to also retain the *Minute* column so we can use it if we want that time increment instead. For this we will use the **derive** transform.
- Select the derive transform. The formula here is complicated: `DATEFORMAT(TIME(0, NewMinute, Second), 'HH:mm:ss')`. 
- Essentially, it converts (0, val. from col. *NewMinute*, val. from col. *Second*) to a *TIME* format. However, Wrangler can't display *TIME* formats, so you have to convert it to the displayable *DATEFORMAT*, with the guide of *HH:mm:ss*. More [here](https://docs.trifacta.com/display/PE/TIME+Function).
- `derive value: dateformat(time(0, Minute, Second), 'HH:mm:ss') as: 'HourMinuteSecond'`

Now, we don't need the *Second* column any more, so we can drop it. 
- In the builder, select the **drop** transformation, then *Second*.
- Alternatively, use the dropdown menu next to the column header to select **drop**.
- `drop col: Second`

We can also remove some of the other useless columns that were in the CSV. 
- In the builder, select **drop** and then the empty columns: *column12*, *column14*, *column19*,  and *Challenger*. 
- The bar graphs under each column name are also helpful: although all of the data in *NextScore* and *TeamWin* is valid, there is only one value (0), represented by a single bar, along with *SeasonYear*, which is all 2016.
- `drop col: column12, column14, column18, column19, Challenger, NextScore, TeamWin, SeasonYear`

There are also some columns with mismatched types. For example, in the *Formation* column, some of the values have quotes around them and others do not. We want a standard format without quotes. 
- An easy way to do this is by selecting just the double quote before a value in *Formation*.
- The quotes that begin and end values in each of the other columns will also select. 
- When you select, Wrangler gives you some suggestions for transformations you might want to execute. The first suggestion, ``replace on: `{start}"|"{end}` ``, replaces double quote (") characters on the beginning and end of cells. 
- Choose **modify** to see the builder. This transform shows the column (*Formation*), the pattern to be replaced, and the New Value to insert (which, in this case, is blank). 
- We want to select all of the columns that need editing, and then **Add to Recipe**.
- Alternatively, you can enter the Editor to make the transformation global to the data sheet.
- ``replace col: * with: '' on: `{start}"|"{end}` global: true``

Now, we will edit the Penalty columns. However, the column *IsPenalty* isn't next to the other penalty columns (*IsPenaltyAccepted*, *PenaltyTeam*, etc).
- We can use the **move** transform to move *IsPenalty* to before *IsPenaltyAccepted*.
- `move col: IsPenalty before: IsPenaltyAccepted`

Next, the *IsPenaltyAccepted* column. While there are values for every row, this column is really only relevant for the times when there actually is a penalty. 
- We will use the **derive** transformation again, but use a different type of formula.
- Instead, it will be conditional: if the *IsPenalty* value is 0, then remove the value in *IsPenaltyAccepted*.
- In other words: `IF(IsPenalty==0, Null(), IsPenaltyAccepted)`
- Also, we can use the transform editor to rename our result from *column1* to something else (I used *IsPenaltyAccepted_New*)
- `derive value: if(IsPenalty==0, null(), IsPenaltyAccepted) as: 'IsPenaltyAccepted_New'`
- Then, we can **drop** the old *IsPenaltyAccepted*. We can repeat this whole process for *PenaltyYards*, which has a similar problem, as well as *IsTwoPointConversionSuccessful* (except using *IsTwoPointConversion*, and *IsChallengeReversed* using *IsChallenge*.

We can also pull out text data from the long, unwieldy *Description* column. 
- We want to beef up our penalty data by adding a column describing the penalty. However, this isn't as simple as selecting the name of a penalty—Wrangler isn't good enough to know what strings describe penalties and which describe players or other descriptors. We have to get a reference that is specific enough to get only the results we want.
- To find a good reference for how penalties are encoded, use the **Filter in grid** option to search for "penalty." 
- This returns all rows that contain "penalty," and we can see some common threads—whether they have a formation, a time, or other words, they all contain the pattern "FIRSTINITIAL.LASTNAME, penaltytype." For example, from the top row: T.MORSTEAD, DELAY OF GAME. 
- This data contains the penalty name, which we want, and enough identifiers to make a robust selection.
- However, selecting simply T.MORSTEAD, DELAY OF GAME is too specific. The transform builder suggests only extracting those exact words. We have to build this transformation from scratch.
- Since we want to pull a part of *Description* for this new column, choose the **extract** transformation, and *Description* for the column.
- We want to extract on a pattern, but we can't describe it because it is just some number of non-unique words. So, under **On pattern**, leave the **on** field blank.
- We want the information after the pattern "FIRSTINITIAL.LASTNAME, ". We can find out how Wrangler understands that input by selecting a few instances of that pattern, and looking at its suggested value, which is `` `{url}` `` because it contains a string, a period, and another string.
- In the **starting after** field, enter `` `{url}, ` ``, which is searching for strings after this url-comma-space pattern we've identified. The grid should update, selecting all of the rows from that pattern onward.
- However, we don't want all of that information, so we simply end it at the first comma, entering `` `,` `` in the **ending before** field, and adding our transformation to the recipe. 
- Then, **rename** the new column (called *Description1*) to *PenaltyType*.
- ``extract col: Description after: `{url}, ` before: `,` ``
- `rename col: Description1 to: 'PenaltyType'`

Don't forget to clear the **Filter in grid** field afterwards. Now, we want to add some new information that isn't contained in this dataset. If you haven't already, download the additional dataset ([here](https://github.com/jlove29/trifacta-wrangler/blob/master/additionalData.csv)). Return to the overview of your flow, and add your new dataset into your flow (**Add Datasets** - **Import Datasets**).

Now navigate back to your original dataset, and select the **join** transformation. Select the dataset you've just uploaded (probably called *additionalData*, but if you're unsure, just find the one whose source is "this flow."

