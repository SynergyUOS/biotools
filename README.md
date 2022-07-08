# `biotools` - Biotope Evaluation Toolset Using `arcpy`
도시생태계 건강성 평가 12항목 (서식지 평가 6항목 + 먹이사슬 평가 6항목)

## Prerequisites
* Install ArcGIS Pro
* Install Java 1.4+ for maxent
* Set `conda` environment to `arcgispro-py3`

## Data Preparation
Biotope Map (도시생태현황도):
* .shp
* PCS_ITRF2000_TM

Keystone Species Table (핵심종 출현정보):
* .csv (encoding: euc-kr)
* ITRF_2000_UTM_K

Environmental Layers (환경변수지도):
* .asc
* ITRF_2000_UTM_K

Commercial Point Table (유동인구 or 발달상권 데이터):
* .csv
* GCS_WGS_1984

Surveypoint Map (생물종 출현정보):
* .csv
* PCS_ITRF2000_TM

Foodchain Info Table (먹이사슬 관계정보):
* .csv

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
- [ ] Habitat (서식지)
  - [ ] 1. Habitat Size (서식지 규모)
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] 2. Layered Structure (층위구조)
    - [ ] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] 3. Patch Isolation (패치고립도)
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] 4. Least Cost Distribution (최소비용 평균)
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] 5. Occurrence of Piece of Land (자투리땅 발생 가능성)
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] 6. Availability of Piece of Land (자투리땅 활용 가능성)
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
- [ ] Foodchain (먹이사슬)
  - [ ] 7. Number of Food Resources (먹이자원의 개체 수)
    - [x] Implementation
    - [x] Encapsulation
    - [ ] Documetation
  - [ ] 8. Diversity Index (종다양성)
    - [x] Implementation
    - [ ] Encapsulation
    - [ ] Documetation
  - [ ] 9. Combinable Producers and Consumers (조합가능한 생산자와 소비자)
    - [x] Implementation
    - [ ] Encapsulation
    - [ ] Documetation
  - [ ] 10. Connection Strength (연결 강도)
    - [x] Implementation
    - [ ] Encapsulation
    - [ ] Documetation
  - [ ] 11. Similar Functional Species (유사기능종)
    - [x] Implementation
    - [ ] Encapsulation
    - [ ] Documetation
  - [ ] 12. Inhabitation of Food Resources (먹이자원 서식확률)
    - [x] Implementation
    - [ ] Encapsulation
    - [ ] Documetation
