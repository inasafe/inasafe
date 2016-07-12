# InaSAFE reporting standards

This document is based on discussions at #2920 and subsequent discussions. 
Please only modify this document via pull requests so that we can discuss 
and approve changes to our standards before implementing them.

## How this document is structured

We have broken up this document into sections based on the different reporting
elements used on map reports, tabular reports, web outputs and so on. Please
use screenshots and examples liberally so that the norms described here 
are accessible in both a textual and graphical form.


# Maps

## Map title

### Description:

The map title appears at the top of each map product and describes the map content. Using this table as a reference:
![image](https://cloud.githubusercontent.com/assets/13621886/16513431/eab2319e-3f8e-11e6-9249-eb265f95ac43.png)

We propose the title should use the following syntax
<**exposure**> <**affected by/in**> <**type of hazard**> <**event/hazard**>

* In the table, we see that **exposure** contains people (population), buildings (building 
  and infrastructure), roads, and land cover. It is people, property, systems, or other elements 
  present in hazard zones that are thereby subject to potential losses (UNISDR's terminology).
* **Affected by/in**, is the influence or effect from external factor, i.e. affected by a disaster.
* **The type of hazard**, it is the type of hazards that supports by InaSAFE to analyse with.
* **Event or hazard**, this is a different scenario, in a single scenario we use **event** and 
  when it is multiple scenarios we use **hazard**.
* We need to use specific “not translated” words for the Indonesian version
* Capitalise the first letter of the title only

### Examples: 

**For examples**: -single scenario flood-
- People affected by flood event
- Buildings affected by flood event
- Roads affected by flood event
- Land cover affected by flood event

**Indonesian example**: we should use the word terdampak and not translate “affected”

- Orang terdampak kejadian banjir
- Bangunan terdampak kejadian banjir
- Jalan terdampak kejadian banjir
- Penutup lahan terdampak kejadian banjir

**Examples**: -for earthquake hazard-

- People affected by earthquake hazard
- Buildings affected by earthquake hazard
- Roads affected by earthquake hazard
- Land cover affected by earthquake hazard

**Indonesian example**:

- Orang terdampak ancaman gempabumi
- Bangunan terdampak ancaman gempabumi
- Jalan terdampak ancaman gempabumi
- Penutup lahan terdampak ancaman gempabumi

**Examples**: -for generic event / hazard-

- People affected 
- Buildings affected 
- Roads affected 
- Land cover affected

 
**Indonesian example**:

- Orang terdampak 
- Bangunan terdampak 
- Jalan terdampak 
- Penutup lahan terdampak

## Map image/content

* The only layers that should be visible are the context data (i.e. administrative boundaries) and the impact layer.
* If the user wants to show the hazard data as well as the impact data, they can turn it on themselves.




### Legend

![image](https://cloud.githubusercontent.com/assets/16660099/16068549/0b08b9a4-330a-11e6-9c74-3e0b772253c7.png)

**Legend title**
Standard options for generic:

- Estimated people affected
- Estimated buildings affected
- Estimated roads affected
- Estimated land cover affected

_Do not add “by each hazard zone” to the end of the title. (Alternatively, if this is done it should be consistent across all maps.)_ 

**Legend content**
All layers shown on the map image should be shown in the legend.

_All legend entries should take the following form:_
Words in the legend directly next to the legend colour, followed by numbers in brackets e.g. like this:
![image](https://cloud.githubusercontent.com/assets/16660099/16068707/6a089608-330b-11e6-93e3-7c0508d4f0ce.png)

_Rounding_

- Population - whole numbers only
- Flood/tsunami depths - to 1 decimal place
- Land Cover - to 1 decimal place
- Roads - to 0 decimal place

Legends with more categories than those listed above should continue according to rainbow increments (e.g. Very high hazard zone should be a dark red, and if a dry zone is included in a low-high scale, the dry zone should be green and the low hazard zone should be yellow)

### Hazard specific legend content:

**Earthquake**
_Low_: MMI < V
_Medium_: MMI = VI - VII
_High_: MMI = VII - IX
Reference: International handbook of Earthquake engineering
_others please correct this if this is wrong - I just found it in the above reference material - I don't like that VII overlaps in two categories_

**Flood**
_Low_: < 1 m
_Medium_: 1 - 3 m
_High_: > 3 m
Reference: Perka 2

**Binary description flood vector hazard classes**
_Dry_: 0 - 1 m
_Wet_: > = 1 m
Reference: .qgis2\python\plugins\inasafe\safe\definitions.py

**Tsunami**
_People_: 0.7m
_Buildings, roads, landcover_:
_Low_ < 1m
_Medium_ 1 - 3 m
_High_  3 - 8m
_Very High_ >8m 
Reference: Papadoupulos and Imamura, 2001
_@eametz and @RikkiWeber - I have updated tsunami classed based on InaSAFE tsunami impact functions released in v3.4. These classes are documented and referenced in .qgis2\python\plugins\inasafe\safe\definitions.py

**Binary description tsunami raster hazard classes**
_Dry_: 0 - 1 m
_Wet_: > = 1 m
Reference: .qgis2\python\plugins\inasafe\safe\definitions.py

**Volcanic Ash**
_Low
Medium
High_
_ @adelebearcrozier and others please update these classes_

**Volcano vector hazard classes**
_Low_: 5 - 10
_Medium_: 3 - 5
_High_: 0 - 3
Reference: .qgis2\python\plugins\inasafe\safe\definitions.py

**Generic vector hazard classes**
_Low_: 5 - 10
_Medium_: 3 - 5
_High_: 0 - 3
Reference: .qgis2\python\plugins\inasafe\safe\definitions.py

**Generic raster hazard classes**
_Low_: 1
_Medium_: 2
_High_: 3
Reference: .qgis2\python\plugins\inasafe\safe\definitions.py

**Record of votes for Legend section**

Vote | Name
------------------- | -------------------------

### Marginalia

_Analysis information:_

- **Impact Function:** which impact function used
- **Time**: time of analysis
- **Note:** recommendation to ground truth
- **Version:** version of InaSAFE used
- logos of BNPB, Australian Aid, GFDRR

_Disclaimer_: InaSAFE has been jointly developed by the Indonesian Government-BNPB, the Australian Government, the World Bank-GFDRR and independent contributors. These agencies and the individual software developers of InaSAFE take no responsibility for the correctness of outputs from InaSAFE or decisions derived as a consequence.
**General:** Capitalise first letter only in marginalia titles

**Record of votes for Marginalia section**

Vote | Name
------------------- | -------------------------

## Reports

### General report
**Standard report order:**
- Analysis results
- Action checklist
- Notes and assumptions
- Analysis details
- Aggregation reports

**Alignment**

Left | Right
------------------------------------------------------------ | ------------------------------------------------------------
Body text | Numbers
Table text | Text column headings for number content
Text row headings |  
Text column headings for text content |  

**Headings**
Capitalise first letter only of headings.
All columns should have headings.

**Standard headings:**
Analysis results
Action checklist
Notes and assumptions
Analysis details

**Exposure specific headings:** 
**Population:**
Evacuated population minimum needs
_Aggregate_
Detailed gender report (affected people)
Detailed age report (affected people)
Detailed minimum needs report (affected people)>

**Buildings:**
Building type affected
Closed buildings

**Roads**
Breakdown by road type
Closed roads

**Landcover:**
Analysis results by aggregate area

**Units and delimiters**
Column headings should include units.
All numbers should include delimiters (in the format _x_,_xxx_,_xxx_._xx_).

**Rounding**

- Numbers are always rounded up as it is better to overestimate than underestimate impact
-  Number of people are rounded to 1000 for values > 100 000
- Number of people are rounded to 100 for values < 100 000
- Number of people are rounded to 10 for values < 1000
- Flood/tsunami depths are rounded to 1 decimal place
- Land cover are rounded to 1 decimal place
- Roads are rounded to 0 decimal place

**Aggregation reports**
These should always come _after_ all other information.

**Action lists**
Should relate to the exposure, hazard specific.

**Notes**
- Should relate to the hazard (e.g. what hazard classes were used)
- Should include something specific about exposure i.e. what defines a closed building
- Explicitly name the parameters set (e.g. “Roads are flooded when flood levels exceed 1.0m”)
- Key words used in the report (e.g. affected, inundated, needs evacuation, flooded) should be automatically included in a glossary in the notes
- Include this standard text if columns or rows are omitted due to zeros _Columns and rows containing only 0 or 'no data' values are excluded from the tables._
- Include above rounding text prefixed by: "Numbers in this report are rounded according to the following conditions:"


**Record of votes for General report section**

Vote | Name
------------------- | -------------------------

### Analysis details

**Hazard source**
Layer name - sourced from x - <insert link here if suitable>
**Exposure source**
Layer name - sourced from y - <insert link here suitable>
**Aggregation source**
Layer name - sourced from z - <insert link here suitable>
**Impact Function**
Impact Function name - published reference for this type of analysis

### Terminology

I propose that these terminology have the following definitions:
**Impacted** : Any person, building, road or land cover that is actively damaged by a hazard - i.e. people that are injured or killed or that need to be evacuated
**Affected** : Any person, building, road or land cover that may experience a hazard but not be impacted by it - i.e. people that feel/experience a hazard but are not injured or killed and do not need to be evacuated
**Inundated vs flooded** : _There are two ways we could do this - inundated referring to tsunami, and flooded referring to flood; or, picking one or the other for both flood and tsunami. Inundated to me suggests greater damage has been incurred, as it would be in a tsunami compared to a flood with the same height of water, so I propose we choose inundated for tsunami and flooded for flood._
**Shaken** : To experience an earthquake, but not necessarily be impacted by it.
**People/population**: _I propose we use the word people as it is a simpler word, but I think which word we pick doesn't matter so much, as long as it is consistent throughout all reports._ 
**Wet**: Water above ground height.
**Dry**: No water above ground height.
Killed
Open
Closed

**Preferred terminology: - bolded text is the predominant opinion**
**Impact on** or ~impact to~
**People** vs ~population~

Examples of good reports:

- Flood raster
- Tsunami
- EQ raster

**Record of votes for Analysis details and Terminology sections**

Vote | Name
------------------- | -------------------------

## Other Guidelines

[Human Interface Guidelines](https://github.com/inasafe/inasafe/wiki/human-interface-guidelines)

[Design](https://github.com/inasafe/inasafe-graphics/)

[Identity](https://github.com/inasafe/inasafe-graphics/blob/master/inasafe-visual-language-guide-updated.pdf)

# General Recommendations

- There should be a clearer link between the map and report even though they are standalone pieces.
- The maps should have more explicit titles.
- Colour palettes should use page 9 of the [Visual Language Guide ](http://inasafe.org/for-documentation-writers-and-designers/design-and-media/)as far as possible. If we need more colours it should be done in a systematic way using considerations of contrast, ability to be distinguished for folks with visual issues (e.g. colour blindness) and so on. New colour palettes should be added to the above mentioned guide.

link to google doc: https://docs.google.com/document/d/1rhipAU4mdykbKQ4Qx4I5XuUwSSd33IY7Iw99tvOQsMo/edit?usp=sharing


