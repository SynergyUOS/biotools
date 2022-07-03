# `biotools` - Biotope Evaluation Toolset Using `arcpy`
도시생태계 건강성 평가 12항목 (서식지 평가 6항목 + 먹이사슬 평가 6항목)

## Prerequisites
* Install ArcGIS Pro
* Install Java 1.4+ for maxent
* Set `conda` environment to `arcgispro-py3`

## Data Preparation
* Biotope Map (도시생태현황도)
* Keystone Species Survey Point Table (핵심종 출현정보)
* Commercial Area Point Table (유동인구 or 발달상권 데이터)
* Species Survey Point Map (생물종 출현정보)
* Species' Foodchain Information Table (먹이사슬 관계정보)

## Usage

## To Do
- [ ] Habitat (서식지)
  - [x] 1. Habitat Size (서식지 규모)
  - [ ] 2. Layered Structure (층위구조)
  - [x] 3. Patch Isolation (패치고립도)
  - [x] 4. Least Cost Distribution (최소비용 평균)
  - [x] 5. Occurrence of Piece of Land (자투리땅 발생 가능성)
  - [x] 6. Availability of Piece of Land (자투리땅 활용 가능성)
- [ ] Foodchain (먹이사슬)
  - [x] 7. Number of Food Resources (먹이자원의 개체 수)
  - [x] 8. Diversity Index (종다양성)
  - [x] 9. Combinable Producers and Consumers (조합가능한 생산자와 소비자)
  - [x] 10. Connection Strength (연결 강도)
  - [x] 11. Similar Functional Species (유사기능종)
  - [ ] 12. Inhabitation of Food Resources (먹이자원 서식확률)
- [ ] Documentation
- [ ] Flexible interface
