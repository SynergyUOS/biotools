# biotools
*Biotope Evaluation Toolset Using Arcpy and Maxent*

This toolset evaluates health of urban ecosystem.
It consists of 6 tools for habitat and 6 tools for foodchain.

Each tool evaluates the following:
|What to evaluate|ID|Description|
|-|-|-|
|Habitat Size                      |H1|[detailed descriptions here]|
|Layered Structure                 |H2||
|Patch Isolation                   |H3||
|Least Cost Distribution           |H4||
|Occurrence of Piece of Land       |H5||
|Availability of Piece of Land     |H6||
|The Number of Food Resources      |F1||
|Shannon Diversity Index           |F2||
|Combinable Producers and Consumers|F3||
|Connection Strength               |F4||
|Similar Functional Species        |F5||
|Inhabitation of Food Resources    |F6||


## Getting Started

### Prerequisites
* ArcGIS Pro 3.0+. (maybe 2.8 is also available...)
* Java 1.4+. (for maxent)
  ```console
  $ java -version
  java version "1.8.0_331"
  ```

### Installation
1. Clone *arcgispro-py3* conda environment.
   ```console
   $ conda create --name cloned-env --clone arcgispro-py3
   ```
2. Place biotools package folder in
   * path/to/cloned-env/Lib/
   * or the same folder as your script.

### Run
1. Write a script with biotools. ([how?](#usage))
2. Activate the cloned conda environment.
   ```console
   $ conda activate cloned-env
   (cloned-env) $
   ```
3. Run your script.
   ```console
   (cloned-env) $ python path/to/your_script.py
   ```


## Input Required

### Specification
||File Format|Coordnate System|Fields|
|-|-|-|-|
|Biotope Map           |Shapefile|Anything but nothing|비오톱, [...]|
|Environmental Layers  |Esri ASCII raster|ITRF_2000_UTM_K|-|
|Keystone Species Table|CSV|ITRF_2000_UTM_K|{Name}, {Longitude}, {Latitude}|
|Commercial Point Table|CSV|GCS_WGS_1984|위도, 경도, [...]|
|Surveypoint Map       |Shapefile|Anything but nothing|국명, 개체수, [...]|
|Foodchain Info Table  |CSV|-|S_Name, Owls_foods, D_Level, Alternatives_S, [...]|

*(All csv files are considered to be encoded using euc-kr.)*

*(Braces can be replaced by another name, if it sticks to same order.)*

*(Values of 비오톱 field must be one of the values in MEDIUM_CATEGORY_CODE field of [this file](biotools/res/biotope_codes.csv).)*

### Where to Use
||H1|H2|H3|H4|H5|H6|F1|F2|F3|F4|F5|F6|
|-|-|-|-|-|-|-|-|-|-|-|-|-|
|Biotope Map           |✔|✔|✔|✔|✔|✔|✔|✔|✔|✔|✔|✔|
|Environmental Layers  | | | |✔| |✔| | | | | |✔|
|Keystone Species Table| | | |✔| |✔| | | | | | |
|Commercial Point Table| | | | |✔| | | | | | | |
|Surveypoint Map       | | | | | | |✔|✔|✔|✔|✔|✔|
|Foodchain Info Table  | | | | | | |✔|✔|✔|✔|✔| |


## Usage

### Basic Use
```python
from biotools import Biotools

bt = Biotools(
    "path/to/BiotopeMap.shp",  # required for all evaluations
    "path/to/result/",  # results are saved in this folder
)

bt.run_h1()  # will create result shapefile in path/to/result/result_{id}/
```

### With Additional Inputs
```python
from biotools import Biotools

bt = Biotools(
    "path/to/BiotopeMap.shp",
    "path/to/result/",
    environmentallayer_directory="path/to/envlayer/",
    surveypoint_shp="path/to/Surveypoint.shp",
    foodchain_info_csv="path/to/foodchain_info.csv"
)

bt.run_f6()
```

### With Arguments
```python
from biotools import Biotools

bt = Biotools(
    "path/to/BiotopeMap.shp",
    "path/to/result/",
    environmentallayer_directory="path/to/envlayer/",
    keystone_species_csv="path/to/keystone_species.csv"
)

bt.run_h6(threshold=0.7, cellsize=3)  # parameters vary in tools
```

### Full Evaluation
```python
from biotools import Biotools

bt = Biotools(
    "path/to/BiotopeMap.shp",
    "path/to/result/",
    environmentallayer_directory="path/to/envlayer/",
    keystone_species_csv="path/to/keystone_species.csv"
    commercialpoint_csv="path/to/commercialpoint.csv"
    surveypoint_shp="path/to/Surveypoint.shp",
    foodchain_info_csv="path/to/foodchain_info.csv"
)

bt.run_h1()
bt.run_h2()
...
bt.run_f6()

bt.merge()  # will create merged result shapefile in path/to/result/result_full/
```

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
