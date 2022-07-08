# `biotools` - Biotope Evaluation Toolset Using `arcpy`

12 health evaluations for urban ecosystem.
Evaluations consist of 6 habitat evaluations and 6 foodchain evaulations.

## Prerequisites
* Install ArcGIS Pro
* Install Java 1.4+ for maxent
* Set `conda` environment to `arcgispro-py3`

## Data Preparation
Biotope Map: .shp, PCS_ITRF2000_TM

Keystone Species Table: .csv, ITRF_2000_UTM_K

Environmental Layers: .asc, ITRF_2000_UTM_K

Commercial Point Table: .csv, GCS_WGS_1984

Surveypoint Map: .shp, PCS_ITRF2000_TM

Foodchain Info Table: .csv

*(All csv files are considered to be encoded using euc-kr.)*

||H1|H2|H3|H4|H5|H6|F1|F2|F3|F4|F5|F6|
|-|-|-|-|-|-|-|-|-|-|-|-|-|
|Biotope Map           |o|o|o|o|o|o|o|o|o|o|o|o|
|Environmental Layers  | | | |o| |o| | | | | |o|
|Keystone Species Table| | | |o| |o| | | | | | |
|Commercial Point Table| | | | |o| | | | | | | |
|Surveypoint Map       | | | | | | |o|o|o|o|o|o|
|Foodchain Info Table  | | | | | | |o|o|o|o|o| |

## Usage

## To Do
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
