# `biotools` - Biotope Evaluation Toolset Using `arcpy`

This tool evaluate health of urban ecosystem.
It consists of 6 tools for habitat and 6 tools for foodchain.

Each tool evaluates the following:
* Habitat Size
* Layered Structure
* Patch Isolation
* Least Cost Distribution
* Occurrence of Piece of Land
* Availability of Piece of Land
* The Number of Food Resources
* Shannon Diversity Index
* Combinable Producers and Consumers
* Connection Strength
* Similar Functional Species
* Inhabitation of Food Resources

# Prerequisites
* Install ArcGIS Pro
* Install Java 1.4+ for maxent
* Set `conda` environment to `arcgispro-py3`

# Data Required
## Specification
||File Format|Coordnate System|Fields (bracket means substitutable)|
|-|-|-|-|
|Biotope Map           |Shapefile|defined|FID, 비오톱|
|Environmental Layers  |Esri ASCII raster|ITRF_2000_UTM_K|-|
|Keystone Species Table|CSV|ITRF_2000_UTM_K|[Name], [Longitude], [Latitude]|
|Commercial Point Table|CSV|GCS_WGS_1984|위도, 경도|
|Surveypoint Map       |Shapefile|defined| |
|Foodchain Info Table  |CSV|-|S_Name, Owls_foods, D_Level, Alternatives_S|

*(All csv files are considered to be encoded using euc-kr.)*

## Where to Use
||H1|H2|H3|H4|H5|H6|F1|F2|F3|F4|F5|F6|
|-|-|-|-|-|-|-|-|-|-|-|-|-|
|Biotope Map           |o|o|o|o|o|o|o|o|o|o|o|o|
|Environmental Layers  | | | |o| |o| | | | | |o|
|Keystone Species Table| | | |o| |o| | | | | | |
|Commercial Point Table| | | | |o| | | | | | | |
|Surveypoint Map       | | | | | | |o|o|o|o|o|o|
|Foodchain Info Table  | | | | | | |o|o|o|o|o| |

# Usage

# To Do
- [ ] Habitat
  - [ ] H1. Habitat Size
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] H2. Layered Structure
    - [ ] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] H3. Patch Isolation
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] H4. Least Cost Distribution
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] H5. Occurrence of Piece of Land
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] H6. Availability of Piece of Land
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
- [ ] Foodchain
  - [ ] F1. Number of Food Resources
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] F2. Diversity Index
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] F3. Combinable Producers and Consumers
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] F4. Connection Strength
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] F5. Similar Functional Species
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] F6. Inhabitation of Food Resources
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
