# InaSAFE reporting standards

This document is based on discussions at #2920 and subsequent discussions. 
 Please only modify this document via pull requests so that we can discuss
 and approve changes to our standards before implementing them.

# Status of document

This document is currently in draft form. Some sections of this document are
ready for implementation. The status of these sections is as follows:

| Section | Status |
| ------------------------- | --------------------------- |
| General rules | draft |
| Map title | ready for implementation |
| Map legend title | draft |
| Marginalia | draft |
| Analysis question | ready for implementation |
| General report | draft |
| Detailed report | draft |
| Minimum needs report | draft |
| Action checklist | ready for implementation |
| Notes and assumptions | Examples |
| Analysis details | draft |
| Aggregation report | draft |
| Overall examples | draft |
| Terminology | ready for implementation |
| Other guidelines | ready for implementation |

## How this document is structured

We have broken up this document into sections based on the different reporting
 elements used on map reports, tabular reports, web outputs and so on. Please
 use screenshots and examples liberally so that the norms described here
 are accessible in both a textual and graphical form.

# General rules

* In line with InaSAFE's human interface guidelines, all titles should
  capitalise only the first letter of the first word in labels and titles.
* Titles, body text, table text, table text row heading and table text column
  headings for text content left aligned.
* Numbers and table text column headings for number content right aligned.

# Maps

## Map title

### Description:

The map title appears at the top of each map product and describes the map
 content. Every map should have a title. Using the below table as a reference,
 the title should use the following syntax:

 <**exposure**> <**affected by**> <**hazard**> <**event/hazard**>

 or for generic impact functions:

 <**exposure**> affected

