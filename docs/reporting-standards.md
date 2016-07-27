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
* We need to use specific “not translated” words for the Indonesian version.
* Capitalise the first letter of the title only.

### Examples: 

**Single scenario flood**:

- People affected by flood event
- Buildings affected by flood event
- Roads affected by flood event
- Land cover affected by flood event

**Indonesian example**: we should use the word terdampak and not translate “affected”

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

The map legend appears at the bottom of each map product and identifies and describes 
the impact layer. 

Using this table as a reference: ![image](https://cloud.githubusercontent.com/assets/16660099/17129361/ca2f9a58-533c-11e6-9b66-a195f20c7bbf.png)

We propose the legend titles should use the following syntax
<**number of**> <**exposure**>

* **Number of**, refers to the way the exposure element is measured, i.e. length, area or 
  number of.
* **Exposure**, is as described in map title, the elements at risk.
* Capitalise the first letter of the title only.
* We do not include the label **affected** in the legend entries as thresholds for the 
  definiton of affected change from impact function to impact function.

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
 
# Reports

* Titles and text left aligned.
* Numbers right aligned.

## Question

The question appears at the beginning of each report and identifies and describes 
the purpose of the analysis. Using this table as a reference:


## Impact summary

## Impact table

## Action list

## Notes and assumptions

## Aggregation report

# Overall Examples

**Volcano on people**


**Tsunami on roads**


**Flood on buildings**

# Terminology

**Displaced**: People who, for different reasons and circumstances because of risk or disaster, have to
leave their place of residence. Ref: [UNISDR (2015), Proposed Updated Terminology on Disaster Risk Reduction: A Technical Review](http://www.preventionweb.net/files/45462_backgoundpaperonterminologyaugust20.pdf)
**Evacuated**: People who, for different reasons or circumstances because of risk conditions or disaster, move temporarily to safer places before, during or after the occurrence of a hazardous event. Evacuation can occur from places of residence, workplace, schools, hospitals to other places. Evacuation is usually a planned and organized mobilization of persons, animals and goods, for
eventual return. Ref: [UNISDR (2015), Proposed Updated Terminology on Disaster Risk Reduction: A Technical Review](http://www.preventionweb.net/files/45462_backgoundpaperonterminologyaugust20.pdf)

# Other Guidelines

[Human Interface Guidelines](https://github.com/inasafe/inasafe/wiki/human-interface-guidelines)

[Design](https://github.com/inasafe/inasafe-graphics/)

[Identity](https://github.com/inasafe/inasafe-graphics/blob/master/inasafe-visual-language-guide-updated.pdf)