![image](https://cloud.githubusercontent.com/assets/16660099/17202979/c7f2533a-54c6-11e6-8f42-97c324f2ff58.png)

**Exposure** identifies which exposure element is present in the analysis
 area, that is subject to potential losses, is being focused on in this report.
 Examples of exposure elements include: people (population), buildings
 (building and infrastructure), roads, and land cover. **Affected by** is the
 influence or effect from an external factor, i.e. affected by a hazard. We
 use the word 'affected' as the default describer for all hazards. Words such
 as inundated, flooded, impacted should not be used. Please note that for
 Indonesian reports we use the word 'terdampak' even though it is not directly
 translated from 'affected'. **Hazard** is the type of hazard that has
 been chosen for analysis out of the hazards that are supported by InaSAFE.
 **Event/hazard** shows whether the analysis is from a single
 event (**event**) or multiple events (**hazard**).

### Examples: 

**For flood event**:

- People affected by flood event
- Buildings affected by flood event
- Roads affected by flood event
- Land cover affected by flood event

**Indonesian example**: use the word terdampak and don't translate “affected”

- Orang terdampak kejadian banjir
- Bangunan terdampak kejadian banjir
- Jalan terdampak kejadian banjir
- Penutup lahan terdampak kejadian banjir

**For earthquake hazard**:

- People affected by earthquake hazard
- Buildings affected by earthquake hazard
- Roads affected by earthquake hazard
- Land cover affected by earthquake hazard

**Indonesian example**:

- Orang terdampak ancaman gempabumi
- Bangunan terdampak ancaman gempabumi
- Jalan terdampak ancaman gempabumi
- Penutup lahan terdampak ancaman gempabumi

**For generic event / hazard**:

- People affected 
- Buildings affected 
- Roads affected 
- Land cover affected

**Indonesian example**:

- Orang terdampak 
- Bangunan terdampak 
- Jalan terdampak 
- Penutup lahan terdampak

## Map legend title

### Description

The map legend appears at the bottom of each map product and identifies and
 describes the impact layer. Every map should have a legend. Every legend
 should have a title. Using the below table as a reference, the legend titles
 should use the following syntax:

  <**exposure measure**> <**exposure**>

![image](https://cloud.githubusercontent.com/assets/16660099/17202993/efdb8cd6-54c6-11e6-9112-c96ce3652a57.png)

**Exposure measure**, refers to the way the exposure element is measured,
 i.e. length, area or number of. **Exposure**, is as described in the map
 title, i.e. the elements at risk. The label **affected** should not be
 included in the legend title as thresholds for the definition of affected
 vary from impact function to impact function.

### Examples

**For different exposures**: 
- Number of people 
- Number of buildings
- Length of roads
- Area of land cover

**Indonesian example**:
- Perkiraan jumlah penduduk 
- Perkiraan jumlah bangunan
- Perkiraan panjang jalan
- Perkiraan luas penutup lahan

## Marginalia

 _Analysis information:_

- **Impact Function**: <which impact function used>
- **Time**: <time of analysis>
- **Note**: <recommendation to ground truth>
- **Version**: <version of InaSAFE used>
- logos of BNPB, Australian Aid, GFDRR

_Disclaimer_: InaSAFE has been jointly developed by the Indonesian
Government-BNPB, the Australian Government, the World Bank-GFDRR and
independent contributors. These agencies and the individual software
developers of InaSAFE take no responsibility for the correctness of outputs
from InaSAFE or decisions derived as a consequence.

# Reports

## Analysis question

### Description

The analysis question appears at the beginning of each report and identifies
 and describes the purpose of the analysis. Each report should have an analysis
 question. It should add more detail to the existing map title. The question
 should reflect the terminology used in the title. Using the below table as a
 reference, the questions should use the following syntax:

 In the event of a <**hazard**>, <**exposure measure**> <**exposure**>
 might be affected?

 or for generic impact functions:

 In each of the hazard zones <**exposure measure**> <**exposure**> might be
 affected?

![image](https://cloud.githubusercontent.com/assets/16660099/17210381/ceb96bec-54ec-11e6-8fef-3bc59e4756cb.png)

Questions should always have a question mark at the end of the sentence.

### Examples

- In the event of a flood, how many people might be affected?
- In the event of an earthquake, what land cover might be affected?
- In each of the hazard zones how many buildings might be affected?
- In each of the hazard zones what length of road might be affected?

## General report

The general report gives a brief summary in table form of what the estimated
effect of the hazard will be. It should follow this form:
Estimated <**exposure measure**><**exposure**>

![image](https://cloud.githubusercontent.com/assets/16660099/17165600/a45ffea2-53fb-11e6-91c3-761157dd7d8d.png)

## Detailed report

The detailed report gives further detail on the estimated effect of the hazard,
broken down into characteristics, e.g. gender and age for population, type of
building for infrastructure.

![image](https://cloud.githubusercontent.com/assets/16660099/17165692/739dd55e-53fc-11e6-82db-eede1413d6e4.png)

## Minimum needs report

The minimum needs report gives information on the estimated amount of relief
 items to support the affected population. It should be broken up into relief
 items that will be provided once and relief items that are to provided weekly.

![image](https://cloud.githubusercontent.com/assets/16660099/17166008/86065ffc-53fe-11e6-841e-cea3b81803f6.png)

## Action checklist

### Description

Action checklists suitable for each hazard and exposure element should be
 included in this section. Each report should have an action checklist. These
 checklists include questions that should be asked in the event of a hazard
 occurring and should reflect the exposure element analysed and the results of
 the report. The checklist should be sorted in the following order: general
 questions, hazard and exposure specific questions, questions related to
 minimum needs (if applicable) and questions regarding coordinators and
 responders.

### Examples

- How will we reach displaced people?
- What kind of food does the population normally consume?
- What are the critical non-food items required by the affected population?

## Notes and assumptions

### Description

The notes and assumptions section identifies any notes or assumptions specific
 to the hazard, exposure and impact function used in this report. All reports
 should have a notes and assumptions section.

If the term 'affected' is used in the analysis, this section should be used
 to explain the definition of affected and not affected for this particular
 hazard and exposure by outlining the thresholds used in the analysis. This
 section also outlines the assumptions made during the analysis that users
 should take into account when interpreting the report.

If columns or rows are omitted due to zeros the following standard text should
 be included in the report:
_Columns and rows containing only 0 or 'no data' values are excluded from
 the tables._

The notes and assumptions should be sorted in the following order: information
 regarding exposure (e.g. total population or total number of buildings in
 area, evacuation thresholds, damage thresholds), information regarding hazard,
 source of minimum needs or other data (if applicable), information
 regarding the impact function, assumptions made in the analysis (e.g
 information on how 'no data' was handled) and information about what the
 report presents (e.g. what is done with rows or columns of zeros, rounding
 rules).

### Examples

 - Total population in the analysis area: 12,707,000
 - 'No data' values in the impact layer were treated as 0 when counting the
   affected or total population
 - Population rounding is applied to all population values, which may cause
   discrepancies when adding values.

## Analysis details

In the analysis details section details for each layer used in the analysis
 should be provided. This includes the layer name, its source and a link to the
 source if it is available.

**Hazard source**
 Layer name - sourced from x - <insert link here if suitable>

**Exposure source**
 Layer name - sourced from y - <insert link here suitable>

**Aggregation source**
 Layer name - sourced from z - <insert link here suitable>

**Impact Function**
 Impact Function name - published reference for this type of analysis

## Aggregation report

# Overall Examples

**Volcano on people**


**Tsunami on roads**


**Flood on buildings**

# Terminology

**Affected**: An exposure element (e.g. people, roads, buildings, land cover)
 that experiences a hazard (e.g. tsunami, flood, earthquake) and endures
 consequences (e.g. damage, evacuation, displacement, death) due to that
 hazard.

**Displaced**: People who, for different reasons and circumstances because of
 risk or disaster, have to leave their place of residence.
Ref: [UNISDR (2015), Proposed Updated Terminology on Disaster Risk Reduction:
A Technical Review](http://www.preventionweb.net/files/45462_backgoundpaperonterminologyaugust20.pdf)

**Evacuated**: People who, for different reasons or circumstances because of
 risk conditions or disaster, move temporarily to safer places before, during
or after the occurrence of a hazardous event. Evacuation can occur from places
of residence, workplace, schools, hospitals to other places. Evacuation is
usually a planned and organized mobilization of persons, animals and goods, for
eventual return.
Ref: [UNISDR (2015), Proposed Updated Terminology on Disaster Risk Reduction:
A Technical Review](http://www.preventionweb.net/files/45462_backgoundpaperonterminologyaugust20.pdf)

# Other guidelines

[Human Interface Guidelines](https://github.com/inasafe/inasafe/wiki/human-interface-guidelines)

[Design](https://github.com/inasafe/inasafe-graphics/)

[Identity](https://github.com/inasafe/inasafe-graphics/blob/master/inasafe-visual-language-guide-updated.pdf)
